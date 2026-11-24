# 2026 Canadian Personal Income Tax Calculator

A modular, object-oriented Python CLI application that estimates **2026 Canadian Federal, Provincial, and Territorial personal income taxes** across all **13 Canadian jurisdictions** (CRA & Revenu Québec rules).

---

## Key Features

- **Mandatory Residency Gatekeeper:** Establishes tax residency (as of December 31, 2026) before collecting financial data, accepting 2-letter postal codes (e.g., `ON`, `BC`, `QC`), full names (e.g., `Ontario`, `British Columbia`), and accented spellings (`Québec`).
- **Interactive Financial Data Collection:** Menu-driven workflow capturing realistic T1 income sources, tax-exempt receipts, deductions, and non-refundable tax credits.
- **2026 CRA & Revenu Québec Tax Rules:**
  - **Income Inclusion & Gross-Ups:** 50% capital gains inclusion rate, 38% eligible dividend gross-up, and 15% non-eligible dividend gross-up.
  - **Non-Taxable Exclusions:** Tracks TFSA withdrawals/growth, Principal Residence Exemption gains, windfalls/gifts/inheritances, and tax-free benefits (CCB, GST/HST Credit).
  - **Federal Reliefs & Clawbacks:** Income-tested Federal Basic Personal Amount ($16,452 phasing down to $14,829 between $181,440 and $258,482), Canada Employment Amount ($1,501), two-tier Charitable Donation Tax Credits (14% / 29% / 33%), Federal Dividend Tax Credits, and the **16.5% Quebec Abatement**.
  - **Provincial & Territorial Nuances:** Full brackets and BPAs for all 13 jurisdictions, including **Ontario's two-tier surtax** (20% over $5,818; +36% over $7,446), **Manitoba's BPA phase-out** ($200k–$400k), and **Yukon's mirrored Federal BPA clawback**.
- **T1-Style Reporting:** Reconciles gross cash inflow vs. CRA Line 15000 & Line 26000 income, combined marginal rate, average tax rate, effective cash tax rate, and net after-tax cash retained.

---

## Project Architecture (One Class Per File)

```text
canadian-tax-calculator/
├── canadian_tax_data.py         # CanadianTaxData: 2026 brackets, BPAs, aliases & rules
├── user.py                      # User: Residency validation, menu loop & tax_profile builder
├── tax_calculator.py            # TaxCalculator (ABC): Progressive bracket & shared credit math
├── federal_tax_calculator.py    # FederalTaxCalculator: CRA Schedule 1, BPA clawback & QC abatement
├── provincial_tax_calculator.py # ProvincialTaxCalculator: All 13 jurisdictions, ON surtax & MB clawback
├── tax_report.py                # TaxReport: T1-style console report & rate calculations
├── main.py                      # TaxAppCLI: Main CLI menu & workflow controller
└── README.md                    # Project documentation
```

---

## Developer Work Distribution

| Developer | Assigned Modules | Core Responsibilities |
| :--- | :--- | :--- |
| **Dev 1** | `canadian_tax_data.py`<br>`user.py` | Maintain 2026 tax tables, jurisdiction normalization, interactive input loop, and structured `tax_profile` generation. |
| **Dev 2** | `tax_calculator.py`<br>`federal_tax_calculator.py`<br>`provincial_tax_calculator.py` | Implement OOP inheritance (`ABC`), progressive bracket math, Federal credits/abatement, and all 13 Provincial/Territorial rules. |
| **Dev 3** | `tax_report.py`<br>`main.py`<br>`README.md` | Build the T1 summary report, CLI menu controller, input error handling, integration testing, and documentation. |

---

## Getting Started

### Prerequisites
- **Python 3.9+** (uses standard library modules only: `abc`, `typing`, `unicodedata`—no external packages required).

### Running the Application
1. Clone or download the repository into a single directory containing all seven `.py` files.
2. Open a terminal in the project folder and run:
   ```bash
   python main.py
   ```

---

## Usage Workflow & Sample Scenarios

1. **Select `1. Start New Tax Calculation`** from the main menu.
2. **Establish Tax Residency:** Enter a code or full name (e.g., `ON` or `Ontario`).
3. **Enter Financial Details via Menu Categories:**
   - **Category 1 (Taxable Income):** T4 employment, self-employment, interest, Canadian eligible/non-eligible dividends, total realized capital gains, rental, or pension/RRSP/EI income.
   - **Category 2 (Non-Taxable Receipts):** TFSA withdrawals, primary residence sale gains, gifts/inheritances, CCB/GST credits.
   - **Category 3 (Deductions):** RRSP/FHSA contributions, child care, union/professional dues, moving/employment expenses.
   - **Category 4 (Non-Refundable Credit Inputs):** CPP/QPP & EI premiums paid, charitable donations, medical expenses, post-secondary tuition.
4. **Select `6. Finalize & Proceed to Tax Calculation`** to view your complete 2026 Federal and Provincial/Territorial tax report.

### Quick Test Cases for Verification
- **Ontario (`ON`) Surtax Check:** Enter `Employment Income = $120,000` and `CPP/EI = $4,900` to verify Ontario Tier 1 & Tier 2 surtaxes trigger cleanly.
- **Quebec (`QC`) Abatement Check:** Enter `Employment Income = $95,000` in `Quebec` to verify the 16.5% reduction on Basic Federal Tax.
- **Capital Gains & TFSA Split:** Enter `Capital Gains = $40,000` and `TFSA Withdrawals = $15,000` to verify only $20,000 (50%) enters CRA Line 15000 while $35,000 remains tax-exempt.

---

## Disclaimer
This software is built for educational and estimation purposes using 2026 indexed Federal, Provincial, and Territorial tax parameters. Consult a CPA or official CRA / Revenu Québec schedules for formal tax filing.
