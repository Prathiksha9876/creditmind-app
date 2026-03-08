"""
Enhanced PDF text extraction service for CreditMind.

Uses pdfplumber for:
  - Full text extraction per page
  - Table detection and extraction
  - Financial term identification (revenue, debt, profit, etc.)

Returns a structured JSON result ready for downstream analysis.
"""

import re
from io import BytesIO
from typing import Optional

import pdfplumber


# ── Financial term patterns ──────────────────────────────────────────────────
# Each entry: (canonical_label, compiled regex)
FINANCIAL_TERMS = [
    ("revenue",             re.compile(r"\b(revenue|total\s+revenue|net\s+revenue|gross\s+revenue|sales|total\s+sales|turnover)\b", re.I)),
    ("net_income",          re.compile(r"\b(net\s+income|net\s+profit|net\s+earnings|profit\s+after\s+tax|pat)\b", re.I)),
    ("gross_profit",        re.compile(r"\b(gross\s+profit|gross\s+margin)\b", re.I)),
    ("operating_income",    re.compile(r"\b(operating\s+income|operating\s+profit|ebit)\b", re.I)),
    ("ebitda",              re.compile(r"\b(ebitda)\b", re.I)),
    ("total_assets",        re.compile(r"\b(total\s+assets)\b", re.I)),
    ("total_liabilities",   re.compile(r"\b(total\s+liabilities|total\s+debt)\b", re.I)),
    ("equity",              re.compile(r"\b(total\s+equity|shareholders?\s+equity|stockholders?\s+equity|net\s+worth)\b", re.I)),
    ("current_assets",      re.compile(r"\b(current\s+assets)\b", re.I)),
    ("current_liabilities", re.compile(r"\b(current\s+liabilities)\b", re.I)),
    ("long_term_debt",      re.compile(r"\b(long[\s-]term\s+debt|non[\s-]current\s+liabilities)\b", re.I)),
    ("interest_expense",    re.compile(r"\b(interest\s+expense|finance\s+cost|interest\s+payable)\b", re.I)),
    ("depreciation",        re.compile(r"\b(depreciation|amortization|depreciation\s+and\s+amortization)\b", re.I)),
    ("cash_flow",           re.compile(r"\b(cash\s+flow|operating\s+cash\s+flow|free\s+cash\s+flow|cash\s+from\s+operations)\b", re.I)),
    ("retained_earnings",   re.compile(r"\b(retained\s+earnings)\b", re.I)),
    ("dividends",           re.compile(r"\b(dividends?\s+paid|dividend\s+per\s+share)\b", re.I)),
    ("cost_of_goods_sold",  re.compile(r"\b(cost\s+of\s+(goods\s+sold|revenue|sales)|cogs)\b", re.I)),
    ("tax",                 re.compile(r"\b(income\s+tax|tax\s+expense|provision\s+for\s+tax)\b", re.I)),
    ("working_capital",     re.compile(r"\b(working\s+capital)\b", re.I)),
    ("debt_to_equity",      re.compile(r"\b(debt[\s-]to[\s-]equity)\b", re.I)),
    ("return_on_equity",    re.compile(r"\b(return\s+on\s+equity|roe)\b", re.I)),
    ("return_on_assets",    re.compile(r"\b(return\s+on\s+assets|roa)\b", re.I)),
    ("earnings_per_share",  re.compile(r"\b(earnings?\s+per\s+share|eps)\b", re.I)),
]

# Regex to match currency-style numbers (e.g. 1,234.56 or $1,234,567)
_NUMBER_RE = re.compile(r"[\$₹€£]?\s*[\d,]+\.?\d*")


def _identify_financial_terms(text: str) -> list[dict]:
    """
    Scan text for known financial terms and try to capture the
    associated numeric value on the same line.

    Returns a list of dicts:
        { "term": str, "matched_phrase": str, "value": str | None, "line": str }
    """
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        for label, pattern in FINANCIAL_TERMS:
            match = pattern.search(stripped)
            if match:
                # Try to grab the first number on this line
                numbers = _NUMBER_RE.findall(stripped)
                value = numbers[-1].strip() if numbers else None

                key = (label, value or "")
                if key not in seen:
                    seen.add(key)
                    findings.append({
                        "term": label,
                        "matched_phrase": match.group(0),
                        "value": value,
                        "line": stripped,
                    })

    return findings


def _extract_tables(page) -> list[list[list[Optional[str]]]]:
    """
    Extract all tables from a pdfplumber page object.
    Returns a list of tables, where each table is a list of rows,
    and each row is a list of cell strings (or None).
    """
    tables = page.extract_tables()
    if not tables:
        return []

    cleaned: list[list[list[Optional[str]]]] = []
    for table in tables:
        cleaned_table = []
        for row in table:
            cleaned_row = [cell.strip() if cell else None for cell in row]
            cleaned_table.append(cleaned_row)
        cleaned.append(cleaned_table)

    return cleaned


def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Extract text, tables, and financial terms from a PDF.

    Args:
        pdf_bytes: Raw bytes of the PDF file.

    Returns:
        Structured dict:
        {
            "pages": int,
            "text": str,
            "page_details": [
                { "page_number": int, "text": str, "tables": [...] }
            ],
            "tables": [ ... ],              # all tables across all pages
            "financial_terms": [ ... ],     # identified financial term hits
            "summary": {
                "total_tables": int,
                "total_financial_terms": int,
                "terms_found": [str]
            }
        }
    """
    pdf_file = BytesIO(pdf_bytes)
    all_text_parts: list[str] = []
    page_details: list[dict] = []
    all_tables: list[dict] = []

    with pdfplumber.open(pdf_file) as pdf:
        for idx, page in enumerate(pdf.pages):
            page_num = idx + 1

            # ── Text ──
            page_text = page.extract_text() or ""
            all_text_parts.append(page_text)

            # ── Tables ──
            tables = _extract_tables(page)
            for t_idx, table_data in enumerate(tables):
                all_tables.append({
                    "page": page_num,
                    "table_index": t_idx,
                    "rows": len(table_data),
                    "data": table_data,
                })

            page_details.append({
                "page_number": page_num,
                "text": page_text,
                "tables": tables,
            })

    full_text = "\n".join(all_text_parts)

    # ── Financial term identification ──
    financial_terms = _identify_financial_terms(full_text)

    unique_terms = sorted({item["term"] for item in financial_terms})

    return {
        "pages": len(page_details),
        "text": full_text,
        "page_details": page_details,
        "tables": all_tables,
        "financial_terms": financial_terms,
        "summary": {
            "total_tables": len(all_tables),
            "total_financial_terms": len(financial_terms),
            "terms_found": unique_terms,
        },
    }
