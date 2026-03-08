"""
Credit Approval Memorandum (CAM) generation service for CreditMind.

Generates a structured CAM with five sections:
    1. Company Overview
    2. Financial Analysis
    3. Risk Assessment
    4. Promoter Analysis
    5. Credit Recommendation

Supports both JSON and formatted Markdown output.
"""

from datetime import datetime
from typing import Optional

from analysis_service import analysis_store


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_currency(value: float) -> str:
    """Format a number as a currency string (e.g. $1,500,000.00)."""
    if value >= 0:
        return f"${value:,.2f}"
    return f"-${abs(value):,.2f}"


def _ratio_display(value) -> str:
    """Safely format a ratio value for display."""
    if value is None:
        return "N/A"
    return f"{value:.2f}"


def _bar(score: float, width: int = 20) -> str:
    """Render a simple ASCII progress bar for markdown."""
    filled = int(score / 100 * width)
    return f"`{'█' * filled}{'░' * (width - filled)}` {score:.1f}/100"


# ── CAM Generation ────────────────────────────────────────────────────────────

def generate_cam(company_name: str) -> Optional[dict]:
    """
    Generate a Credit Approval Memorandum for the specified company.

    Returns None if no analysis data has been stored for the company.
    Returns a dict with both 'cam_json' (structured data) and
    'cam_markdown' (formatted markdown string).
    """
    entry = analysis_store.get(company_name)
    if not entry:
        return None

    ratios = entry["financial_ratios"]
    credit = entry["credit_score"]
    enhanced = entry.get("enhanced_risk_score", {})
    factor_scores = enhanced.get("factor_scores", {})

    generated_at = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

    # ── Risk alerts ───────────────────────────────────────────────────────
    risk_alerts = []
    if ratios.get("current_ratio") is not None and ratios["current_ratio"] < 1.5:
        risk_alerts.append("Current ratio below healthy threshold of 1.5")
    if ratios.get("debt_to_equity") is not None and ratios["debt_to_equity"] > 1.0:
        risk_alerts.append("Debt-to-equity ratio exceeds 1.0 — elevated leverage")
    if ratios.get("net_profit_margin") is not None and ratios["net_profit_margin"] < 0.05:
        risk_alerts.append("Net profit margin is thin (< 5%)")
    if ratios.get("interest_coverage_ratio") is not None and ratios["interest_coverage_ratio"] < 2.0:
        risk_alerts.append("Interest coverage ratio below 2.0 — debt servicing concern")
    litigation_count = enhanced.get("litigation_count", 0)
    if litigation_count > 0:
        risk_alerts.append(f"{litigation_count} litigation/legal mention(s) detected in report")

    # ── Strengths ─────────────────────────────────────────────────────────
    strengths = []
    if ratios.get("current_ratio") is not None and ratios["current_ratio"] >= 2.0:
        strengths.append("Strong liquidity position")
    if ratios.get("debt_to_equity") is not None and ratios["debt_to_equity"] <= 0.5:
        strengths.append("Conservative capital structure")
    if ratios.get("net_profit_margin") is not None and ratios["net_profit_margin"] >= 0.15:
        strengths.append("Healthy profit margins")
    if ratios.get("return_on_assets") is not None and ratios["return_on_assets"] >= 0.08:
        strengths.append("Efficient asset utilisation")
    if ratios.get("interest_coverage_ratio") is not None and ratios["interest_coverage_ratio"] >= 4.0:
        strengths.append("Comfortable debt servicing capacity")
    if factor_scores.get("revenue_growth", 0) >= 70:
        strengths.append("Strong revenue growth trajectory")

    # ── Recommendation ────────────────────────────────────────────────────
    score = enhanced.get("score", credit.get("score", 0))
    grade = enhanced.get("grade", credit.get("grade", "N/A"))

    if score >= 70:
        decision = "APPROVE"
        decision_detail = (
            f"{company_name} demonstrates solid financial health with a credit score of "
            f"{score} ({grade}). The company is recommended for credit approval with "
            f"standard terms and conditions."
        )
    elif score >= 50:
        decision = "CONDITIONAL APPROVE"
        decision_detail = (
            f"{company_name} shows moderate financial health with a credit score of "
            f"{score} ({grade}). Approval is recommended subject to enhanced monitoring, "
            f"additional collateral, and periodic financial review covenants."
        )
    else:
        decision = "DECLINE"
        decision_detail = (
            f"{company_name} presents elevated credit risk with a score of {score} "
            f"({grade}). The application is not recommended for approval at this time. "
            f"Re-evaluation may be considered after material improvement in financials."
        )

    # ── Promoter info (from stored raw data if available) ─────────────────
    raw_data = entry.get("_raw_data", {})
    promoter_name = raw_data.get("promoter_name") or "Not provided"
    promoter_exp = raw_data.get("promoter_experience_years")

    # ─────────────────────────────────────────────────────────────────────
    # Build structured JSON
    # ─────────────────────────────────────────────────────────────────────
    cam_json = {
        "title": "Credit Approval Memorandum",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "sections": {
            "company_overview": {
                "company_name": company_name,
                "industry": entry["industry"],
            },
            "financial_analysis": {
                "ratios": ratios,
                "credit_score": credit["score"],
                "credit_grade": credit["grade"],
                "risk_level": credit["risk_level"],
            },
            "risk_assessment": {
                "enhanced_score": enhanced.get("score"),
                "enhanced_grade": enhanced.get("grade"),
                "factor_scores": factor_scores,
                "risk_alerts": risk_alerts if risk_alerts else ["No significant risk alerts"],
                "strengths": strengths if strengths else ["No outstanding strengths identified"],
                "litigation_mentions": litigation_count,
            },
            "promoter_analysis": {
                "promoter_name": promoter_name,
                "experience_years": promoter_exp,
            },
            "credit_recommendation": {
                "decision": decision,
                "detail": decision_detail,
            },
        },
    }

    # ─────────────────────────────────────────────────────────────────────
    # Build formatted Markdown
    # ─────────────────────────────────────────────────────────────────────
    risk_alerts_md = "\n".join(f"- ⚠️ {a}" for a in risk_alerts) if risk_alerts else "- ✅ No significant risk alerts"
    strengths_md = "\n".join(f"- ✅ {s}" for s in strengths) if strengths else "- No outstanding strengths identified"

    promoter_exp_str = f"{promoter_exp} years" if promoter_exp else "Not provided"

    # Factor score bars
    rg_bar = _bar(factor_scores.get("revenue_growth", 50))
    de_bar = _bar(factor_scores.get("debt_to_equity", 50))
    pm_bar = _bar(factor_scores.get("profit_margin", 50))
    lt_bar = _bar(factor_scores.get("litigation", 100))

    decision_emoji = {"APPROVE": "✅", "CONDITIONAL APPROVE": "⚠️", "DECLINE": "❌"}.get(decision, "")

    cam_markdown = f"""# 📋 Credit Approval Memorandum

**Company:** {company_name}  
**Industry:** {entry["industry"]}  
**Generated:** {generated_at}

---

## 1. Company Overview

| Field | Value |
|-------|-------|
| **Company Name** | {company_name} |
| **Industry** | {entry["industry"]} |
| **Credit Grade** | **{grade}** |
| **Risk Level** | {enhanced.get("risk_level", credit.get("risk_level", "N/A"))} |

---

## 2. Financial Analysis

### Key Financial Ratios

| Ratio | Value | Benchmark |
|-------|------:|-----------|
| Current Ratio | {_ratio_display(ratios.get("current_ratio"))} | ≥ 2.0 (healthy) |
| Debt-to-Equity | {_ratio_display(ratios.get("debt_to_equity"))} | ≤ 0.5 (conservative) |
| Net Profit Margin | {_ratio_display(ratios.get("net_profit_margin"))} | ≥ 0.15 (healthy) |
| Return on Assets | {_ratio_display(ratios.get("return_on_assets"))} | ≥ 0.08 (efficient) |
| Interest Coverage | {_ratio_display(ratios.get("interest_coverage_ratio"))} | ≥ 4.0 (comfortable) |

### Credit Score

- **Base Score:** {credit["score"]} / 100 ({credit["grade"]})
- **Enhanced Score:** {enhanced.get("score", "N/A")} / 100 ({enhanced.get("grade", "N/A")})

---

## 3. Risk Assessment

### Factor Scores (Enhanced Model)

| Factor | Score | Bar |
|--------|------:|-----|
| Revenue Growth | {factor_scores.get("revenue_growth", "N/A")} | {rg_bar} |
| Debt-to-Equity | {factor_scores.get("debt_to_equity", "N/A")} | {de_bar} |
| Profit Margin | {factor_scores.get("profit_margin", "N/A")} | {pm_bar} |
| Litigation | {factor_scores.get("litigation", "N/A")} | {lt_bar} |

### Risk Alerts

{risk_alerts_md}

### Strengths

{strengths_md}

---

## 4. Promoter Analysis

| Field | Detail |
|-------|--------|
| **Promoter Name** | {promoter_name} |
| **Experience** | {promoter_exp_str} |

> *Promoter analysis is based on self-reported data. Additional due diligence
> (directorship checks, CIBIL reports, background verification) is recommended
> before final credit approval.*

---

## 5. Credit Recommendation

### Decision: {decision_emoji} **{decision}**

{decision_detail}

---

*This Credit Approval Memorandum was auto-generated by CreditMind on {generated_at}.
It is intended as an analytical aid and does not constitute a binding credit decision.*
"""

    return {
        **cam_json,
        "cam_markdown": cam_markdown,
    }
