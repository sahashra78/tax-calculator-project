from typing import Dict, Any


class TaxReport:
    """
    Compiles and formats the 2026 Canadian Personal Income Tax Summary Report
    from the User tax profile and Federal/Provincial calculation outputs.
    """

    def __init__(
        self,
        tax_profile: Dict[str, Any],
        federal_result: Dict[str, float],
        provincial_result: Dict[str, float],
    ) -> None:
        self._profile: Dict[str, Any] = tax_profile
        self._fed: Dict[str, float] = federal_result
        self._prov: Dict[str, float] = provincial_result

    def calculate_total_tax(self) -> float:
        """Returns combined Net Federal and Net Provincial/Territorial income tax."""
        return round(
            self._fed["net_federal_tax"] + self._prov["net_provincial_tax"], 2
        )

    def calculate_net_after_tax_cash(self) -> float:
        """
        Calculates total after-tax cash retained from all actual cash inflows
        (both taxable cash income and non-taxable receipts, minus income tax payable).
        """
        gross_cash = self._profile["non_taxable"]["total_gross_cash_inflow"]
        return round(gross_cash - self.calculate_total_tax(), 2)

    def calculate_average_tax_rate(self) -> float:
        """Total tax divided by CRA Net Taxable Income (%)."""
        taxable_income = self._profile["taxable"]["net_taxable_income"]
        if taxable_income <= 0:
            return 0.0
        return round((self.calculate_total_tax() / taxable_income) * 100, 2)

    def calculate_effective_cash_tax_rate(self) -> float:
        """Total tax divided by Total Gross Cash Inflow including tax-free items (%)."""
        gross_cash = self._profile["non_taxable"]["total_gross_cash_inflow"]
        if gross_cash <= 0:
            return 0.0
        return round((self.calculate_total_tax() / gross_cash) * 100, 2)

    def calculate_combined_marginal_rate(self) -> float:
        """
        Combined top Federal + Provincial/Territorial marginal rate (%).
        Accounts for the 16.5% Quebec federal abatement when resident in QC.
        """
        fed_marginal = self._fed["federal_marginal_rate"]
        if self._profile["residency"]["province_code"] == "QC":
            fed_marginal = round(fed_marginal * (1.0 - 0.165), 2)
        return round(fed_marginal + self._prov["provincial_marginal_rate"], 2)

    def display_summary(self) -> None:
        """Prints a comprehensive T1-style Canadian tax breakdown to the console."""
        residency = self._profile["residency"]
        taxable = self._profile["taxable"]
        non_taxable = self._profile["non_taxable"]
        details = self._profile["details"]

        total_tax = self.calculate_total_tax()
        net_cash = self.calculate_net_after_tax_cash()
        avg_rate = self.calculate_average_tax_rate()
        eff_rate = self.calculate_effective_cash_tax_rate()
        marginal_rate = self.calculate_combined_marginal_rate()

        width = 68
        print("\n" + "=" * width)
        print(f"2026 CANADIAN PERSONAL INCOME TAX REPORT (T1 SUMMARY)")
        print(f"Taxpayer: {residency['name']} | Residency: {residency['province_name']} ({residency['province_code']})")
        print("=" * width)

        # Section 1: Income & Taxability Reconciliation
        print("\n[1] INCOME & TAXABILITY RECONCILIATION")
        print("-" * width)
        print(f"  Total Actual Gross Cash Inflow        : ${non_taxable['total_gross_cash_inflow']:>14,.2f}")
        print(f"  Less: Non-Taxable Receipts            : -${non_taxable['total_non_taxable_income']:>13,.2f}")
        if non_taxable["exempt_capital_gains_portion"] > 0:
            print(f"  Less: Exempt 50% Capital Gains        : -${non_taxable['exempt_capital_gains_portion']:>13,.2f}")
        if taxable["grossed_up_eligible_dividends"] > 0:
            actual_el = details["taxable_sources_raw"]["eligible_dividends_actual"]
            gross_el = taxable["grossed_up_eligible_dividends"]
            print(f"  Add: Eligible Dividend Gross-Up (38%) : +${(gross_el - actual_el):>13,.2f}")
        if taxable["grossed_up_non_eligible_dividends"] > 0:
            actual_nel = details["taxable_sources_raw"]["non_eligible_dividends_actual"]
            gross_nel = taxable["grossed_up_non_eligible_dividends"]
            print(f"  Add: Non-Elig. Div. Gross-Up (15%)    : +${(gross_nel - actual_nel):>13,.2f}")
        print("-" * width)
        print(f"  CRA Line 15000 - Total Income         : ${taxable['line_15000_total_income']:>14,.2f}")
        print(f"  Less: Total Deductions (RRSP/FHSA/etc): -${taxable['total_deductions']:>13,.2f}")
        print(f"  CRA Line 26000 - Taxable Income       : ${taxable['net_taxable_income']:>14,.2f}")

        # Section 2: Federal Tax Breakdown
        print("\n[2] FEDERAL INCOME TAX BREAKDOWN (CRA)")
        print("-" * width)
        print(f"  Gross Federal Tax on Brackets         : ${self._fed['gross_bracket_tax']:>14,.2f}")
        print(f"  Federal BPA Claimed                   : ${self._fed['federal_bpa_claimed']:>14,.2f}")
        print(f"  Less: Non-Refundable & Donation Cred. : -${(self._fed['base_non_refundable_credits'] + self._fed['donation_credit']):>13,.2f}")
        if self._fed["dividend_tax_credit"] > 0:
            print(f"  Less: Federal Dividend Tax Credit     : -${self._fed['dividend_tax_credit']:>13,.2f}")
        if self._fed["quebec_abatement"] > 0:
            print(f"  Less: Quebec Abatement (16.5%)        : -${self._fed['quebec_abatement']:>13,.2f}")
        print(f"  Net Federal Tax Payable               : ${self._fed['net_federal_tax']:>14,.2f}")

        # Section 3: Provincial / Territorial Tax Breakdown
        print(f"\n[3] {residency['province_name'].upper()} TAX BREAKDOWN")
        print("-" * width)
        print(f"  Gross Provincial/Territorial Tax      : ${self._prov['gross_bracket_tax']:>14,.2f}")
        print(f"  Provincial/Territorial BPA Claimed    : ${self._prov['provincial_bpa_claimed']:>14,.2f}")
        print(f"  Less: Non-Refundable & Donation Cred. : -${(self._prov['base_non_refundable_credits'] + self._prov['donation_credit']):>13,.2f}")
        if self._prov["dividend_tax_credit"] > 0:
            print(f"  Less: Provincial Dividend Tax Credit  : -${self._prov['dividend_tax_credit']:>13,.2f}")
        if self._prov["surtax"] > 0:
            print(f"  Add: Ontario Surtax                   : +${self._prov['surtax']:>13,.2f}")
        print(f"  Net {residency['province_name']} Tax Payable : ${self._prov['net_provincial_tax']:>14,.2f}")

        # Section 4: Final Summary & Rates
        print("\n[4] FINAL SUMMARY & TAX RATES")
        print("-" * width)
        print(f"  Total Combined Income Tax Payable     : ${total_tax:>14,.2f}")
        print(f"  Combined Marginal Tax Rate            : {marginal_rate:>14.2f}%")
        print(f"  Average Tax Rate (on Taxable Income)  : {avg_rate:>14.2f}%")
        print(f"  Effective Tax Rate (on Gross Cash)    : {eff_rate:>14.2f}%")
        print(f"  Net After-Tax Cash Retained           : ${net_cash:>14,.2f}")
        print("=" * width + "\n")
