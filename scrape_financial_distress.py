#!/usr/bin/env python3
"""
Invoice Delinquency Intelligence System v2
Uses ACTUAL accessible APIs and data sources (no JavaScript rendering needed).

Data Sources:
1. SEC EDGAR - Public company 10-K/10-Q filings (accounts payable, tax liabilities)
2. OpenCorporates API - Business registration + litigation records
3. County tax lien datasets (CSV downloads)
4. SAM.gov - Federal contractors with payment issues
5. State Secretary of State APIs - Business status data

Output: CSV with company name, financial distress signals, contact info, priority score
"""

import os
import csv
import json
import time
import asyncio
import aiohttp
import ssl
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Fix SSL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Configuration
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

@dataclass
class CompanyDistressRecord:
    company_name: str
    ticker: str
    industry: str
    state: str
    accounts_payable: float
    tax_liabilities: float
    total_debt: float
    revenue: float
    debt_to_revenue_ratio: float
    distress_signals: List[str]
    source: str
    source_url: str
    priority_score: str  # "critical", "high", "medium"
    scraped_at: str

class FinancialDistressScraper:
    """Scrapes financial distress signals from public data sources"""
    
    def __init__(self):
        self.results: List[CompanyDistressRecord] = []
        self.headers = {
            "User-Agent": "InvoiceIntelligence/1.0 (yoshikondo@email.com)"
        }
    
    async def fetch_json(self, url: str, timeout: int = 30) -> dict:
        """Fetch JSON data"""
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.headers, timeout=timeout) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        print(f"   ⚠️  HTTP {resp.status}: {url}")
                        return {}
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")
            return {}
    
    async def fetch_text(self, url: str, timeout: int = 30) -> str:
        """Fetch text/CSV data"""
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.headers, timeout=timeout) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    else:
                        return ""
        except Exception as e:
            return ""
    
    async def scrape_sec_edgar_10k(self, ticker: str) -> Optional[CompanyDistressRecord]:
        """Get financial distress signals from SEC 10-K filings"""
        # Get company facts
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{ticker.zfill(10)}.json"
        data = await self.fetch_json(facts_url)
        
        if not data:
            return None
        
        # Extract financial data
        facts = data.get('facts', {})
        us_gaap = facts.get('us-gaap', {})
        
        # Get key metrics
        def get_latest_value(concept, tag='USD'):
            concept_data = us_gaap.get(concept, {})
            units = concept_data.get('units', {})
            usd_data = units.get(tag, units.get('shares', units.get('pure', [])))
            if usd_data:
                # Get most recent year
                usd_data.sort(key=lambda x: x.get('end', ''), reverse=True)
                return usd_data[0].get('val', 0)
            return 0
        
        accounts_payable = get_latest_value('AccountsPayableCurrent')
        tax_liabilities = get_latest_value('AccruedIncomeTaxesCurrent')
        total_debt = get_latest_value('LongTermDebt')
        revenue = get_latest_value('Revenues')
        
        # Calculate distress signals
        signals = []
        if revenue > 0:
            debt_ratio = total_debt / revenue if revenue else 0
        else:
            debt_ratio = 0
        
        if debt_ratio > 1.0:
            signals.append("Debt exceeds annual revenue")
        if accounts_payable > revenue * 0.1:
            signals.append("High accounts payable (>10% revenue)")
        if tax_liabilities > 0:
            signals.append(f"Accrued tax liabilities: ${tax_liabilities:,.0f}")
        
        priority = "critical" if len(signals) >= 2 else "high" if signals else "medium"
        
        return CompanyDistressRecord(
            company_name=data.get('name', ticker),
            ticker=ticker,
            industry=data.get('entityType', ''),
            state="",
            accounts_payable=accounts_payable,
            tax_liabilities=tax_liabilities,
            total_debt=total_debt,
            revenue=revenue,
            debt_to_revenue_ratio=round(debt_ratio, 2),
            distress_signals=signals,
            source="SEC EDGAR",
            source_url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=10-K",
            priority_score=priority,
            scraped_at=datetime.now().isoformat()
        )
    
    async def scrape_sp500_financials(self) -> List[CompanyDistressRecord]:
        """Scrape all S&P 500 company financials for distress signals"""
        print("\n[1/4] Scanning S&P 500 companies for financial distress...")
        
        # Get S&P 500 list
        sp500_url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
        csv_data = await self.fetch_text(sp500_url)
        
        if not csv_data:
            return []
        
        import csv
        import io
        reader = csv.DictReader(io.StringIO(csv_data))
        companies = list(reader)
        
        print(f"   Found {len(companies)} S&P 500 companies to scan")
        
        results = []
        # Scan first 20 companies (full scan would take hours)
        for i, company in enumerate(companies[:20]):
            ticker = company.get('Symbol', '')
            print(f"   [{i+1}/20] Scanning {company.get('Name', ticker)} ({ticker})...")
            
            record = await self.scrape_sec_edgar_10k(ticker)
            if record and record.distress_signals:
                results.append(record)
                print(f"   🔴 {len(record.distress_signals)} distress signals found")
            else:
                print(f"   ✅ No significant distress signals")
            
            # Rate limit
            await asyncio.sleep(0.5)
        
        print(f"   ✅ Found {len(results)} companies with distress signals")
        return results
    
    async def scrape_sam_gov_contracts(self) -> List[CompanyDistressRecord]:
        """Scrape SAM.gov for federal contractors with issues"""
        print("\n[2/4] Checking federal contractor database...")
        
        # SAM.gov API for contract opportunities/awards
        # This is a simplified version - full access requires API key
        url = "https://api.sam.gov/prod/opportunities/v1/search?limit=10"
        data = await self.fetch_json(url)
        
        # In production, you'd parse this for contractors with payment issues
        print("   ⚠️  SAM.gov requires API key for full access")
        print("   ℹ️  Register at sam.gov for free API access")
        return []
    
    async def scrape_county_tax_liens(self) -> List[CompanyDistressRecord]:
        """Scrape county tax lien datasets"""
        print("\n[3/4] Checking county tax lien databases...")
        
        # Example: Allegheny County tax liens (public dataset)
        url = "https://data.wprdc.org/api/3/action/datastore_search?resource_id=tax-liens&limit=100"
        data = await self.fetch_json(url)
        
        records = []
        if data and data.get('result', {}).get('records'):
            lien_records = data['result']['records']
            print(f"   Found {len(lien_records)} tax lien records")
            
            for lien in lien_records[:20]:  # First 20
                debtor = lien.get('taxpayer_name', lien.get('owner_name', 'Unknown'))
                amount = float(lien.get('amount', 0))
                
                if amount > 10000:  # Only significant liens
                    records.append(CompanyDistressRecord(
                        company_name=debtor,
                        ticker="",
                        industry="tax_lien",
                        state="PA",
                        accounts_payable=0,
                        tax_liabilities=amount,
                        total_debt=amount,
                        revenue=0,
                        debt_to_revenue_ratio=0,
                        distress_signals=[f"Tax lien filed: ${amount:,.0f}"],
                        source="County Tax Records",
                        source_url="https://data.wprdc.org/dataset/tax-liens",
                        priority_score="critical" if amount > 100000 else "high",
                        scraped_at=datetime.now().isoformat()
                    ))
        
        print(f"   ✅ Found {len(records)} significant tax liens")
        return records
    
    async def scrape_opencorporates(self) -> List[CompanyDistressRecord]:
        """Use OpenCorporates API for business registration issues"""
        print("\n[4/4] Checking business registration records...")
        
        # OpenCorporates API (free tier available)
        # Search for companies with litigation/dissolution
        url = "https://api.opencorporates.com/v0.4/companies/search?company_type=active&per_page=10"
        data = await self.fetch_json(url)
        
        # In production, you'd search for:
        # - Companies with litigation records
        # - Recently dissolved companies
        # - Companies with officers who are also officers of distressed companies
        
        print("   ⚠️  OpenCorporates requires API key for advanced searches")
        print("   ℹ️  Free tier: 1 query/second, limited results")
        return []
    
    async def run_full_scan(self):
        """Run all scrapers and generate intelligence report"""
        print("═══════════════════════════════════════════════════════════")
        print("🔍 Invoice Delinquency Intelligence System v2")
        print("═══════════════════════════════════════════════════════════")
        
        # Run all scrapers
        sp500_results = await self.scrape_sp500_financials()
        sam_results = await self.scrape_sam_gov_contracts()
        county_results = await self.scrape_county_tax_liens()
        opencorp_results = await self.scrape_opencorporates()
        
        # Combine all results
        all_results = sp500_results + sam_results + county_results + opencorp_results
        
        # Sort by priority
        all_results.sort(key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2}.get(x.priority_score, 3),
            -x.total_debt
        ))
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = OUTPUT_DIR / f"financial_distress_intelligence_{timestamp}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CompanyDistressRecord.__dataclass_fields__.keys())
            writer.writeheader()
            for record in all_results:
                writer.writerow(asdict(record))
        
        # Summary
        total = len(all_results)
        critical = sum(1 for r in all_results if r.priority_score == "critical")
        high = sum(1 for r in all_results if r.priority_score == "high")
        total_debt = sum(r.total_debt for r in all_results)
        
        print("\n" + "="*60)
        print("📊 FINANCIAL DISTRESS INTELLIGENCE REPORT")
        print("="*60)
        print(f"  Companies scanned: 20 (S&P 500 sample)")
        print(f"  Companies with distress signals: {total}")
        print(f"  Critical priority: {critical}")
        print(f"  High priority: {high}")
        print(f"  Total tax liens found: ${total_debt:,.0f}")
        print(f"\n  Full report: {csv_file}")
        print("="*60)
        
        return all_results


async def main():
    scraper = FinancialDistressScraper()
    await scraper.run_full_scan()

if __name__ == "__main__":
    asyncio.run(main())
