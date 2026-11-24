class TaxCalculator:
    def __init__(self, tax_brackets):
        self.__tax_brackets = tax_brackets

    def calculate_tax(self, income):
        # Accept numbers only, from 0 to 1 billion dollars.
        if not isinstance(income, (int, float)):
            raise ValueError('Income must be a number.')

        if not (0 <= income <= 1000000000):
            raise ValueError('Income must be between 0 and 1 billion.')

        total_tax = 0
        previous_limit = 0

        # Each rate applies only to the income inside that bracket.
        for limit, rate in self.__tax_brackets:
            if limit is None or income <= limit:
                total_tax += (income - previous_limit) * rate
                break
            else:
                total_tax += (limit - previous_limit) * rate
                previous_limit = limit

        return round(total_tax, 2)

    def get_effective_rate(self, income, tax_owed):
        if not isinstance(income, (int, float)):
            raise ValueError('Income must be a number.')

        if not (0 <= income <= 1000000000):
            raise ValueError('Income must be between 0 and 1 billion.')

        if income == 0:
            return 0

        return round(tax_owed / income * 100, 2)
