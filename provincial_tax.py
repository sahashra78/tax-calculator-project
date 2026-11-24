from tax_calculator import TaxCalculator


class ProvincialTaxCalculator(TaxCalculator):
    def __init__(self, province):
        if not isinstance(province, str):
            raise ValueError('Province must be a name or code.')

        # Accept SK, MB, Saskatchewan and Manitoba.
        province = province.upper()
        province = province.replace(' ', '')

        if province == 'SASKATCHEWAN':
            province = 'SK'
        elif province == 'MANITOBA':
            province = 'MB'

        # Canadian provincial tax brackets for 2026.
        province_brackets = {
            'SK': [
                (54532, 0.105),
                (155805, 0.125),
                (None, 0.145)
            ],
            'MB': [
                (47000, 0.108),
                (100000, 0.1275),
                (None, 0.174)
            ]
        }

        if province not in province_brackets:
            raise ValueError('Only Saskatchewan and Manitoba are supported.')

        self.__province = province
        TaxCalculator.__init__(self, province_brackets[province])

    def get_province(self):
        return self.__province
