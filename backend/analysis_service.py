"""
Financial analysis and credit risk scoring service for CreditMind.

Computes key financial ratios from company data and derives a composite
credit risk score (0-100) mapped to a letter grade.
"""

import re
from typing import Optional

# In-memory store: company_name -> analysis result
analysis_store: dict[str, dict] = {}


def calculate_ratios(data: dict) -> dict:
    """
    Calculate key financial ratios.

    Expected keys in `data`:
        revenue, expenses, total_assets, total_liabilities,
        equity, net_income, interest_expense,
        current_assets, current_liabilities

    Returns:
        dict of ratio name -> value (rounded to 2 decimals).
    """
    ratios = {}

    # Current Ratio = Current Assets / Current Liabilities
    current_liabilities = data.get("current_liabilities", 0)
    if current_liabilities > 0:
        ratios["current_ratio"] = round(data["current_assets"] / current_liabilities, 2)
    else:
        ratios["current_ratio"] = None

    # Debt-to-Equity = Total Liabilities / Equity
    equity = data.get("equity", 0)
    if equity > 0:
        ratios["debt_to_equity"] = round(data["total_liabilities"] / equity, 2)
    else:
        ratios["debt_to_equity"] = None

    # Net Profit Margin = Net Income / Revenue
    revenue = data.get("revenue", 0)
    if revenue > 0:
        ratios["net_profit_margin"] = round(data["net_income"] / revenue, 2)
    else:
        ratios["net_profit_margin"] = None

    # Return on Assets = Net Income / Total Assets
    total_assets = data.get("total_assets", 0)
    if total_assets > 0:
        ratios["return_on_assets"] = round(data["net_income"] / total_assets, 2)
    else:
        ratios["return_on_assets"] = None

    # Interest Coverage Ratio = (Revenue - Expenses) / Interest Expense
    interest_expense = data.get("interest_expense", 0)
    if interest_expense > 0:
        operating_income = data["revenue"] - data["expenses"]
        ratios["interest_coverage_ratio"] = round(operating_income / interest_expense, 2)
    else:
        ratios["interest_coverage_ratio"] = None

    return ratios


def _score_ratio(value: Optional[float], ideal: float, weight: float, higher_is_better: bool = True) -> float:
    """Score a single ratio on a 0-100 scale relative to an ideal benchmark."""
    if value is None:
        return 50 * weight  # neutral when data is unavailable

    if higher_is_better:
        score = min(value / ideal, 1.5) / 1.5 * 100
    else:
        # For ratios where lower is better (e.g., debt-to-equity)
        if value <= 0:
            score = 100
        else:
            score = min(ideal / value, 1.5) / 1.5 * 100

    return round(score * weight, 2)


def calculate_credit_score(ratios: dict) -> dict:
    """
    Derive a composite credit risk score (0-100) and letter grade.

    Weights:
        Current Ratio        – 20%
        Debt-to-Equity       – 25%
        Net Profit Margin    – 20%
        Return on Assets     – 15%
        Interest Coverage    – 20%

    Returns:
        dict with score (float), grade (str), and risk_level (str).
    """
    total = 0.0

    total += _score_ratio(ratios.get("current_ratio"), ideal=2.0, weight=0.20, higher_is_better=True)
    total += _score_ratio(ratios.get("debt_to_equity"), ideal=0.5, weight=0.25, higher_is_better=False)
    total += _score_ratio(ratios.get("net_profit_margin"), ideal=0.20, weight=0.20, higher_is_better=True)
    total += _score_ratio(ratios.get("return_on_assets"), ideal=0.10, weight=0.15, higher_is_better=True)
    total += _score_ratio(ratios.get("interest_coverage_ratio"), ideal=5.0, weight=0.20, higher_is_better=True)

    score = round(min(max(total, 0), 100), 2)

    # Map score to letter grade
    if score >= 90:
        grade, risk_level = "AAA", "Very Low Risk"
    elif score >= 80:
        grade, risk_level = "AA", "Low Risk"
    elif score >= 70:
        grade, risk_level = "A", "Moderate-Low Risk"
    elif score >= 60:
        grade, risk_level = "BBB", "Moderate Risk"
    elif score >= 50:
        grade, risk_level = "BB", "Moderate-High Risk"
    elif score >= 40:
        grade, risk_level = "B", "High Risk"
    elif score >= 30:
        grade, risk_level = "CCC", "Very High Risk"
    else:
        grade, risk_level = "D", "Extremely High Risk"

    return {
        "score": score,
        "grade": grade,
        "risk_level": risk_level,
    }


# ── Litigation keyword patterns ───────────────────────────────────────────────
_LITIGATION_PATTERNS = [
    re.compile(r"\b(lawsuit|lawsuits)\b", re.I),
    re.compile(r"\b(litigation|litigations)\b", re.I),
    re.compile(r"\b(legal\s+proceedings?)\b", re.I),
    re.compile(r"\b(arbitration)\b", re.I),
    re.compile(r"\b(regulatory\s+action|regulatory\s+penalty)\b", re.I),
    re.compile(r"\b(class\s+action)\b", re.I),
    re.compile(r"\b(settlement)\b", re.I),
    re.compile(r"\b(injunction)\b", re.I),
    re.compile(r"\b(compliance\s+violation|compliance\s+issue)\b", re.I),
    re.compile(r"\b(fraud\s+allegation|fraud\s+investigation)\b", re.I),
    re.compile(r"\b(SEC\s+investigation|SEC\s+enforcement)\b", re.I),
    re.compile(r"\b(pending\s+claim|legal\s+claim)\b", re.I),
]


def _count_litigation_mentions(text: str) -> int:
    """Count distinct litigation-related mentions in the provided text."""
    if not text:
        return 0
    total = 0
    for pattern in _LITIGATION_PATTERNS:
        total += len(pattern.findall(text))
    return total


def calculate_credit_risk_score(
    revenue_growth: float,
    debt_to_equity: float,
    profit_margin: float,
    report_text: str = "",
) -> dict:
    """
    Calculate a credit risk score (0-100) based on four factors.

    Args:
        revenue_growth:  Year-over-year revenue growth as a decimal
                         (e.g. 0.12 = 12% growth, -0.05 = 5% decline).
        debt_to_equity:  Total liabilities / equity ratio.
        profit_margin:   Net income / revenue as a decimal.
        report_text:     Raw text from a financial report to scan for
                         litigation mentions.

    Returns:
        dict:
            score            (float)  – 0 to 100
            grade            (str)    – AAA to D
            risk_level       (str)    – human-readable risk band
            factor_scores    (dict)   – per-factor breakdown
            litigation_count (int)    – number of litigation mentions found
    """

    # ── 1. Revenue Growth Score (25%) ────────────────────────────────────────
    #   >= 20% growth → 100 | 0% → 50 | <= -20% → 0  (linear)
    rg_score = max(0.0, min(100.0, 50 + (revenue_growth * 250)))

    # ── 2. Debt-to-Equity Score (25%) ────────────────────────────────────────
    #   0.0 → 100 | 1.0 → 60 | >= 3.0 → 0  (inverse linear)
    if debt_to_equity <= 0:
        de_score = 100.0
    elif debt_to_equity >= 3.0:
        de_score = 0.0
    else:
        de_score = max(0.0, 100 - (debt_to_equity * 33.33))

    # ── 3. Profit Margin Score (25%) ─────────────────────────────────────────
    #   >= 30% → 100 | 0% → 30 | <= -20% → 0
    if profit_margin >= 0.30:
        pm_score = 100.0
    elif profit_margin <= -0.20:
        pm_score = 0.0
    else:
        pm_score = max(0.0, min(100.0, 30 + (profit_margin * 233.33)))

    # ── 4. Litigation Score (25%) ────────────────────────────────────────────
    #   0 mentions → 100 | each mention deducts 10 pts, floor at 0
    litigation_count = _count_litigation_mentions(report_text)
    lit_score = max(0.0, 100 - (litigation_count * 10))

    # ── Weighted composite ───────────────────────────────────────────────────
    weights = {
        "revenue_growth": 0.25,
        "debt_to_equity": 0.25,
        "profit_margin":  0.25,
        "litigation":     0.25,
    }

    composite = (
        rg_score * weights["revenue_growth"]
        + de_score * weights["debt_to_equity"]
        + pm_score * weights["profit_margin"]
        + lit_score * weights["litigation"]
    )
    score = round(max(0, min(100, composite)), 2)

    # Map to grade
    if score >= 90:
        grade, risk_level = "AAA", "Very Low Risk"
    elif score >= 80:
        grade, risk_level = "AA", "Low Risk"
    elif score >= 70:
        grade, risk_level = "A", "Moderate-Low Risk"
    elif score >= 60:
        grade, risk_level = "BBB", "Moderate Risk"
    elif score >= 50:
        grade, risk_level = "BB", "Moderate-High Risk"
    elif score >= 40:
        grade, risk_level = "B", "High Risk"
    elif score >= 30:
        grade, risk_level = "CCC", "Very High Risk"
    else:
        grade, risk_level = "D", "Extremely High Risk"

    return {
        "score": score,
        "grade": grade,
        "risk_level": risk_level,
        "factor_scores": {
            "revenue_growth":  round(rg_score, 2),
            "debt_to_equity":  round(de_score, 2),
            "profit_margin":   round(pm_score, 2),
            "litigation":      round(lit_score, 2),
        },
        "litigation_count": litigation_count,
    }


def analyze_company(data: dict) -> dict:
    """
    Full analysis pipeline: compute ratios, derive credit score, and store result.

    Args:
        data: dict containing company_name, industry, and all financial fields.
              Optional extras: previous_revenue, report_text.

    Returns:
        Complete analysis result dict.
    """
    ratios = calculate_ratios(data)
    credit = calculate_credit_score(ratios)

    # Enhanced risk score (uses new four-factor model)
    revenue = data.get("revenue", 0)
    previous_revenue = data.get("previous_revenue", None)
    revenue_growth = 0.0
    if previous_revenue and previous_revenue > 0:
        revenue_growth = (revenue - previous_revenue) / previous_revenue

    debt_to_equity = ratios.get("debt_to_equity") or 0.0
    profit_margin = ratios.get("net_profit_margin") or 0.0
    report_text = data.get("report_text", "")

    enhanced_risk = calculate_credit_risk_score(
        revenue_growth=revenue_growth,
        debt_to_equity=debt_to_equity,
        profit_margin=profit_margin,
        report_text=report_text,
    )

    result = {
        "company_name": data["company_name"],
        "industry": data["industry"],
        "financial_ratios": ratios,
        "credit_score": credit,
        "enhanced_risk_score": enhanced_risk,
        "_raw_data": data,  # pass through for CAM generation
    }

    # Persist in memory for later retrieval
    analysis_store[data["company_name"]] = result
    return result


def get_risk_score(company_name: str) -> Optional[dict]:
    """Retrieve the stored credit score for a company, or None if not found."""
    entry = analysis_store.get(company_name)
    if entry:
        return {
            "company_name": company_name,
            **entry["credit_score"],
        }
    return None
