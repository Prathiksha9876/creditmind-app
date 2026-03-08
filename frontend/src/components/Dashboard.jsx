import { useState } from 'react';

export default function Dashboard() {
  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>📊 Dashboard</h2>
        <p>Welcome to CreditMind — AI-Powered Credit Analysis Platform</p>
      </div>

      <div className="stats-grid">
        <div className="card stat-card blue">
          <div className="stat-icon">📄</div>
          <div className="card-title">Upload Reports</div>
          <div className="card-value" style={{ color: 'var(--accent-blue)' }}>PDF</div>
          <div className="card-subtitle">Extract financial data from reports</div>
        </div>

        <div className="card stat-card cyan">
          <div className="stat-icon">🔍</div>
          <div className="card-title">Analyze Companies</div>
          <div className="card-value" style={{ color: 'var(--accent-cyan)' }}>5 Ratios</div>
          <div className="card-subtitle">Current, D/E, NPM, ROA, ICR</div>
        </div>

        <div className="card stat-card green">
          <div className="stat-icon">📈</div>
          <div className="card-title">Risk Scoring</div>
          <div className="card-value" style={{ color: 'var(--accent-green)' }}>0–100</div>
          <div className="card-subtitle">Four-factor credit risk model</div>
        </div>

        <div className="card stat-card purple">
          <div className="stat-icon">📋</div>
          <div className="card-title">CAM Reports</div>
          <div className="card-value" style={{ color: 'var(--accent-purple)' }}>5 Sections</div>
          <div className="card-subtitle">Auto-generated memorandums</div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-title">How It Works</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[
              { step: '1', icon: '📄', title: 'Upload Report', desc: 'Upload a PDF financial report to extract text and financial terms automatically.' },
              { step: '2', icon: '🔢', title: 'Enter Financials', desc: 'Input company financial data — revenue, assets, liabilities, equity, and more.' },
              { step: '3', icon: '⚡', title: 'Get Risk Score', desc: 'Our model computes ratios and produces a 0–100 credit score with letter grade.' },
              { step: '4', icon: '📋', title: 'Generate CAM', desc: 'Auto-generate a full Credit Approval Memorandum with recommendation.' },
            ].map((item) => (
              <div key={item.step} style={{ display: 'flex', gap: '14px', alignItems: 'flex-start' }}>
                <div style={{
                  width: 36, height: 36, borderRadius: '50%',
                  background: 'rgba(59, 130, 246, 0.12)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1rem', flexShrink: 0
                }}>
                  {item.icon}
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 2 }}>{item.title}</div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '0.82rem' }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Credit Grade Scale</div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Grade</th>
                <th>Score Range</th>
                <th>Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {[
                { grade: 'AAA', range: '90 – 100', risk: 'Very Low Risk', badge: 'badge-green' },
                { grade: 'AA', range: '80 – 89', risk: 'Low Risk', badge: 'badge-green' },
                { grade: 'A', range: '70 – 79', risk: 'Moderate-Low', badge: 'badge-blue' },
                { grade: 'BBB', range: '60 – 69', risk: 'Moderate', badge: 'badge-blue' },
                { grade: 'BB', range: '50 – 59', risk: 'Moderate-High', badge: 'badge-amber' },
                { grade: 'B', range: '40 – 49', risk: 'High Risk', badge: 'badge-amber' },
                { grade: 'CCC', range: '30 – 39', risk: 'Very High', badge: 'badge-red' },
                { grade: 'D', range: '0 – 29', risk: 'Extreme', badge: 'badge-red' },
              ].map((row) => (
                <tr key={row.grade}>
                  <td><strong>{row.grade}</strong></td>
                  <td>{row.range}</td>
                  <td><span className={`badge ${row.badge}`}>{row.risk}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
