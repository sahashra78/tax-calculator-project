from user import User
from canadian_tax_data import CanadianTaxData
from federal_tax_calculator import FederalTaxCalculator
from provincial_tax_calculator import ProvincialTaxCalculator
from tax_report import TaxReport


class TaxAppCLI:
    """
    Main Command-Line Interface controller for the 2026 Canadian
    Federal & Provincial/Territorial Income Tax Calculator.
    """
    def __init__(self) -> None:
        self._federal_calculator = FederalTaxCalculator()

    def display_main_menu(self) -> None:
        marker_width = 120
        print("\n" + "=" * marker_width)
        print(" 2026 CANADIAN INCOME TAX CALCULATOR (FEDERAL & PROVINCIAL)")
        print("=" * marker_width)
        print("     1. Start New Tax Calculation")
        print("     2. View Supported Provinces & Territories")
        print("     3. View CRA Non-Taxable Income Guidelines")
        print("     4. Exit")
        print("-" * marker_width)

    def _display_supported_jurisdictions(self) -> None:
        print("\n--- SUPPORTED CANADIAN PROVINCES & TERRITORIES (2026) ---")
        for code, full_name in sorted(CanadianTaxData.JURISDICTION_NAMES.items()):
            bpa = CanadianTaxData.PROVINCIAL_DATA[code]["bpa"]
            top_rate = CanadianTaxData.PROVINCIAL_DATA[code]["brackets"][-1][1] * 100
            print(f"  {code} - {full_name:<26} | Base BPA: ${bpa:>9,.2f} | Top Bracket: {top_rate:.2f}%")
        print()

    def _display_non_taxable_rules(self) -> None:
        print("\n--- COMMON NON-TAXABLE INCOME & RECEIPTS IN CANADA ---")
        for item in CanadianTaxData.INCOME_TAXABILITY_RULES["non_taxable_categories"]:
            print(f"  • {item}")
        print("  • Plus: 50% of realized capital gains (only 50% is included in taxable income)\n")

    def _run_tax_workflow(self) -> None:
        """
        Orchestrates the end-to-end tax flow:
        1. Instantiate User & establish tax residency first
        2. Run interactive menu loop to collect financial data & build tax profile
        3. Pass profile to Federal and Provincial/Territorial calculators
        4. Generate and display the final TaxReport
        """
        name = input("\nEnter taxpayer's name (press Enter for 'Taxpayer'): ")
        user = User(name=name)

        # Mandatory Step 1: Establish residency before any financial data entry
        user.prompt_residency()

        # Step 2: Interactive menu loop to collect income, deductions, and credits
        tax_profile = user.collect_financial_data()

        # Step 3: Run Federal and Provincial/Territorial calculations
        prov_code = tax_profile["residency"]["province_code"]
        provincial_calculator = ProvincialTaxCalculator(prov_code)

        federal_result = self._federal_calculator.calculate_tax(tax_profile)
        provincial_result = provincial_calculator.calculate_tax(tax_profile)

        # Step 4: Compile and print final report
        report = TaxReport(
            tax_profile=tax_profile,
            federal_result=federal_result,
            provincial_result=provincial_result,
        )
        report.display_summary()

    def run(self) -> None:
        """Starts the main interactive application loop."""
        while True:
            self.display_main_menu()
            choice = input("Select an option (1-4): ").strip()

            if choice == "1":
                try:
                    self._run_tax_workflow()
                except Exception as exc:
                    print(f"\n[Application Error] An unexpected error occurred: {exc}\n")
            elif choice == "2":
                self._display_supported_jurisdictions()
            elif choice == "3":
                self._display_non_taxable_rules()
            elif choice == "4":
                print("Thank you for using the 2026 Canadian Tax Calculator. Goodbye!")
                break
            else:
                print("[Invalid Choice] Please select a valid option (1-4).")


if __name__ == "__main__":
    app = TaxAppCLI()
    app.run()
