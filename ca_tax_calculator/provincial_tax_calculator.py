from typing import Dict, Any
from canadian_tax_data import CanadianTaxData
from tax_calculator import TaxCalculator


class ProvincialTaxCalculator(TaxCalculator):
    """
    Computes 2026 Provincial or Territorial Income Tax for all 13 Canadian
    jurisdictions, including progressive brackets, BPA phase-outs (MB, YT),
    provincial non-refundable credits, dividend credits, and Ontario surtaxes.
    """

    # 2026 Provincial/Territorial Dividend Tax Credit rates (% of grossed-up dividend)
    PROVINCIAL_DIVIDEND_RATES: Dict[str, Dict[str, float]] = {
        "AB": {"eligible": 0.0812, "non_eligible": 0.0218},
        "BC": {"eligible": 0.1200, "non_eligible": 0.0196},
        "MB": {"eligible": 0.0800, "non_eligible": 0.007835},
        "NB": {"eligible": 0.1400, "non_eligible": 0.0275},
        "NL": {"eligible": 0.0630, "non_eligible": 0.0320},
        "NS": {"eligible": 0.0885, "non_eligible": 0.0150},
        "NT": {"eligible": 0.1150, "non_eligible": 0.0600},
        "NU": {"eligible": 0.0551, "non_eligible": 0.0261},
        "ON": {"eligible": 0.1000, "non_eligible": 0.029863},
        "PE": {"eligible": 0.1050, "non_eligible": 0.0130},
        "QC": {"eligible": 0.1170, "non_eligible": 0.0342},
        "SK": {"eligible": 0.1100, "non_eligible": 0.02105},
        "YT": {"eligible": 0.1202, "non_eligible": 0.0067},
    }

    def __init__(self, province_code: str) -> None:
        self._province_code: str = CanadianTaxData.resolve_jurisdiction(province_code)
        self._config: Dict[str, Any] = CanadianTaxData.get_provincial_config(self._province_code)
        super().__init__(
            brackets=self._config["brackets"],
            lowest_rate=self._config["lowest_rate"],
        )

    @property
    def province_code(self) -> str:
        return self._province_code

    @property
    def province_name(self) -> str:
        return self._config["name"]

    def _calculate_provincial_bpa(self, net_income: float) -> float:
        """
        Calculates the provincial/territorial Basic Personal Amount,
        accounting for Manitoba's $200k-$400k phase-out and Yukon's Federal-mirrored clawback.
        """
        base_bpa: float = self._config["bpa"]

        if self._province_code == "MB":
            start = self._config["bpa_clawback_start"]  # $200,000
            end = self._config["bpa_clawback_end"]      # $400,000
            if net_income <= start:
                return base_bpa
            if net_income >= end:
                return 0.0
            ratio = (net_income - start) / (end - start)
            return round(base_bpa * (1.0 - ratio), 2)

        if self._province_code == "YT":
            fed_rules = CanadianTaxData.FEDERAL_RULES
            start = fed_rules["bpa_clawback_start"]  # $181,440
            end = fed_rules["bpa_clawback_end"]      # $258,482
            bpa_min = fed_rules["bpa_min"]           # $14,829
            if net_income <= start:
                return base_bpa
            if net_income >= end:
                return bpa_min
            ratio = (net_income - start) / (end - start)
            return round(base_bpa - (base_bpa - bpa_min) * ratio, 2)

        return base_bpa

    def _calculate_provincial_donation_credit(self, donations: float) -> float:
        """
        Computes provincial/territorial charitable donation tax credit:
        - Lowest bracket rate on the first $200
        - Top provincial bracket rate on amounts exceeding $200
        """
        if donations <= 0:
            return 0.0

        top_rate: float = self._brackets[-1][1]
        if donations <= 200.0:
            return round(donations * self._lowest_rate, 2)

        first_200 = 200.0 * self._lowest_rate
        excess = (donations - 200.0) * top_rate
        return round(first_200 + excess, 2)

    def _calculate_surtax(self, basic_provincial_tax: float) -> float:
        """
        Computes provincial surtax where applicable (currently Ontario's
        two-tier surtax on basic provincial tax payable).
        """
        surtax_cfg = self._config.get("surtax")
        if not surtax_cfg or basic_provincial_tax <= 0:
            return 0.0

        surtax = 0.0
        t1 = surtax_cfg["tier1_threshold"]
        t2 = surtax_cfg["tier2_threshold"]

        if basic_provincial_tax > t1:
            surtax += (basic_provincial_tax - t1) * surtax_cfg["tier1_rate"]
        if basic_provincial_tax > t2:
            surtax += (basic_provincial_tax - t2) * surtax_cfg["tier2_rate"]

        return round(surtax, 2)

    def calculate_tax(self, tax_profile: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculates the complete 2026 Provincial/Territorial Tax breakdown
        from the structured User tax profile.
        """
        taxable_data: Dict[str, float] = tax_profile["taxable"]
        raw_taxable: Dict[str, float] = tax_profile["details"]["taxable_sources_raw"]
        raw_credits: Dict[str, float] = tax_profile["details"]["tax_credit_inputs_raw"]

        taxable_income = taxable_data["net_taxable_income"]
        gross_prov_tax = self.calculate_gross_bracket_tax(taxable_income)
        marginal_rate = self.get_marginal_rate(taxable_income)

        # 1. Base Non-Refundable Credits
        bpa_amount = self._calculate_provincial_bpa(taxable_income)
        cpp_ei_paid = raw_credits["cpp_qpp_ei_paid"]
        claimable_medical = self.calculate_claimable_medical_expenses(
            raw_credits["medical_expenses"], taxable_income
        )

        # Yukon also grants the Canada Employment Amount ($1,501) territorially
        yt_employment_credit = 0.0
        if self._province_code == "YT":
            yt_employment_credit = min(
                raw_taxable["employment_income"],
                CanadianTaxData.FEDERAL_RULES["canada_employment_amount_max"],
            )

        # Quebec (Revenu Québec) does not grant a separate tuition credit at 14% in the same T1 schedule;
        # other provinces allow tuition at the lowest rate (simplified here for non-QC jurisdictions)
        tuition_credit_base = 0.0 if self._province_code == "QC" else raw_credits["tuition_fees"]

        base_credit_pool = (
            bpa_amount
            + cpp_ei_paid
            + claimable_medical
            + yt_employment_credit
            + tuition_credit_base
        )
        base_non_refundable_credits = round(base_credit_pool * self._lowest_rate, 2)

        # 2. Provincial Charitable Donation Credit
        donation_credit = self._calculate_provincial_donation_credit(
            raw_credits["charitable_donations"]
        )

        # 3. Provincial Dividend Tax Credits
        div_rates = self.PROVINCIAL_DIVIDEND_RATES[self._province_code]
        eligible_div_credit = round(
            taxable_data["grossed_up_eligible_dividends"] * div_rates["eligible"], 2
        )
        non_eligible_div_credit = round(
            taxable_data["grossed_up_non_eligible_dividends"] * div_rates["non_eligible"], 2
        )
        total_dividend_credit = round(eligible_div_credit + non_eligible_div_credit, 2)

        total_credits = round(
            base_non_refundable_credits + donation_credit + total_dividend_credit, 2
        )

        # Basic Provincial Tax (before surtax)
        basic_provincial_tax = round(max(0.0, gross_prov_tax - total_credits), 2)

        # 4. Provincial Surtax (e.g., Ontario)
        surtax_amount = self._calculate_surtax(basic_provincial_tax)

        net_provincial_tax = round(basic_provincial_tax + surtax_amount, 2)

        # Effective top marginal rate including Ontario surtax tiers if applicable
        effective_marginal_rate = marginal_rate
        if self._province_code == "ON" and basic_provincial_tax > 7446.00:
            effective_marginal_rate = round(marginal_rate * 1.56, 4)
        elif self._province_code == "ON" and basic_provincial_tax > 5818.00:
            effective_marginal_rate = round(marginal_rate * 1.20, 4)

        return {
            "province_code": self._province_code,
            "province_name": self.province_name,
            "gross_bracket_tax": gross_prov_tax,
            "provincial_bpa_claimed": bpa_amount,
            "base_non_refundable_credits": base_non_refundable_credits,
            "donation_credit": donation_credit,
            "dividend_tax_credit": total_dividend_credit,
            "total_credits_applied": total_credits,
            "basic_provincial_tax": basic_provincial_tax,
            "surtax": surtax_amount,
            "net_provincial_tax": net_provincial_tax,
            "provincial_marginal_rate": round(effective_marginal_rate * 100, 2),
        }
