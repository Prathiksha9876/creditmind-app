import { useState } from 'react';
import Dashboard from './components/Dashboard';
import UploadReport from './components/UploadReport';
import AnalyzeCompany from './components/AnalyzeCompany';
import CamReport from './components/CamReport';

const TABS = [
  { id: 'dashboard',  label: 'Dashboard',       icon: '📊' },
  { id: 'upload',     label: 'Upload Report',   icon: '📄' },
  { id: 'analyze',    label: 'Analyze',         icon: '🔍' },
  { id: 'cam',        label: 'CAM Report',      icon: '📋' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [lastAnalyzedCompany, setLastAnalyzedCompany] = useState('');

  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard />;
      case 'upload':    return <UploadReport />;
      case 'analyze':   return <AnalyzeCompany onAnalyzed={(name) => setLastAnalyzedCompany(name)} />;
      case 'cam':       return <CamReport lastAnalyzedCompany={lastAnalyzedCompany} />;
      default:          return <Dashboard />;
    }
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>💳 CreditMind</h1>
          <p>Credit Analysis Platform</p>
        </div>

        <nav className="sidebar-nav">
          {TABS.map((tab) => (
            <div
              key={tab.id}
              className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="nav-icon">{tab.icon}</span>
              <span>{tab.label}</span>
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <p>CreditMind v1.0.0</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
