import { useState, useRef } from 'react';
import { uploadReport } from '../api';

export default function UploadReport() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef();

  const handleFile = (f) => {
    if (f && f.name.toLowerCase().endsWith('.pdf')) {
      setFile(f);
      setError('');
    } else {
      setError('Only PDF files are accepted.');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await uploadReport(file);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>📄 Upload Financial Report</h2>
        <p>Upload a PDF to extract text, tables, and identify financial terms</p>
      </div>

      <div className="card mb-6">
        <div
          className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFile(e.dataTransfer.files[0]);
          }}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            style={{ display: 'none' }}
            onChange={(e) => handleFile(e.target.files[0])}
          />
          <div className="upload-icon">📁</div>
          <h3>{file ? file.name : 'Drop your PDF here or click to browse'}</h3>
          <p>{file ? `${(file.size / 1024).toFixed(1)} KB selected` : 'Supports .pdf financial reports'}</p>
        </div>

        {error && (
          <div className="alert alert-error mt-4">
            <span className="alert-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div style={{ marginTop: 20, display: 'flex', gap: 12 }}>
          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading && <span className="spinner" />}
            {loading ? 'Processing...' : 'Upload & Extract'}
          </button>
          {file && (
            <button
              className="btn btn-secondary"
              onClick={() => { setFile(null); setResult(null); setError(''); }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {result && (
        <div className="fade-in">
          <div className="stats-grid">
            <div className="card stat-card blue">
              <div className="card-title">Pages</div>
              <div className="card-value" style={{ color: 'var(--accent-blue)' }}>{result.pages}</div>
            </div>
            <div className="card stat-card green">
              <div className="card-title">Financial Terms Found</div>
              <div className="card-value" style={{ color: 'var(--accent-green)' }}>{result.summary?.total_financial_terms || 0}</div>
            </div>
            <div className="card stat-card cyan">
              <div className="card-title">Tables Found</div>
              <div className="card-value" style={{ color: 'var(--accent-cyan)' }}>{result.summary?.total_tables || 0}</div>
            </div>
          </div>

          {result.financial_terms && result.financial_terms.length > 0 && (
            <div className="card mb-6">
              <div className="card-title">Identified Financial Terms</div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Term</th>
                    <th>Matched Phrase</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {result.financial_terms.map((t, i) => (
                    <tr key={i}>
                      <td><span className="badge badge-blue">{t.term}</span></td>
                      <td>{t.matched_phrase}</td>
                      <td><strong>{t.value || '—'}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="card">
            <div className="card-title">Extracted Text</div>
            <pre style={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              color: 'var(--text-secondary)',
              fontSize: '0.82rem',
              lineHeight: 1.7,
              maxHeight: 400,
              overflow: 'auto',
              padding: 16,
              background: 'rgba(0,0,0,0.2)',
              borderRadius: 'var(--radius-sm)',
            }}>
              {result.extracted_text || 'No text extracted.'}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
