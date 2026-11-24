# Dev 1 – Canadian Tax Calculator (2026)

This folder contains the Dev 1 classes and basic tests for the group's final project.
The code uses classes, inheritance, lists, tuples, dictionaries, loops, decisions,
functions, and exception handling from the course lectures (Chapters 1–11).

## Files

- `tax_calculator.py` – parent class for progressive tax calculations and effective rate.
- `federal_tax.py` – 2026 Canadian federal brackets.
- `provincial_tax.py` – 2026 Saskatchewan and Manitoba brackets.
- `test_dev1.py` – basic tests; no extra packages.

## Run tests

Keep the four Python files in the same directory and run:

    python3 test_dev1.py

## How the classmates can call the classes

    from federal_tax import FederalTaxCalculator
    from provincial_tax import ProvincialTaxCalculator

    income = 50000
    federal_tax = FederalTaxCalculator().calculate_tax(income)
    provincial_tax = ProvincialTaxCalculator('SK').calculate_tax(income)
    print(federal_tax, provincial_tax)

Use 'SK' or 'MB', or the full province name. Tax methods return a numeric amount,
not printed output. The other developers handle the CLI, users and reports.

## Simplifications to stay close to the lecture slides

- Removed `import math` and `math.isfinite()`. Input must be a numeric value between
  $0 and $1,000,000,000, inclusive. This clear limit also rejects infinite and NaN values.
  The upper limit is a project-level input-validation choice, not a tax law.
- Used `.upper()` and `.replace(' ', '')` (Chapter 8 string methods) instead of `.strip()`.
- Replaced the `float('inf')` test with a test for income above the stated limit.
- Kept `round(..., 2)` to return amounts to two decimal places.
- Kept `raise ValueError(...)` so the other developers can catch invalid inputs using
  `try` / `except ValueError`. This small statement goes beyond the exact examples in
  Chapter 6, but removing it would change the error-handling behavior.

## Tax scope

Inputs are annual **taxable income in CAD**, not gross income.
Calculations are **bracket tax before credits**, not final tax owing.
No deductions, tax credits, CPP, EI, or other special rules are included.

At $50,000 taxable income:
- Federal bracket tax: $7,000.00
- Saskatchewan bracket tax: $5,250.00
- Manitoba bracket tax: $5,458.50

## Bracket sources

Federal and Saskatchewan 2026 tax rates (CRA):
https://www.canada.ca/en/revenue-agency/services/tax/individuals/tax-rates-brackets/current-year.html

Manitoba 2026 rates used in this project (CRA Manitoba-specific payroll tables):
https://www.canada.ca/en/revenue-agency/services/forms-publications/payroll/t4032-payroll-deductions-tables/t4032mb-jan/t4032mb-january-general-information.html

Manitoba's Finance page discusses the indexation freeze:
https://gov.mb.ca/finance/personal/ptaxes.html

**Documentation note:** CRA's general 2026 individual income tax page lists
Manitoba thresholds of $47,564 and $101,200, while its Manitoba-specific 2026
payroll tables list $47,000 and $100,000. This project retains the previous
$47,000 and $100,000 assumptions, supported by the Manitoba-specific tables.
The group should state this source difference in its report.

## Integration note

This is the Canadian version of the project. Use `ProvincialTaxCalculator` from
`provincial_tax.py`; the old US `StateTaxCalculator` and `state_tax.py` are not
part of this version. The user interface should ask for a province, not a state.
