import unicodedata
from typing import Dict, List, Tuple, Any


class CanadianTaxData:
    """
    Central repository for 2026 Canadian Federal, Provincial, and Territorial
    tax brackets, Basic Personal Amounts (BPA), surtaxes, credits, and income rules.
    """

    TAX_YEAR: int = 2026

    # Maps normalized user inputs (codes and full names) to official 2-letter postal codes
    JURISDICTION_ALIASES: Dict[str, str] = {
        "AB": "AB", "ALBERTA": "AB",
        "BC": "BC", "BRITISH COLUMBIA": "BC",
        "MB": "MB", "MANITOBA": "MB",
        "NB": "NB", "NEW BRUNSWICK": "NB",
        "NL": "NL", "NEWFOUNDLAND AND LABRADOR": "NL", "NEWFOUNDLAND": "NL",
        "NS": "NS", "NOVA SCOTIA": "NS",
        "NT": "NT", "NORTHWEST TERRITORIES": "NT", "NWT": "NT",
        "NU": "NU", "NUNAVUT": "NU",
        "ON": "ON", "ONTARIO": "ON",
        "PE": "PE", "PEI": "PE", "PRINCE EDWARD ISLAND": "PE",
        "QC": "QC", "QUEBEC": "QC",
        "SK": "SK", "SASKATCHEWAN": "SK",
        "YT": "YT", "YUKON": "YT", "YUKON TERRITORY": "YT",
    }

    JURISDICTION_NAMES: Dict[str, str] = {
        "AB": "Alberta",
        "BC": "British Columbia",
        "MB": "Manitoba",
        "NB": "New Brunswick",
        "NL": "Newfoundland and Labrador",
        "NS": "Nova Scotia",
        "NT": "Northwest Territories",
        "NU": "Nunavut",
        "ON": "Ontario",
        "PE": "Prince Edward Island",
        "QC": "Quebec",
        "SK": "Saskatchewan",
        "YT": "Yukon",
    }

    # 2026 Federal Tax Brackets: (upper_threshold, marginal_rate)
    FEDERAL_BRACKETS: List[Tuple[float, float]] = [
        (58523.00, 0.140),
        (117045.00, 0.205),
        (181440.00, 0.260),
        (258482.00, 0.290),
        (float("inf"), 0.330),
    ]

    # 2026 Federal Credits & Reliefs
    FEDERAL_RULES: Dict[str, Any] = {
        "lowest_rate": 0.140,
        "bpa_max": 16452.00,              # For net income <= $181,440
        "bpa_min": 14829.00,              # For net income >= $258,482
        "bpa_clawback_start": 181440.00,
        "bpa_clawback_end": 258482.00,
        "canada_employment_amount_max": 1501.00,
        "quebec_abatement_rate": 0.165,   # 16.5% reduction of basic federal tax for QC residents
        "donation_rate_low": 0.140,       # First $200
        "donation_rate_high": 0.290,      # Over $200 (33% if taxable income > $258,482)
        "donation_rate_top": 0.330,
    }

    # 2026 Provincial & Territorial Tax Brackets, BPAs, and Special Rules
    PROVINCIAL_DATA: Dict[str, Dict[str, Any]] = {
        "AB": {
            "name": "Alberta",
            "brackets": [
                (61200.00, 0.080),
                (154259.00, 0.100),
                (185111.00, 0.120),
                (246813.00, 0.130),
                (370220.00, 0.140),
                (float("inf"), 0.150),
            ],
            "bpa": 22769.00,
            "lowest_rate": 0.080,
            "surtax": None,
        },
        "BC": {
            "name": "British Columbia",
            "brackets": [
                (50363.00, 0.056),
                (100728.00, 0.077),
                (115648.00, 0.105),
                (140430.00, 0.1229),
                (190405.00, 0.147),
                (265545.00, 0.168),
                (float("inf"), 0.205),
            ],
            "bpa": 13216.00,
            "lowest_rate": 0.056,
            "surtax": None,
        },
        "MB": {
            "name": "Manitoba",
            "brackets": [
                (47564.00, 0.108),
                (101200.00, 0.1275),
                (float("inf"), 0.174),
            ],
            "bpa": 15780.00,  # Phases out between $200,000 and $400,000 net income
            "bpa_clawback_start": 200000.00,
            "bpa_clawback_end": 400000.00,
            "lowest_rate": 0.108,
            "surtax": None,
        },
        "NB": {
            "name": "New Brunswick",
            "brackets": [
                (52333.00, 0.094),
                (104666.00, 0.140),
                (193861.00, 0.160),
                (float("inf"), 0.195),
            ],
            "bpa": 13664.00,
            "lowest_rate": 0.094,
            "surtax": None,
        },
        "NL": {
            "name": "Newfoundland and Labrador",
            "brackets": [
                (44678.00, 0.087),
                (89354.00, 0.145),
                (159528.00, 0.158),
                (223340.00, 0.178),
                (285319.00, 0.198),
                (570638.00, 0.208),
                (1141275.00, 0.213),
                (float("inf"), 0.218),
            ],
            "bpa": 13094.00,
            "lowest_rate": 0.087,
            "surtax": None,
        },
        "NS": {
            "name": "Nova Scotia",
            "brackets": [
                (30995.00, 0.0879),
                (61991.00, 0.1495),
                (97417.00, 0.1667),
                (157124.00, 0.175),
                (float("inf"), 0.210),
            ],
            "bpa": 11932.00,
            "lowest_rate": 0.0879,
            "surtax": None,
        },
        "NT": {
            "name": "Northwest Territories",
            "brackets": [
                (53003.00, 0.059),
                (106009.00, 0.086),
                (172346.00, 0.122),
                (float("inf"), 0.1405),
            ],
            "bpa": 18199.00,
            "lowest_rate": 0.059,
            "surtax": None,
        },
        "NU": {
            "name": "Nunavut",
            "brackets": [
                (55801.00, 0.040),
                (111602.00, 0.070),
                (181439.00, 0.090),
                (float("inf"), 0.115),
            ],
            "bpa": 19659.00,
            "lowest_rate": 0.040,
            "surtax": None,
        },
        "ON": {
            "name": "Ontario",
            "brackets": [
                (53891.00, 0.0505),
                (107785.00, 0.0915),
                (150000.00, 0.1116),
                (220000.00, 0.1216),
                (float("inf"), 0.1316),
            ],
            "bpa": 12989.00,
            "lowest_rate": 0.0505,
            # Ontario two-tier surtax on basic Ontario tax payable
            "surtax": {
                "tier1_threshold": 5818.00,
                "tier1_rate": 0.20,
                "tier2_threshold": 7446.00,
                "tier2_rate": 0.36,
            },
        },
        "PE": {
            "name": "Prince Edward Island",
            "brackets": [
                (33928.00, 0.095),
                (65820.00, 0.1347),
                (106890.00, 0.166),
                (142520.00, 0.1762),
                (200000.00, 0.190),
                (float("inf"), 0.200),
            ],
            "bpa": 15000.00,
            "lowest_rate": 0.095,
            "surtax": None,
        },
        "QC": {
            "name": "Quebec",
            "brackets": [
                (54345.00, 0.140),
                (108680.00, 0.190),
                (132245.00, 0.240),
                (float("inf"), 0.2575),
            ],
            "bpa": 18952.00,
            "lowest_rate": 0.140,
            "surtax": None,
        },
        "SK": {
            "name": "Saskatchewan",
            "brackets": [
                (54532.00, 0.105),
                (155805.00, 0.125),
                (float("inf"), 0.145),
            ],
            "bpa": 20381.00,
            "lowest_rate": 0.105,
            "surtax": None,
        },
        "YT": {
            "name": "Yukon",
            "brackets": [
                (58523.00, 0.064),
                (117045.00, 0.090),
                (181440.00, 0.109),
                (500000.00, 0.128),
                (float("inf"), 0.150),
            ],
            "bpa": 16452.00,  # Mirrors Federal BPA (including clawback)
            "lowest_rate": 0.064,
            "surtax": None,
        },
    }

    # Inclusion rates, gross-up rates, and non-taxable rules
    INCOME_TAXABILITY_RULES: Dict[str, Any] = {
        "capital_gains_inclusion_rate": 0.50,        # 50% of capital gains are taxable in 2026
        "eligible_dividend_grossup": 1.38,           # Grossed up by 38%
        "eligible_dividend_fed_credit_rate": 0.150198,
        "non_eligible_dividend_grossup": 1.15,       # Grossed up by 15%
        "non_eligible_dividend_fed_credit_rate": 0.090301,
        "non_taxable_categories": [
            "TFSA Withdrawals & Investment Growth",
            "Primary Residence Capital Gain (Principal Residence Exemption)",
            "Lottery & Windfall Winnings",
            "Inheritances & Gifts",
            "Canada Child Benefit (CCB) & GST/HST Credit",
            "Life Insurance Death Benefits",
        ],
    }

    @classmethod
    def resolve_jurisdiction(cls, user_input: str) -> str:
        """
        Validates and converts a province/territory code or full name
        (case-insensitive, accent-insensitive) into its 2-letter code.
        """
        if not user_input or not isinstance(user_input, str):
            raise ValueError("Province or territory cannot be empty.")

        # Strip accents (e.g., 'Québec' -> 'Quebec') and normalize whitespace
        normalized = unicodedata.normalize("NFKD", user_input.strip())
        ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))
        cleaned = " ".join(ascii_only.upper().split())

        if cleaned in cls.JURISDICTION_ALIASES:
            return cls.JURISDICTION_ALIASES[cleaned]

        raise ValueError(
            f"Unrecognized province or territory: '{user_input}'. "
            "Enter a valid 2-letter code (e.g., ON, BC, QC) or full name."
        )

    @classmethod
    def get_jurisdiction_name(cls, code: str) -> str:
        return cls.JURISDICTION_NAMES[code.upper()]

    @classmethod
    def get_provincial_config(cls, code: str) -> Dict[str, Any]:
        return cls.PROVINCIAL_DATA[code.upper()]
