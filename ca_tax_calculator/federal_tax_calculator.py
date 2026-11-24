from typing import Dict, Any
from canadian_tax_data import CanadianTaxData
from tax_calculator import TaxCalculator


class FederalTaxCalculator(TaxCalculator):
    """
    Computes 2026 Canadian Federal Income Tax including progressive brackets,
    income-tested BPA clawback, non-refundable credits, dividend tax credits,
    charitable donation tiers, and the 16.5% Quebec abatement.
    """

    def __init__(self) -> None:
        rules = CanadianTaxData.FEDERAL_RULES
        super().__init__(
            brackets=CanadianTaxData.FEDERAL_BRACKETS,
            lowest_rate=rules["lowest_rate"],
        )
        self._rules = rules
        self._taxability_rules = CanadianTaxData.INCOME_TAXABILITY_RULES

    def _calculate_federal_bpa(self, net_income: float) -> float:
        """
        Computes the 2026 Federal Basic Personal Amount ($16,452 max,
        phasing down to $14,829 between $181,440 and $258,482 net income).
        """
        bpa_max = self._rules["bpa_max"]
        bpa_min = self._rules["bpa_min"]
        start = self._rules["bpa_clawback_start"]
        end = self._rules["bpa_clawback_end"]

        if net_income <= start:
            return bpa_max
        if net_income >= end:
            return bpa_min

        reduction_ratio = (net_income - start) / (end - start)
        clawed_back_bpa = bpa_max - (bpa_max - bpa_min) * reduction_ratio
        return round(clawed_back_bpa, 2)

    def _calculate_donation_credit(self, donations: float, taxable_income: float) -> float:
        """
        Computes the 2026 Federal Charitable Donation Tax Credit:
        - 14.0% on the first $200
        - 33.0% on amounts over $200 up to taxable income exceeding $258,482
        - 29.0% on remaining amounts over $200
        """
        if donations <= 0:
            return 0.0

        if donations <= 200.0:
            return round(donations * self._rules["donation_rate_low"], 2)

        first_200_credit = 200.0 * self._rules["donation_rate_low"]
        excess_donations = donations - 200.0

        top_bracket_threshold = self._rules["bpa_clawback_end"]  # $258,482
        income_in_top_bracket = max(0.0, taxable_income - top_bracket_threshold)

        amount_at_33 = min(excess_donations, income_in_top_bracket)
        amount_at_29 = excess_donations - amount_at_33

        credit = (
            first_200_credit
            + (amount_at_33 * self._rules["donation_rate_top"])
            + (amount_at_29 * self._rules["donation_rate_high"])
        )
        return round(credit, 2)

    def calculate_tax(self, tax_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates the complete 2026 Federal Tax breakdown from the User profile.
        """
        province_code: str = tax_profile["residency"]["province_code"]
        taxable_data: Dict[str, float] = tax_profile["taxable"]
        raw_taxable: Dict[str, float] = tax_profile["details"]["taxable_sources_raw"]
        raw_credits: Dict[str, float] = tax_profile["details"]["tax_credit_inputs_raw"]

        taxable_income = taxable_data["net_taxable_income"]
        gross_federal_tax = self.calculate_gross_bracket_tax(taxable_income)
        marginal_rate = self.get_marginal_rate(taxable_income)

        # 1. Base Non-Refundable Credits (multiplied by 14.0% lowest federal rate)
        bpa_amount = self._calculate_federal_bpa(taxable_income)
        canada_employment_amount = min(
            raw_taxable["employment_income"],
            self._rules["canada_employment_amount_max"],
        )
        cpp_ei_paid = raw_credits["cpp_qpp_ei_paid"]
        tuition_fees = raw_credits["tuition_fees"]
        claimable_medical = self.calculate_claimable_medical_expenses(
            raw_credits["medical_expenses"], taxable_income
        )

        base_credit_base = (
            bpa_amount
            + canada_employment_amount
            + cpp_ei_paid
            + tuition_fees
            + claimable_medical
        )
        base_non_refundable_credits = round(base_credit_base * self._lowest_rate, 2)

        # 2. Charitable Donation Credit
        donation_credit = self._calculate_donation_credit(
            raw_credits["charitable_donations"], taxable_income
        )

        # 3. Federal Dividend Tax Credits
        eligible_div_credit = round(
            taxable_data["grossed_up_eligible_dividends"]
            * self._taxability_rules["eligible_dividend_fed_credit_rate"],
            2,
        )
        non_eligible_div_credit = round(
            taxable_data["grossed_up_non_eligible_dividends"]
            * self._taxability_rules["non_eligible_dividend_fed_credit_rate"],
            2,
        )
        total_dividend_credit = round(eligible_div_credit + non_eligible_div_credit, 2)

        total_credits = round(
            base_non_refundable_credits + donation_credit + total_dividend_credit, 2
        )

        # Basic Federal Tax cannot go below $0
        basic_federal_tax = round(max(0.0, gross_federal_tax - total_credits), 2)

        # 4. Quebec Abatement (16.5% reduction of Basic Federal Tax for QC residents)
        quebec_abatement = 0.0
        if province_code == "QC":
            quebec_abatement = round(
                basic_federal_tax * self._rules["quebec_abatement_rate"], 2
            )

        net_federal_tax = round(max(0.0, basic_federal_tax - quebec_abatement), 2)

        return {
            "gross_bracket_tax": gross_federal_tax,
            "federal_bpa_claimed": bpa_amount,
            "base_non_refundable_credits": base_non_refundable_credits,
            "donation_credit": donation_credit,
            "dividend_tax_credit": total_dividend_credit,
            "total_credits_applied": total_credits,
            "basic_federal_tax": basic_federal_tax,
            "quebec_abatement": quebec_abatement,
            "net_federal_tax": net_federal_tax,
            "federal_marginal_rate": round(marginal_rate * 100, 2),
        }
