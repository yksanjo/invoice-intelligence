# State Delinquent Taxpayer Database - 2026

## All Public State Delinquency List URLs

| State | URL | Data Type | Update Frequency | Format |
|-------|-----|-----------|------------------|--------|
| **California** | https://cdtfa.ca.gov/taxes-and-fees/top500.htm | Top 500 Sales Tax (> $100K) | Monthly | HTML Table |
| **California (FTB)** | https://www.ftb.ca.gov/about-ftb/newsroom/tax-news/notice-of-public-disclosure-of-tax-delinquency.html | Top 500 Income Tax | Quarterly | HTML/PDF |
| **New York** | https://www.tax.ny.gov/enforcement/nys-delinquent-taxpayers.htm | Top 100 Businesses + Top 100 Individuals | Quarterly | PDF |
| **South Carolina** | https://dor.sc.gov/delinquent-taxpayers | Top Delinquent Businesses + Individuals | Quarterly | HTML Table |
| **Minnesota** | https://www.revenue.state.mn.us/businesses-and-organizations/businesses-prohibited-purchasing-state-contracts | Prohibited from State Contracts | Monthly | HTML |
| **Florida** | https://floridarevenue.com/taxes/delinquent/Pages/default.aspx | Tax Warrants | Monthly | HTML |
| **Texas** | https://comptroller.texas.gov/taxes/delinquent/ | Delinquent Tax List | Quarterly | HTML/PDF |
| **Illinois** | https://www2.illinois.gov/rev/Pages/Tax-Delinquency-Lists.aspx | Delinquent Taxpayers | Quarterly | HTML |
| **Georgia** | https://dor.georgia.gov/delinquent-taxpayers | Top Delinquent Taxpayers | Quarterly | HTML |
| **Pennsylvania** | https://revenue.pa.gov/Pages/default.aspx | Tax Delinquency List | Quarterly | PDF |
| **Ohio** | https://tax.ohio.gov/Home/Delinquency | Delinquent Taxpayers | Quarterly | HTML |
| **Michigan** | https://www.michigan.gov/treasury/0,9360,7-125-17306_17429---,00.html | Delinquent Tax List | Quarterly | HTML/PDF |
| **New Jersey** | https://www.state.nj.us/treasury/taxation/delinquent.shtml | Delinquent Taxpayers | Quarterly | HTML |
| **Virginia** | https://www.tax.virginia.gov/delinquent-taxpayers | Top Delinquent Taxpayers | Quarterly | HTML |
| **Washington** | https://dor.wa.gov/taxes-rates/other-resources/delinquent-taxpayers | Delinquent Taxpayers | Quarterly | HTML |
| **Massachusetts** | https://www.mass.gov/orgs/delinquent-tax-bureau | Tax Liens | Monthly | HTML |
| **Arizona** | https://azdor.gov/taxes/debt-collection/delinquent-taxpayers | Delinquent Tax List | Quarterly | HTML |
| **Tennessee** | https://www.tn.gov/revenue.html | Tax Liens | Quarterly | HTML |
| **Indiana** | https://www.in.gov/dor/ | Tax Warrants | Quarterly | HTML |
| **Missouri** | https://dor.mo.gov/ | Delinquent Taxpayers | Quarterly | HTML |

## Additional Sources (County/City Level)

| Jurisdiction | URL | Data Type | Format |
|--------------|-----|-----------|--------|
| **Los Angeles** | https://finance.lacity.gov/top-delinquent-taxpayers | Top Tax Delinquencies > $100K | HTML |
| **Douglas County, CO** | https://douglastax.org/delinquent-tax-list | Property Tax Defaults | PDF |
| **Montgomery County, MD** | https://data.montgomerycountymd.gov/api/views/99ya-kjjr/rows.csv | Tax Delinquency CSV | CSV |
| **City of Olean, NY** | https://cityofolean.gov/departments/public-works/dpw-delinquent-water-sewer-reports/ | Utility Delinquencies | PDF |
| **Chicago** | https://www.chicago.gov/city/en/depts/other/provdrs/ccco/svcs/real_estate_and_taxservices.html | Tax Delinquencies | HTML |
| **Allegheny County, PA** | https://data.wprdc.org/dataset/tax-liens | Tax Liens Dataset | API/CSV |

## Federal Sources

| Source | URL | Data Type | Format | Access |
|--------|-----|-----------|--------|--------|
| **IRS Lien Database** | https://www.irs.gov/privacy-disclosure/automated-lien-system-database-listing | Federal Tax Liens | Pipe-delimited | FOIA Request (Free) |
| **SAM.gov** | https://sam.gov | Federal Contractors | API | Free API Key |
| **SEC EDGAR** | https://www.sec.gov/cgi-bin/browse-edgar | Public Company 10-K/10-Q Filings | JSON/XML | Free |

## Scraping Priority Order

### Tier 1 (Highest Value, Easiest Access)
1. **California CDTFA Top 500** - HTML table, $100K+ debts
2. **New York Top 100 Businesses** - PDF, downloadable
3. **South Carolina Delinquent** - HTML table, full details
4. **Florida Tax Warrants** - Searchable database

### Tier 2 (High Value, Moderate Access)
5. **Texas Delinquent List** - HTML/PDF, quarterly updates
6. **Illinois Tax Lists** - HTML, quarterly
7. **Georgia Delinquent** - HTML, quarterly
8. **Pennsylvania** - PDF, quarterly

### Tier 3 (Medium Value, Requires Effort)
9. **Minnesota** - HTML, list of prohibited contractors
10. **Ohio** - HTML, quarterly
11. **Michigan** - HTML/PDF, quarterly
12. **New Jersey** - HTML, quarterly

### Tier 4 (County/City - Niche but Valuable)
13. **Los Angeles Top Delinquent** - HTML, $100K+
14. **Montgomery County CSV** - Direct CSV download
15. **Allegheny County API** - Programmatic access
16. **Douglas County PDF** - Property tax defaults

## Notes

- **25 states** publish delinquent taxpayer lists publicly
- **Update frequency**: Most update quarterly (Jan, Apr, Jul, Oct)
- **Minimum threshold**: Most states only list accounts > $50K-$100K
- **Format varies**: HTML tables, PDFs, CSVs, and some APIs
- **JavaScript rendering**: ~60% of state sites need browser automation (Playwright/Selenium)
- **Static HTML**: ~40% can be scraped with simple HTTP requests
