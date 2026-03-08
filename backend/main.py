from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from pdf_service import extract_text_from_pdf
from analysis_service import analyze_company, get_risk_score
from cam_service import generate_cam

app = FastAPI(title="CreditMind API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ────────────────────────────────────────────────────────────
class CompanyFinancials(BaseModel):
    company_name: str
    industry: str
    revenue: float
    expenses: float
    total_assets: float
    total_liabilities: float
    equity: float
    net_income: float
    interest_expense: float
    current_assets: float
    current_liabilities: float
    # Optional fields for enhanced risk scoring
    previous_revenue: Optional[float] = None
    report_text: Optional[str] = ""
    # Optional fields for promoter analysis in CAM
    promoter_name: Optional[str] = None
    promoter_experience_years: Optional[int] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Welcome to CreditMind API", "version": "1.0.0"}


@app.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):
    """
    Upload a PDF financial report and extract its text content.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    contents = await file.read()

    try:
        result = extract_text_from_pdf(contents)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to process PDF: {str(e)}")

    return {
        "filename": file.filename,
        "status": "success",
        "pages": result["pages"],
        "extracted_text": result["text"],
        "tables": result["tables"],
        "financial_terms": result["financial_terms"],
        "summary": result["summary"],
    }


@app.post("/analyze-company")
async def analyze_company_endpoint(financials: CompanyFinancials):
    """
    Analyze a company's financial data — computes ratios and credit risk score.
    Results are stored for later retrieval via /risk-score and /generate-cam.
    """
    result = analyze_company(financials.model_dump())
    # Filter out internal fields from API response
    response = {k: v for k, v in result.items() if not k.startswith("_")}
    return {
        "status": "success",
        **response,
    }


@app.get("/risk-score")
async def risk_score(company_name: str):
    """
    Retrieve the credit risk score for a previously analyzed company.
    """
    result = get_risk_score(company_name)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for '{company_name}'. Run /analyze-company first.",
        )
    return {"status": "success", **result}


@app.get("/generate-cam")
async def generate_cam_endpoint(company_name: str):
    """
    Generate a Credit Approval Memorandum for a previously analyzed company.
    """
    cam = generate_cam(company_name)
    if cam is None:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found for '{company_name}'. Run /analyze-company first.",
        )
    return {"status": "success", **cam}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
