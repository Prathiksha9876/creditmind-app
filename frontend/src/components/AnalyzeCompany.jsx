import { useState } from 'react';
import { analyzeCompany } from '../api';

const INITIAL_FORM = {
  company_name: '',
  industry: '',
  revenue: '',
  expenses: '',
  total_assets: '',
  total_liabilities: '',
  equity: '',
  net_income: '',
  interest_expense: '',
  current_assets: '',
  current_liabilities: '',
  previous_revenue: '',
  report_text: '',
  promoter_name: '',
  promoter_experience_years: '',
};

function ScoreGauge({ score, grade, riskLevel }) {
  const color = score >= 80 ? 'var(--accent-green)'
    : score >= 60 ? 'var(--accent-blue)'
    : score >= 40 ? 'var(--accent-amber)'
    : 'var(--accent-red)';

  return (
    <div className="score-gauge">
      <div className="gauge-ring" style={{
        background: `conic-gradient(${color} ${score * 3.6}deg, rgba(148,163,184,0.1) 0deg)`
      }}>
        <div className="gauge-value" style={{ color }}>{score}</div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{grade}</div>
        <div className="gauge-label">{riskLevel}</div>
      </div>
    </div>
  );
}

function FactorBar({ label, score }) {
  const color = score >= 70 ? 'green' : score >= 40 ? 'amber' : 'red';
  return (
    <div style={{ marginBottom: 14 }}>
      <div className="flex justify-between" style={{ marginBottom: 6 }}>
        <span style={{ fontSize: '0.82rem', fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-accent)' }}>{score}</span>
      </div>
      <div className="progress-bar">
        <div className={`progress-fill ${color}`} style={{ width: `${Math.min(score, 100)}%` }} />
      </div>
    </div>
  );
}

export default function AnalyzeCompany({ onAnalyzed }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const payload = {
        ...form,
        revenue: parseFloat(form.revenue) || 0,
        expenses: parseFloat(form.expenses) || 0,
        total_assets: parseFloat(form.total_assets) || 0,
        total_liabilities: parseFloat(form.total_liabilities) || 0,
        equity: parseFloat(form.equity) || 0,
        net_income: parseFloat(form.net_income) || 0,
        interest_expense: parseFloat(form.interest_expense) || 0,
        current_assets: parseFloat(form.current_assets) || 0,
        current_liabilities: parseFloat(form.current_liabilities) || 0,
        previous_revenue: form.previous_revenue ? parseFloat(form.previous_revenue) : null,
        promoter_experience_years: form.promoter_experience_years ? parseInt(form.promoter_experience_years) : null,
        promoter_name: form.promoter_name || null,
        report_text: form.report_text || '',
      };

      const data = await analyzeCompany(payload);
      setResult(data);
      if (onAnalyzed) onAnalyzed(data.company_name);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ratios = result?.financial_ratios;
  const credit = result?.credit_score;
  const enhanced = result?.enhanced_risk_score;
  const factors = enhanced?.factor_scores;

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>🔍 Analyze Company</h2>
        <p>Enter financial data to compute ratios, risk score, and credit grade</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card mb-6">
          <div className="card-title">Company Information</div>
          <div className="form-grid">
            <div className="form-group">
              <label>Company Name *</label>
              <input name="company_name" value={form.company_name} onChange={handleChange} placeholder="e.g. Acme Corp" required />
            </div>
            <div className="form-group">
              <label>Industry *</label>
              <input name="industry" value={form.industry} onChange={handleChange} placeholder="e.g. Manufacturing" required />
            </div>
            <div className="form-group">
              <label>Promoter Name</label>
              <input name="promoter_name" value={form.promoter_name} onChange={handleChange} placeholder="e.g. John Smith" />
            </div>
            <div className="form-group">
              <label>Promoter Experience (Years)</label>
              <input name="promoter_experience_years" type="number" value={form.promoter_experience_years} onChange={handleChange} placeholder="e.g. 15" />
            </div>
          </div>
        </div>

        <div className="card mb-6">
          <div className="card-title">Financial Data ($)</div>
          <div className="form-grid">
            <div className="form-group">
              <label>Revenue *</label>
              <input name="revenue" type="number" value={form.revenue} onChange={handleChange} placeholder="5000000" required />
            </div>
            <div className="form-group">
              <label>Previous Year Revenue</label>
              <input name="previous_revenue" type="number" value={form.previous_revenue} onChange={handleChange} placeholder="4200000" />
            </div>
            <div className="form-group">
              <label>Expenses *</label>
              <input name="expenses" type="number" value={form.expenses} onChange={handleChange} placeholder="3500000" required />
            </div>
            <div className="form-group">
              <label>Net Income *</label>
              <input name="net_income" type="number" value={form.net_income} onChange={handleChange} placeholder="1500000" required />
            </div>
            <div className="form-group">
              <label>Total Assets *</label>
              <input name="total_assets" type="number" value={form.total_assets} onChange={handleChange} placeholder="8000000" required />
            </div>
            <div className="form-group">
              <label>Total Liabilities *</label>
              <input name="total_liabilities" type="number" value={form.total_liabilities} onChange={handleChange} placeholder="3000000" required />
            </div>
            <div className="form-group">
              <label>Equity *</label>
              <input name="equity" type="number" value={form.equity} onChange={handleChange} placeholder="5000000" required />
            </div>
            <div className="form-group">
              <label>Interest Expense *</label>
              <input name="interest_expense" type="number" value={form.interest_expense} onChange={handleChange} placeholder="200000" required />
            </div>
            <div className="form-group">
              <label>Current Assets *</label>
              <input name="current_assets" type="number" value={form.current_assets} onChange={handleChange} placeholder="2000000" required />
            </div>
            <div className="form-group">
              <label>Current Liabilities *</label>
              <input name="current_liabilities" type="number" value={form.current_liabilities} onChange={handleChange} placeholder="1000000" required />
            </div>
          </div>
        </div>

        <div className="card mb-6">
          <div className="card-title">Report Text (Optional — scanned for litigation mentions)</div>
          <div className="form-group">
            <textarea
              name="report_text"
              value={form.report_text}
              onChange={handleChange}
              rows={4}
              placeholder="Paste any report text here. The system will scan for lawsuit, litigation, settlement, and other legal mentions..."
              style={{ width: '100%', resize: 'vertical' }}
            />
          </div>
        </div>

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading && <span className="spinner" />}
          {loading ? 'Analyzing...' : '⚡ Analyze Company'}
        </button>
      </form>

      {result && (
        <div className="fade-in mt-6">
          <div className="alert alert-success mb-6">
            <span className="alert-icon">✅</span>
            <span>Analysis complete for <strong>{result.company_name}</strong> — You can now generate a CAM report from the CAM Report tab.</span>
          </div>

          <div className="grid-2 mb-6">
            <div className="card" style={{ display: 'flex', justifyContent: 'center', padding: 32 }}>
              <div>
                <div className="card-title" style={{ textAlign: 'center' }}>Base Credit Score</div>
                <ScoreGauge score={credit.score} grade={credit.grade} riskLevel={credit.risk_level} />
              </div>
            </div>
            <div className="card" style={{ display: 'flex', justifyContent: 'center', padding: 32 }}>
              <div>
                <div className="card-title" style={{ textAlign: 'center' }}>Enhanced Risk Score</div>
                <ScoreGauge score={enhanced.score} grade={enhanced.grade} riskLevel={enhanced.risk_level} />
              </div>
            </div>
          </div>

          {factors && (
            <div className="card mb-6">
              <div className="card-title">Factor Breakdown (Enhanced Model)</div>
              <div style={{ maxWidth: 500 }}>
                <FactorBar label="Revenue Growth" score={factors.revenue_growth} />
                <FactorBar label="Debt-to-Equity" score={factors.debt_to_equity} />
                <FactorBar label="Profit Margin" score={factors.profit_margin} />
                <FactorBar label="Litigation" score={factors.litigation} />
              </div>
              {enhanced.litigation_count > 0 && (
                <div className="alert alert-warning mt-4">
                  <span className="alert-icon">⚖️</span>
                  <span>{enhanced.litigation_count} litigation/legal mention(s) detected in report text</span>
                </div>
              )}
            </div>
          )}

          <div className="card">
            <div className="card-title">Financial Ratios</div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Ratio</th>
                  <th>Value</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { name: 'Current Ratio', key: 'current_ratio', good: 2.0, higher: true },
                  { name: 'Debt-to-Equity', key: 'debt_to_equity', good: 0.5, higher: false },
                  { name: 'Net Profit Margin', key: 'net_profit_margin', good: 0.15, higher: true },
                  { name: 'Return on Assets', key: 'return_on_assets', good: 0.08, higher: true },
                  { name: 'Interest Coverage', key: 'interest_coverage_ratio', good: 4.0, higher: true },
                ].map((r) => {
                  const val = ratios?.[r.key];
                  const isGood = val != null && (r.higher ? val >= r.good : val <= r.good);
                  return (
                    <tr key={r.key}>
                      <td>{r.name}</td>
                      <td><strong>{val != null ? val.toFixed(2) : 'N/A'}</strong></td>
                      <td>
                        <span className={`badge ${isGood ? 'badge-green' : 'badge-amber'}`}>
                          {isGood ? '✓ Healthy' : '⚠ Watch'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
