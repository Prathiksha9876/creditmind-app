import { useState } from 'react';
import { generateCam } from '../api';

/**
 * Simple markdown-to-JSX renderer.
 * Handles: headings, tables, bold, lists, hr, blockquote, code, paragraphs.
 */
function renderMarkdown(md) {
  if (!md) return null;

  const lines = md.split('\n');
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Horizontal rule
    if (/^---\s*$/.test(line)) {
      elements.push(<hr key={i} />);
      i++;
      continue;
    }

    // Headings
    if (line.startsWith('### ')) {
      elements.push(<h3 key={i}>{processInline(line.slice(4))}</h3>);
      i++;
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(<h2 key={i}>{processInline(line.slice(3))}</h2>);
      i++;
      continue;
    }
    if (line.startsWith('# ')) {
      elements.push(<h1 key={i}>{processInline(line.slice(2))}</h1>);
      i++;
      continue;
    }

    // Table
    if (line.includes('|') && line.trim().startsWith('|')) {
      const tableLines = [];
      while (i < lines.length && lines[i].includes('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      elements.push(renderTable(tableLines, elements.length));
      continue;
    }

    // Blockquote
    if (line.startsWith('>')) {
      const quoteLines = [];
      while (i < lines.length && lines[i].startsWith('>')) {
        quoteLines.push(lines[i].replace(/^>\s?/, ''));
        i++;
      }
      elements.push(
        <blockquote key={elements.length}>
          {quoteLines.map((ql, qi) => <span key={qi}>{processInline(ql)}<br /></span>)}
        </blockquote>
      );
      continue;
    }

    // Unordered list
    if (line.startsWith('- ')) {
      const listItems = [];
      while (i < lines.length && lines[i].startsWith('- ')) {
        listItems.push(lines[i].slice(2));
        i++;
      }
      elements.push(
        <ul key={elements.length}>
          {listItems.map((li, idx) => <li key={idx}>{processInline(li)}</li>)}
        </ul>
      );
      continue;
    }

    // Empty line
    if (!line.trim()) {
      i++;
      continue;
    }

    // Paragraph
    elements.push(<p key={i}>{processInline(line)}</p>);
    i++;
  }

  return elements;
}

function processInline(text) {
  // Process **bold** and `code`
  const parts = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Bold
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
    // Code
    const codeMatch = remaining.match(/`(.+?)`/);

    let first = null;
    let firstIdx = remaining.length;

    if (boldMatch && boldMatch.index < firstIdx) {
      first = 'bold';
      firstIdx = boldMatch.index;
    }
    if (codeMatch && codeMatch.index < firstIdx) {
      first = 'code';
      firstIdx = codeMatch.index;
    }

    if (!first) {
      parts.push(remaining);
      break;
    }

    if (firstIdx > 0) {
      parts.push(remaining.slice(0, firstIdx));
    }

    if (first === 'bold') {
      parts.push(<strong key={key++}>{boldMatch[1]}</strong>);
      remaining = remaining.slice(firstIdx + boldMatch[0].length);
    } else {
      parts.push(<code key={key++}>{codeMatch[1]}</code>);
      remaining = remaining.slice(firstIdx + codeMatch[0].length);
    }
  }

  return parts;
}

function renderTable(tableLines, key) {
  if (tableLines.length < 2) return null;

  const parseRow = (line) =>
    line.split('|').filter((_, i, arr) => i > 0 && i < arr.length - 1).map(c => c.trim());

  const headers = parseRow(tableLines[0]);
  // Skip separator line (index 1)
  const rows = tableLines.slice(2).map(parseRow);

  return (
    <table key={key}>
      <thead>
        <tr>{headers.map((h, i) => <th key={i}>{processInline(h)}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, ri) => (
          <tr key={ri}>{row.map((cell, ci) => <td key={ci}>{processInline(cell)}</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}


export default function CamReport({ lastAnalyzedCompany }) {
  const [companyName, setCompanyName] = useState(lastAnalyzedCompany || '');
  const [loading, setLoading] = useState(false);
  const [cam, setCam] = useState(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!companyName.trim()) return;
    setLoading(true);
    setError('');
    setCam(null);

    try {
      const data = await generateCam(companyName.trim());
      setCam(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>📋 Credit Approval Memorandum</h2>
        <p>Generate a comprehensive CAM report for an analyzed company</p>
      </div>

      <div className="card mb-6">
        <div className="card-title">Generate Report</div>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>Company Name</label>
            <input
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Enter the company name you analyzed..."
              onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={!companyName.trim() || loading}
            style={{ marginBottom: 0, height: 42 }}
          >
            {loading && <span className="spinner" />}
            {loading ? 'Generating...' : '📋 Generate CAM'}
          </button>
        </div>

        {error && (
          <div className="alert alert-error mt-4">
            <span className="alert-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}
      </div>

      {cam && (
        <div className="card fade-in">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div className="card-title" style={{ margin: 0 }}>Generated Memorandum</div>
            <span className="badge badge-green">
              {cam.sections?.credit_recommendation?.decision || 'N/A'}
            </span>
          </div>
          <div className="cam-markdown">
            {renderMarkdown(cam.cam_markdown)}
          </div>
        </div>
      )}
    </div>
  );
}
