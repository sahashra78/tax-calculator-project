from abc import ABC, abstractmethod
from typing import List, Tuple, Dict


class TaxCalculator(ABC):
    """Abstract base class defining the blueprint for tax calculations."""

    def __init__(self, brackets: List[Tuple[float, float]]) -> None:
        # Each tuple represents (upper_income_limit, tax_rate)
        self._brackets: List[Tuple[float, float]] = brackets

    def calculate_tax(self, income: float) -> float:
        """Computes progressive tax across defined brackets."""
        if income <= 0:
            return 0.0

        tax_owed: float = 0.0
        previous_limit: float = 0.0

        for upper_limit, rate in self._brackets:
            if income > previous_limit:
                taxable_amount = min(income, upper_limit) - previous_limit
                tax_owed += taxable_amount * rate
                previous_limit = upper_limit
            else:
                break

        return round(tax_owed, 2)

    @abstractmethod
    def get_tax_type(self) -> str:
        """Returns the category of tax being calculated."""
        pass


class FederalTaxCalculator(TaxCalculator):
    """Calculates federal income tax using predefined progressive brackets."""

    def __init__(self) -> None:
        # Simplified standard federal tax brackets
        federal_brackets: List[Tuple[float, float]] = [
            (11600.0, 0.10),
            (47150.0, 0.12),
            (100525.0, 0.22),
            (191950.0, 0.24),
            (243725.0, 0.32),
            (609350.0, 0.35),
            (float("inf"), 0.37),
        ]
        super().__init__(federal_brackets)

    def get_tax_type(self) -> str:
        return "Federal Income Tax"


class StateTaxCalculator(TaxCalculator):
    """Calculates state income tax based on predefined state-specific rates."""

    # Sample database of state tax brackets (flat and progressive examples)
    STATE_BRACKETS_DB: Dict[str, List[Tuple[float, float]]] = {
        "CA": [(10412.0, 0.01), (24684.0, 0.02), (38959.0, 0.04), (float("inf"), 0.093)],
        "NY": [(8500.0, 0.04), (11700.0, 0.045), (13900.0, 0.0525), (float("inf"), 0.0685)],
        "IL": [(float("inf"), 0.0495)],  # Flat tax state
        "TX": [(float("inf"), 0.0)],     # No state income tax
        "FL": [(float("inf"), 0.0)],     # No state income tax
    }

    def __init__(self, state: str) -> None:
        self._state: str = state.upper().strip()
        if self._state not in self.STATE_BRACKETS_DB:
            raise ValueError(f"Unsupported state code: '{self._state}'")
        super().__init__(self.STATE_BRACKETS_DB[self._state])

    @property
    def state(self) -> str:
        return self._state

    def get_tax_type(self) -> str:
        return f"State Income Tax ({self._state})"

    @classmethod
    def get_supported_states(cls) -> List[str]:
        return list(cls.STATE_BRACKETS_DB.keys())
