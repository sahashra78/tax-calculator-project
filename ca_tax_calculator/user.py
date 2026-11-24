from typing import Dict, Any, Optional
from canadian_tax_data import CanadianTaxData


class User:
    """
    Represents a Canadian taxpayer for the 2026 tax year.
    Requires valid provincial/territorial tax residency before collecting
    income, deductions, and tax credits via an interactive menu loop.
    """

    def __init__(self, name: str = "Taxpayer", residency: Optional[str] = None) -> None:
        self._name: str = name.strip() if name and name.strip() else "Taxpayer"
        self._province_code: Optional[str] = None
        self._province_name: Optional[str] = None

        if residency:
            self.set_residency(residency)

        # Raw collected financial entries
        self._taxable_sources: Dict[str, float] = {
            "employment_income": 0.0,           # T4 Box 14
            "self_employment_net": 0.0,         # T2125 Net Business/Professional Income
            "interest_and_foreign_income": 0.0, # T5 / T3 Interest & Foreign Dividends
            "eligible_dividends_actual": 0.0,   # Actual Canadian Eligible Dividends received
            "non_eligible_dividends_actual": 0.0, # Actual Canadian Non-Eligible Dividends received
            "capital_gains_total": 0.0,         # Total realized capital gains (50% taxable)
            "rental_net_income": 0.0,           # T776 Net Rental Income
            "pension_rrsp_ei_income": 0.0,      # T4A / T4RSP / T4E (EI, OAS, CPP, RRSP withdrawals)
        }

        self._non_taxable_sources: Dict[str, float] = {
            "tfsa_withdrawals_gains": 0.0,      # Tax-Free Savings Account
            "primary_residence_gain": 0.0,      # Principal Residence Exemption
            "lottery_gifts_inheritance": 0.0,   # Windfalls, gifts, inheritances
            "gov_benefits_ccb_gst": 0.0,        # CCB, GST/HST Credit, provincial rebates
        }

        self._deductions: Dict[str, float] = {
            "rrsp_fhsa_contributions": 0.0,     # RRSP & First Home Savings Account deductions
            "child_care_expenses": 0.0,         # Form T778
            "union_professional_dues": 0.0,     # Line 21200
            "moving_employment_expenses": 0.0,  # Line 22900 / Line 21900
        }

        self._tax_credits_inputs: Dict[str, float] = {
            "cpp_qpp_ei_paid": 0.0,             # Employee CPP/QPP & EI premiums paid
            "charitable_donations": 0.0,        # Eligible donations (Line 34900)
            "medical_expenses": 0.0,            # Eligible medical expenses (Line 33099)
            "tuition_fees": 0.0,                # T2202 eligible tuition
        }

    # --- Residency Establishment (Mandatory Gatekeeper) ---

    def set_residency(self, jurisdiction_input: str) -> None:
        """Validates and sets the user's province or territory of residence (as of Dec 31)."""
        code = CanadianTaxData.resolve_jurisdiction(jurisdiction_input)
        self._province_code = code
        self._province_name = CanadianTaxData.get_jurisdiction_name(code)

    # def prompt_residency(self) -> None:
    #     """Interactive prompt that loops until a valid Canadian province/territory is set."""
    #     print("\n--- STEP 1: ESTABLISH CANADIAN TAX RESIDENCY (AS OF DEC 31, 2026) ---")
    #     print("You may enter a 2-letter code (e.g., ON, BC, QC) or full name (e.g., Ontario).")
    #     while not self.is_residency_established:
    #         user_input = input("Enter Province or Territory of residence: ")
    #         try:
    #             self.set_residency(user_input)
    #             print(f"Residency confirmed: {self._province_name} ({self._province_code})\n")
    #         except ValueError as e:
    #             print(f"[Residency Error] {e}\n")

    def prompt_residency(self) -> None:
        """Displays a numbered menu of Canadian provinces/territories until a valid choice is made."""
        # Sort jurisdictions alphabetically by full name
        jurisdictions = sorted(
            CanadianTaxData.JURISDICTION_NAMES.items(),
            key=lambda item: item[1]
        )
        marker_width = 120
        print("\n--- STEP 1: ESTABLISH CANADIAN TAX RESIDENCY (AS OF DEC 31, 2026) ---")
        for idx, (code, name) in enumerate(jurisdictions, start=1):
            print(f"      {idx:>2}. {name} ({code})")
        print("-" * marker_width)

        while not self.is_residency_established:
            choice = input("Select a number (1-13) or enter province/territory code/name: ").strip()
            try:
                if choice.isdigit():
                    num = int(choice)
                    if 1 <= num <= len(jurisdictions):
                        selected_code = jurisdictions[num - 1][0]
                        self.set_residency(selected_code)
                    else:
                        print(f"[Residency Error] Please select a number between 1 and {len(jurisdictions)}.\n")
                        continue
                else:
                    # Also supports direct code/name entry (e.g., "ON" or "Ontario")
                    self.set_residency(choice)

                print(f"Residency confirmed: {self._province_name} ({self._province_code})\n")
            except ValueError as e:
                print(f"[Residency Error] {e}\n")


    @property
    def is_residency_established(self) -> bool:
        return self._province_code is not None

    @property
    def province_code(self) -> str:
        if not self._province_code:
            raise RuntimeError("Tax residency has not been established yet.")
        return self._province_code

    @property
    def province_name(self) -> str:
        if not self._province_name:
            raise RuntimeError("Tax residency has not been established yet.")
        return self._province_name

    # --- Interactive Income, Deductions & Credits Collection ---

    @staticmethod
    def _prompt_amount(label: str, current_val: float) -> float:
        """Prompts for a non-negative dollar amount, allowing user to keep existing value."""
        while True:
            raw = input(f"  {label} [Current: ${current_val:,.2f}] (Enter amount or press Enter to keep): ")
            cleaned = raw.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return current_val
            try:
                val = float(cleaned)
                if val < 0:
                    print("    [Error] Amount cannot be negative.")
                    continue
                return round(val, 2)
            except ValueError:
                print("    [Error] Please enter a valid numeric dollar amount.")

    def collect_financial_data(self) -> Dict[str, Any]:
        """
        Menu-driven loop to collect realistic annual Canadian financial data.
        Blocks execution until tax residency is established.
        Returns the fully structured dictionary ready for the calculators.
        """
        if not self.is_residency_established:
            self.prompt_residency()
        marker_width = 120
        while True:
            print("=" * marker_width)
            print(f"    2026 TAX DATA COLLECTION | {self._name.upper()} ({self._province_name})")
            print("=" * marker_width)
            print("     1. Enter/Edit Taxable Income (T4, Self-Employed, Dividends, Cap Gains, etc.)")
            print("     2. Enter/Edit Non-Taxable Income (TFSA, Primary Residence, Gifts, CCB/GST)")
            print("     3. Enter/Edit Tax Deductions (RRSP, FHSA, Child Care, Union Dues)")
            print("     4. Enter/Edit Non-Refundable Credit Inputs (CPP/EI, Donations, Medical, Tuition)")
            print("     5. Review Current Totals & Summary")
            print("     6. Finalize & Proceed to Tax Calculation")
            print("-" * marker_width)

            choice = input("Select a category (1-6): ").strip()

            if choice == "1":
                self._menu_taxable_income()
            elif choice == "2":
                self._menu_non_taxable_income()
            elif choice == "3":
                self._menu_deductions()
            elif choice == "4":
                self._menu_tax_credits()
            elif choice == "5":
                self._print_quick_review()
            elif choice == "6":
                print("\nData collection finalized. Preparing payload for tax calculators...\n")
                return self.get_structured_tax_profile()
            else:
                print("[Invalid Option] Please select a number between 1 and 6.\n")

    def _menu_taxable_income(self) -> None:
        print("\n--- TAXABLE INCOME SOURCES (2026) ---")
        self._taxable_sources["employment_income"] = self._prompt_amount(
            "Employment Income (T4 Box 14)", self._taxable_sources["employment_income"]
        )
        self._taxable_sources["self_employment_net"] = self._prompt_amount(
            "Net Self-Employment / Business Income (T2125)", self._taxable_sources["self_employment_net"]
        )
        self._taxable_sources["interest_and_foreign_income"] = self._prompt_amount(
            "Interest & Foreign Investment Income (T5/T3)", self._taxable_sources["interest_and_foreign_income"]
        )
        self._taxable_sources["eligible_dividends_actual"] = self._prompt_amount(
            "Canadian Eligible Dividends (Actual Cash Received)", self._taxable_sources["eligible_dividends_actual"]
        )
        self._taxable_sources["non_eligible_dividends_actual"] = self._prompt_amount(
            "Canadian Non-Eligible Dividends (Actual Cash Received)", self._taxable_sources["non_eligible_dividends_actual"]
        )
        self._taxable_sources["capital_gains_total"] = self._prompt_amount(
            "Total Realized Capital Gains (Before 50% Inclusion)", self._taxable_sources["capital_gains_total"]
        )
        self._taxable_sources["rental_net_income"] = self._prompt_amount(
            "Net Rental Income (T776)", self._taxable_sources["rental_net_income"]
        )
        self._taxable_sources["pension_rrsp_ei_income"] = self._prompt_amount(
            "Pension, CPP/OAS, EI, or RRSP Withdrawals", self._taxable_sources["pension_rrsp_ei_income"]
        )
        print("---\n")

    def _menu_non_taxable_income(self) -> None:
        print("\n--- NON-TAXABLE INCOME & RECEIPTS (EXCLUDED FROM TAXABLE INCOME) ---")
        self._non_taxable_sources["tfsa_withdrawals_gains"] = self._prompt_amount(
            "TFSA Withdrawals & Investment Growth", self._non_taxable_sources["tfsa_withdrawals_gains"]
        )
        self._non_taxable_sources["primary_residence_gain"] = self._prompt_amount(
            "Principal Residence Sale Gain (Exempt)", self._non_taxable_sources["primary_residence_gain"]
        )
        self._non_taxable_sources["lottery_gifts_inheritance"] = self._prompt_amount(
            "Lottery Windfalls, Gifts, or Inheritances", self._non_taxable_sources["lottery_gifts_inheritance"]
        )
        self._non_taxable_sources["gov_benefits_ccb_gst"] = self._prompt_amount(
            "Tax-Free Gov Benefits (CCB, GST/HST Credit, Trillium/Rebates)", self._non_taxable_sources["gov_benefits_ccb_gst"]
        )
        print("---\n")

    def _menu_deductions(self) -> None:
        print("\n--- TAX DEDUCTIONS (REDUCE NET & TAXABLE INCOME) ---")
        self._deductions["rrsp_fhsa_contributions"] = self._prompt_amount(
            "RRSP & FHSA Contributions", self._deductions["rrsp_fhsa_contributions"]
        )
        self._deductions["child_care_expenses"] = self._prompt_amount(
            "Eligible Child Care Expenses (T778)", self._deductions["child_care_expenses"]
        )
        self._deductions["union_professional_dues"] = self._prompt_amount(
            "Annual Union, Professional, or Like Dues", self._deductions["union_professional_dues"]
        )
        self._deductions["moving_employment_expenses"] = self._prompt_amount(
            "Allowable Employment / Moving Expenses", self._deductions["moving_employment_expenses"]
        )
        print("---\n")

    def _menu_tax_credits(self) -> None:
        print("\n--- NON-REFUNDABLE TAX CREDIT INPUTS ---")
        self._tax_credits_inputs["cpp_qpp_ei_paid"] = self._prompt_amount(
            "CPP/QPP & EI Premiums Paid (T4 Boxes 16/17/18)", self._tax_credits_inputs["cpp_qpp_ei_paid"]
        )
        self._tax_credits_inputs["charitable_donations"] = self._prompt_amount(
            "Charitable Donations Made in 2026", self._tax_credits_inputs["charitable_donations"]
        )
        self._tax_credits_inputs["medical_expenses"] = self._prompt_amount(
            "Eligible Medical Expenses Paid", self._tax_credits_inputs["medical_expenses"]
        )
        self._tax_credits_inputs["tuition_fees"] = self._prompt_amount(
            "Eligible Post-Secondary Tuition Fees (T2202)", self._tax_credits_inputs["tuition_fees"]
        )
        print("---\n")

    # --- Taxable vs. Non-Taxable Calculations & Structured Output ---

    def get_structured_tax_profile(self) -> Dict[str, Any]:
        """
        Applies Canadian tax inclusion/gross-up rules and returns a structured
        dictionary containing 'residency', 'taxable', 'non_taxable', and 'details'.
        """
        if not self.is_residency_established:
            raise RuntimeError("Cannot generate tax profile before establishing tax residency.")

        rules = CanadianTaxData.INCOME_TAXABILITY_RULES

        # Apply CRA gross-ups and inclusion rates
        taxable_cap_gains = round(
            self._taxable_sources["capital_gains_total"] * rules["capital_gains_inclusion_rate"], 2
        )
        grossed_up_eligible_div = round(
            self._taxable_sources["eligible_dividends_actual"] * rules["eligible_dividend_grossup"], 2
        )
        grossed_up_non_eligible_div = round(
            self._taxable_sources["non_eligible_dividends_actual"] * rules["non_eligible_dividend_grossup"], 2
        )

        # Total Gross Cash Income (actual money received)
        actual_taxable_cash = sum(self._taxable_sources.values())
        total_non_taxable = round(sum(self._non_taxable_sources.values()), 2)
        total_gross_cash_inflow = round(actual_taxable_cash + total_non_taxable, 2)

        # Line 15000: Total Income (includes grossed-up dividends and 50% cap gains)
        line_15000_total_income = round(
            self._taxable_sources["employment_income"]
            + self._taxable_sources["self_employment_net"]
            + self._taxable_sources["interest_and_foreign_income"]
            + grossed_up_eligible_div
            + grossed_up_non_eligible_div
            + taxable_cap_gains
            + self._taxable_sources["rental_net_income"]
            + self._taxable_sources["pension_rrsp_ei_income"],
            2,
        )

        # Line 23600 / 26000: Net & Taxable Income after deductions
        total_deductions = round(sum(self._deductions.values()), 2)
        taxable_income = round(max(0.0, line_15000_total_income - total_deductions), 2)

        return {
            "tax_year": CanadianTaxData.TAX_YEAR,
            "residency": {
                "name": self._name,
                "province_code": self._province_code,
                "province_name": self._province_name,
            },
            "taxable": {
                "line_15000_total_income": line_15000_total_income,
                "total_deductions": total_deductions,
                "net_taxable_income": taxable_income,
                "taxable_capital_gains": taxable_cap_gains,
                "grossed_up_eligible_dividends": grossed_up_eligible_div,
                "grossed_up_non_eligible_dividends": grossed_up_non_eligible_div,
            },
            "non_taxable": {
                "total_non_taxable_income": total_non_taxable,
                "exempt_capital_gains_portion": round(
                    self._taxable_sources["capital_gains_total"] - taxable_cap_gains, 2
                ),
                "total_gross_cash_inflow": total_gross_cash_inflow,
            },
            "details": {
                "taxable_sources_raw": dict(self._taxable_sources),
                "non_taxable_sources_raw": dict(self._non_taxable_sources),
                "deductions_raw": dict(self._deductions),
                "tax_credit_inputs_raw": dict(self._tax_credits_inputs),
            },
        }

    def _print_quick_review(self) -> None:
        profile = self.get_structured_tax_profile()
        print("\n--- CURRENT SUMMARY PREVIEW ---")
        print(f"    Total Gross Cash Inflow   : ${profile['non_taxable']['total_gross_cash_inflow']:,.2f}")
        print(f"    Non-Taxable Income        : ${profile['non_taxable']['total_non_taxable_income']:,.2f}")
        print(f"    CRA Line 15000 Income     : ${profile['taxable']['line_15000_total_income']:,.2f}")
        print(f"    Total Deductions          : -${profile['taxable']['total_deductions']:,.2f}")
        print(f"    Net Taxable Income        : ${profile['taxable']['net_taxable_income']:,.2f}\n")
