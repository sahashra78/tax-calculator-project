from tax_calculators import StateTaxCalculator


class User:
    """Encapsulates user financial data with strict input validation."""

    def __init__(self, annual_income: float, state: str, name: str = "Taxpayer") -> None:
        self.name = name
        self.annual_income = annual_income
        self.state = state

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        cleaned = value.strip()
        self._name = cleaned if cleaned else "Taxpayer"

    @property
    def annual_income(self) -> float:
        return self._annual_income

    @annual_income.setter
    def annual_income(self, value: float) -> None:
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Annual income must be a non-negative number.")
        if value > 1_000_000_000:
            raise ValueError("Annual income exceeds reasonable calculation limits.")
        self._annual_income = float(value)

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, value: str) -> None:
        cleaned_state = value.upper().strip()
        if cleaned_state not in StateTaxCalculator.get_supported_states():
            supported = ", ".join(StateTaxCalculator.get_supported_states())
            raise ValueError(f"Invalid state '{value}'. Supported states: {supported}")
        self._state = cleaned_state


class TaxReport:
    """Compiles and formats the tax calculation results for display."""

    def __init__(self, user: User, federal_tax: float, state_tax: float) -> None:
        self._user: User = user
        self._federal_tax: float = federal_tax
        self._state_tax: float = state_tax

    def calculate_total_tax(self) -> float:
        return round(self._federal_tax + self._state_tax, 2)

    def calculate_net_income(self) -> float:
        return round(self._user.annual_income - self.calculate_total_tax(), 2)

    def calculate_effective_rate(self) -> float:
        if self._user.annual_income == 0:
            return 0.0
        return round((self.calculate_total_tax() / self._user.annual_income) * 100, 2)

    def display_summary(self) -> None:
        """Prints a formatted summary report to the console."""
        print("\n" + "=" * 45)
        print(f"TAX SUMMARY REPORT - {self._user.name.upper()}")
        print("=" * 45)
        print(f"State of Residence : {self._user.state}")
        print(f"Gross Annual Income: ${self._user.annual_income:,.2f}")
        print("-" * 45)
        print(f"Federal Income Tax : ${self._federal_tax:,.2f}")
        print(f"State Income Tax   : ${self._state_tax:,.2f}")
        print(f"Total Tax Owed     : ${self.calculate_total_tax():,.2f}")
        print("-" * 45)
        print(f"Effective Tax Rate : {self.calculate_effective_rate()}%")
        print(f"Net After-Tax Pay  : ${self.calculate_net_income():,.2f}")
        print("=" * 45 + "\n")
