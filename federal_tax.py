from tax_calculator import TaxCalculator


class FederalTaxCalculator(TaxCalculator):
    def __init__(self):
        # Canadian federal income tax brackets for 2026.
        tax_brackets = [
            (58523, 0.14),
            (117045, 0.205),
            (181440, 0.26),
            (258482, 0.29),
            (None, 0.33)
        ]
        TaxCalculator.__init__(self, tax_brackets)
