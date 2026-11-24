from tax_calculators import FederalTaxCalculator, StateTaxCalculator
from models import User, TaxReport


class TaxAppCLI:
    """Command-Line Interface controller for the Tax Calculator application."""

    def __init__(self) -> None:
        self._federal_calc = FederalTaxCalculator()

    def display_menu(self) -> None:
        print("\n--- ANNUAL INCOME TAX CALCULATOR ---")
        print("1. Calculate Income Tax")
        print("2. View Supported States")
        print("3. Exit")

    def _prompt_user_details(self) -> User:
        """Prompts and validates user input, retrying until valid data is entered."""
        name = input("Enter your name (press Enter for 'Taxpayer'): ")

        while True:
            try:
                raw_income = input("Enter your gross annual income ($): ").replace(",", "").strip()
                income = float(raw_income)

                supported = ", ".join(StateTaxCalculator.get_supported_states())
                state = input(f"Enter your state code ({supported}): ")

                # Validation occurs inside the User setters
                return User(annual_income=income, state=state, name=name)

            except ValueError as e:
                print(f"[Input Error] {e} Please try again.\n")

    def _process_calculation(self) -> None:
        user = self._prompt_user_details()
        state_calc = StateTaxCalculator(user.state)

        fed_tax = self._federal_calc.calculate_tax(user.annual_income)
        state_tax = state_calc.calculate_tax(user.annual_income)

        report = TaxReport(user=user, federal_tax=fed_tax, state_tax=state_tax)
        report.display_summary()

    def run(self) -> None:
        """Main application execution loop."""
        while True:
            self.display_menu()
            choice = input("Select an option (1-3): ").strip()

            if choice == "1":
                self._process_calculation()
            elif choice == "2":
                states = ", ".join(StateTaxCalculator.get_supported_states())
                print(f"\nSupported States: {states}")
            elif choice == "3":
                print("Exiting Tax Calculator. Goodbye!")
                break
            else:
                print("[Invalid Choice] Please enter 1, 2, or 3.")


if __name__ == "__main__":
    app = TaxAppCLI()
    app.run()
