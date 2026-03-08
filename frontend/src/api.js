/**
 * CreditMind API client
 * Centralized fetch wrapper for all backend API calls.
 */

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Upload a PDF financial report.
 * @param {File} file
 * @returns {Promise<object>}
 */
export async function uploadReport(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/upload-report`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }

  return res.json();
}

/**
 * Analyze company financials.
 * @param {object} financials
 * @returns {Promise<object>}
 */
export async function analyzeCompany(financials) {
  const res = await fetch(`${API_BASE}/analyze-company`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(financials),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Analysis failed (${res.status})`);
  }

  return res.json();
}

/**
 * Get risk score for a company.
 * @param {string} companyName
 * @returns {Promise<object>}
 */
export async function getRiskScore(companyName) {
  const res = await fetch(
    `${API_BASE}/risk-score?company_name=${encodeURIComponent(companyName)}`
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Risk score fetch failed (${res.status})`);
  }

  return res.json();
}

/**
 * Generate a Credit Approval Memorandum.
 * @param {string} companyName
 * @returns {Promise<object>}
 */
export async function generateCam(companyName) {
  const res = await fetch(
    `${API_BASE}/generate-cam?company_name=${encodeURIComponent(companyName)}`
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `CAM generation failed (${res.status})`);
  }

  return res.json();
}
