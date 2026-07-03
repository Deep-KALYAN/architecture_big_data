import React, { useState, useEffect, Component } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { searchCompanies, fetchCompanyProfile } from './store/companySlice';
import axios from 'axios';
// 📊 Import Recharts core layout mechanics
import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';



// 🛡️ Error Boundary Component to prevent the whole page from going blank if a chart fails
class ChartErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    console.error("Chart Error Caught:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ marginTop: '30px', padding: '15px', border: '1px solid #ffcccb', borderRadius: '6px', backgroundColor: '#fff5f5', color: '#cc0000' }}>
          <h4>📈 Financial Performance Chart</h4>
          <p style={{ fontSize: '14px' }}>Could not render chart component. Check browser console logs for bundle issues.</p>
        </div>
      );
    }
    return this.props.children;
  }
}


function App() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [searchTerm, setSearchTerm] = useState(''); // Search query for dropdown filter
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [streamedLogs, setStreamedLogs] = useState([]);


  // -------------------------------
  const [activeDocumentView, setActiveDocumentView] = useState(null);
  // ----------------------------------

  // 📈 New State for Macro-Finance Sector Analytics
  const [globalFinance, setGlobalFinance] = useState({
    total_turnover: 0,
    average_margin: 0,
    market_leader: 'Loading...',
    market_leader_revenue: 0
  });
  const dispatch = useDispatch();
  const { searchResults, selectedProfile, loading } = useSelector((state) => state.company);

  // Fetch Cities AND Cross-Company Global Analytics on load
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/cities')
      .then(res => setCities(res.data))
      .catch(err => console.error("Error loading cities", err));
      
    axios.get('http://127.0.0.1:8000/api/analytics/finance')
      .then(res => setGlobalFinance(res.data))
      .catch(err => console.error("Error loading global finance analytics", err));
  }, [searchResults]); // Updates if search results shift the environment context
  
  // Mock total records calculation for demo (Replace with live selector array totals if applicable)
  const bronzeCount = 1952471;
  const silverCount = 1952471;
  const goldCount = searchResults?.length || 0; 
  const goldStatus = selectedProfile ? "Synced" : "Awaiting Selection";

  // Ambient external light blue glow styling
  const ambientGlowStyle = {
    boxShadow: '0 0 15px rgba(173, 216, 230, 0.6), inset 0 0 10px rgba(173, 216, 230, 0.2)',
    border: '1px solid rgba(135, 206, 250, 0.5)',
    borderRadius: '12px',
    padding: '20px',
    backgroundColor: '#ffffff'
  };

  // 🧮 Currency Formatter Tool
  const formatCurrency = (value) => {
    if (!value) return '0 €';
    if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M €`;
    if (value >= 1000) return `${(value / 1000).toFixed(0)}k €`;
    return `${value} €`;
  };

  // 🏙️ Fetch available cities on component load
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/cities')
      .then(res => setCities(res.data))
      .catch(err => console.error("Error loading cities", err));
  }, []);

  const handleCitySelect = (city) => {
    setSelectedCity(city);
    setSearchTerm(city);
    setIsDropdownOpen(false);
    if (city) {
      dispatch(searchCompanies(city));
    }
  };

  const triggerNotaryStream = (bce) => {
    setStreamedLogs([]);
    const eventSource = new EventSource(`http://127.0.0.1:8000/api/companies/${bce}/statutes/stream`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStreamedLogs((prev) => [...prev, data]);
      if (data.status === 'completed') eventSource.close();
    };
    eventSource.onerror = () => eventSource.close();
  };

  // Filter city values against search query input
  const filteredCities = cities.filter(city => 
    city.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const chartData = selectedProfile?.financials
    ? [...selectedProfile.financials]
        .map((f) => ({
          year: String(f?.year || ''),
          turnover: Number(f?.ca || 0),
          grossMargin: Number(f?.marge_brute || 0),
        }))
        .filter(f => f.year)
        .sort((a, b) => a.year.localeCompare(b.year))
    : [];

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '8px' }}>🇧🇪 Belgium Enterprise Analytics Dashboard </h1>
      
      {/* 🚀 STEP 1: ONE-LINE MULTI-COLOR KPI STATUS BAR */}
      <div style={{ display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '20px', fontSize: '14px', fontWeight: 'bold' }}>
        <span style={{ color: '#cd7f32', backgroundColor: '#fdf5e6', padding: '6px 12px', borderRadius: '20px', border: '1px solid #cd7f32' }}>
          🥉 Bronze: {bronzeCount.toLocaleString()} records
        </span>
        <span style={{ color: '#718096', backgroundColor: '#f7fafc', padding: '6px 12px', borderRadius: '20px', border: '1px solid #cbd5e0' }}>
          🥈 Silver: {silverCount.toLocaleString()} records
        </span>
        <span style={{ color: '#d4af37', backgroundColor: '#fffdf0', padding: '6px 12px', borderRadius: '20px', border: '1px solid #d4af37' }}>
          👑 Gold: {goldCount} active keys 
          {/* | Status: <span style={{ color: selectedProfile ? '#2f855a' : '#c53030' }}>{goldStatus}</span> */}
        </span>
      </div>
      <hr style={{ border: '0', borderTop: '1px solid #e2e8f0', marginBottom: '25px' }} />

      {/* SEARCHABLE CUSTOM DROPDOWN SELECTOR */}
      <section style={{ margin: '20px 0', position: 'relative', width: '350px' }}>
        <label htmlFor="city-search-input" style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#4a5568' }}>
          Filter by Corporate City Hub:
        </label>
        <div style={{ position: 'relative' }}>
          <input 
            id="city-search-input"
            type="text"
            placeholder="Type to search city..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setIsDropdownOpen(true);
            }}
            onFocus={() => setIsDropdownOpen(true)}
            style={{ width: '100%', padding: '10px', fontSize: '15px', borderRadius: '6px', border: '1px solid #cbd5e0', boxSizing: 'border-box' }}
          />
          {searchTerm && (
            <button 
              onClick={() => { setSearchTerm(''); setSelectedCity(''); setIsDropdownOpen(true); }}
              style={{ position: 'absolute', right: '10px', top: '25%', border: 'none', background: 'none', cursor: 'pointer', color: '#a0aec0' }}
            >
              ✕
            </button>
          )}
        </div>
        
        {isDropdownOpen && (
          <ul style={{ 
            position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 1000, 
            backgroundColor: '#fff', border: '1px solid #cbd5e0', borderRadius: '6px', 
            maxHeight: '200px', overflowY: 'auto', margin: '4px 0 0 0', padding: 0, listStyle: 'none',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)' 
          }}>
            {filteredCities.length > 0 ? (
              filteredCities.map((city, idx) => (
                <li 
                  key={idx} 
                  onClick={() => handleCitySelect(city)}
                  style={{ padding: '10px', cursor: 'pointer', backgroundColor: selectedCity === city ? '#ebf8ff' : '#fff', borderBottom: '1px solid #edf2f7' }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#f7fafc'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = selectedCity === city ? '#ebf8ff' : '#fff'}
                >
                  📍 {city}
                </li>
              ))
            ) : (
              <li style={{ padding: '10px', color: '#a0aec0', italic: 'true' }}>No matching cities found</li>
            )}
          </ul>
        )}
      </section>

      {/* MAIN DASHBOARD BLOCK WITH OUTER LIGHT BLUE AMBIENT GLOW */}
      <div style={{ display: 'flex', gap: '30px', ...ambientGlowStyle }} onClick={() => setIsDropdownOpen(false)}>
        
        {/* LEFT COLUMN: RESULTS */}
        <div style={{ flex: 1, maxHeight: '850px', overflowY: 'auto', paddingRight: '10px' }}>
          <h3 style={{ borderBottom: '2px solid #edf2f7', paddingBottom: '8px', color: '#2d3748' }}>🏢 Found Entities</h3>
          {loading && <p>Loading data layers...</p>}
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {searchResults && searchResults.map((company, idx) => (
              <li key={idx} style={{ marginBottom: '12px' }}>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    dispatch(fetchCompanyProfile(company.bce));
                    triggerNotaryStream(company.bce);
                  }}
                  style={{ 
                    textAlign: 'left', width: '100%', padding: '12px', cursor: 'pointer',
                    borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#3182ce'; e.currentTarget.style.backgroundColor = '#fff'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.backgroundColor = '#f8fafc'; }}
                >
                  <strong style={{ color: '#2b6cb0', fontSize: '15px' }}>{company.company_name}</strong> <span style={{ color: '#4a5568' }}>({company.city})</span><br />
                  <div style={{ marginTop: '5px', fontSize: '12px', color: '#718096' }}>
                    <span>🆔 BCE: {company.bce}</span> | <span>💼 Sector: {company.sector}</span>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* RIGHT COLUMN: ANALYTICS PROFILE */}
        <div style={{ flex: 2.2, borderLeft: '1px solid #e2e8f0', paddingLeft: '30px' }}>
          {selectedProfile && selectedProfile.metadata ? (
            <div>
              <h2 style={{ color: '#1a202c', marginTop: 0 }}>📋 Profile Sheet: {selectedProfile.metadata.company_name}</h2>
              <p><strong>BCE Number:</strong> {selectedProfile.metadata.bce} | <strong>HQ City:</strong> {selectedProfile.metadata.city} ({selectedProfile.metadata.zipcode})</p>

              <h3 style={{ color: '#2d3748', marginTop: '25px' }}>💰 Unified Financial History (Gold Layer)</h3>
              {selectedProfile.financials && selectedProfile.financials.length > 0 ? (
                <table border="0" cellPadding="10" style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#edf2f7', color: '#4a5568', textAlign: 'left' }}>
                      <th>Year</th>
                      <th>Turnover (€)</th>
                      <th>Gross Margin (€)</th>
                      <th>ROE (%)</th>
                      <th>Liquidity Ratio</th>
                      <th>Debt Ratio (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedProfile.financials.map((f, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #edf2f7' }}>
                        <td><strong>{f.year}</strong></td>
                        <td>{f.ca?.toLocaleString()} €</td>
                        <td>{f.marge_brute?.toLocaleString()} €</td>
                        <td>{f.ratios?.roe_pct}%</td>
                        <td>{f.ratios?.liquidite}</td>
                        <td>{f.ratios?.taux_endettement_pct}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p style={{ color: 'orange' }}>⚠️ No financial exercises matched.</p>
              )}

              {/* 🚀 STEP 2: BEAUTIFIED LIVE NOTAIRE STREAM COMPONENT */}
              {/* LIVE SCRAPER STREAM WITH EMBEDDED METADATA VIEWER */}
              <h3 style={{ marginTop: '35px', color: '#2d3748' }}>🗀 Live Notaire.be Document Scraper (SSE Stream)</h3>
              <div style={{ 
                backgroundColor: '#0f172a', color: '#38bdf8', padding: '20px', 
                borderRadius: '10px', fontFamily: '"Fira Code", monospace', fontSize: '13px',
                boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.8)', border: '1px solid #334155',
                maxHeight: '220px', overflowY: 'auto'
              }}>
                {streamedLogs.length === 0 && <p style={{ color: '#64748b', margin: 0, fontStyle: 'italic' }}>⚡ System idle. Select an entity to spin up real-time stream engine...</p>}
                {streamedLogs.map((log, index) => {
                  const isDone = log.status?.toLowerCase() === 'completed';
                  return (
                    <div key={index} style={{ marginBottom: '8px', display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ 
                        color: isDone ? '#4ade80' : '#fbbf24', 
                        backgroundColor: isDone ? 'rgba(74,222,128,0.1)' : 'rgba(251,191,36,0.1)',
                        padding: '2px 6px', borderRadius: '4px', marginRight: '10px', fontSize: '11px', fontWeight: 'bold'
                      }}>
                        {log.status ? log.status.toUpperCase() : 'INFO'}
                      </span>
                      <div style={{ flex: 1, color: isDone ? '#e2e8f0' : '#94a3b8' }}>
                        {log.message || `Found act metadata link: ${log.doc?.type || 'Statuts'} (${log.doc?.date || 'N/A'})`}
                        {log.doc && (
                          <button 
                            onClick={(e) => {
                              e.preventDefault();
                              // Capture data block to display locally instead of linking to ejustice
                              setActiveDocumentView(log.doc);
                            }}
                            style={{ 
                              color: '#38bdf8', border: '1px solid #0284c7', cursor: 'pointer',
                              marginLeft: '12px', padding: '2px 8px', borderRadius: '4px', 
                              backgroundColor: '#1e293b', fontSize: '11px'
                            }}
                          >
                            PDF View 📊
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* 📑 EMBEDDED MODAL DOCUMENT VIEWER (REPLACES EXTERNAL REDIRECTS) */}
              {/* 📑 EMBEDDED MODAL DOCUMENT VIEWER */}
              {activeDocumentView && (
                <div style={{
                  position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                  backgroundColor: 'rgba(15, 23, 42, 0.75)', display: 'flex',
                  justifyContent: 'center', alignItems: 'center', zIndex: 2000,
                  backdropFilter: 'blur(4px)'
                }}>
                  <div style={{
                    backgroundColor: '#ffffff', width: '600px', borderRadius: '12px',
                    padding: '25px', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
                      <h3 style={{ margin: 0, color: '#0f172a' }}>📄 Act Metadata Inspector</h3>
                      <button 
                        onClick={() => setActiveDocumentView(null)}
                        style={{ border: 'none', background: 'transparent', fontSize: '18px', cursor: 'pointer', color: '#64748b' }}
                      >✕</button>
                    </div>
                    
                    <div style={{ marginTop: '20px' }}>
                      {/* Check if the URL points to the raw search portal fallback instead of a deep-scraped PDF metadata chunk */}
                      {activeDocumentView.url && activeDocumentView.url.includes("tsvn.htm") ? (
                        <div style={{ padding: '15px', backgroundColor: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '8px', color: '#78350f' }}>
                          <h4 style={{ margin: '0 0 8px 0' }}>⚠️ Portal Index Pointer Detected</h4>
                          <p style={{ margin: 0, fontSize: '13px', lineHeight: '1.5' }}>
                            The current backend scraper returned the root <strong>Moniteur Belge Search Index Portal</strong> link rather than a granular document object. To access specific PDF acts or structural histories for this corporate ID, use the primary lookup route inside the portal.
                          </p>
                        </div>
                      ) : (
                        <p style={{ fontSize: '14px', color: '#475569', marginBottom: '15px' }}>
                          The document scraper successfully extracted the following published metadata directly from the official publication source:
                        </p>
                      )}
                      
                      <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #e2e8f0', marginTop: '15px' }}>
                        <tbody>
                          <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                            <td style={{ padding: '10px', backgroundColor: '#f8fafc', fontWeight: 'bold', width: '35%' }}>Document Type</td>
                            <td style={{ padding: '10px', color: '#0f172a' }}>
                              {activeDocumentView.url && activeDocumentView.url.includes("tsvn.htm") ? "📁 Moniteur Belge Index Search Portal" : `✨ ${activeDocumentView.type || 'Corporate Decree / Statuts'}`}
                            </td>
                          </tr>
                          <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                            <td style={{ padding: '10px', backgroundColor: '#f8fafc', fontWeight: 'bold' }}>Publication Date</td>
                            <td style={{ padding: '10px', color: '#0f172a' }}>
                              {activeDocumentView.url && activeDocumentView.url.includes("tsvn.htm") ? "📅 Index Link Only" : `📅 ${activeDocumentView.date || 'N/A'}`}
                            </td>
                          </tr>
                          <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                            <td style={{ padding: '10px', backgroundColor: '#f8fafc', fontWeight: 'bold' }}>Source Origin</td>
                            <td style={{ padding: '10px', color: '#2563eb', fontSize: '12px', fontFamily: 'monospace' }}>
                              Moniteur Belge (ejustice Extraction)
                            </td>
                          </tr>
                          <tr>
                            <td style={{ padding: '10px', backgroundColor: '#f8fafc', fontWeight: 'bold' }}>Internal File Routing</td>
                            <td style={{ padding: '10px', color: '#64748b', fontSize: '11px', fontFamily: 'monospace', wordBreak: 'break-all' }}>
                              <a href={activeDocumentView.url} target="_blank" rel="noreferrer" style={{ color: '#2563eb', textDecoration: 'underline' }}>
                                {activeDocumentView.url}
                              </a>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>

                    <div style={{ marginTop: '25px', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                      {activeDocumentView.url && (
                        <a 
                          href={activeDocumentView.url} 
                          target="_blank" 
                          rel="noreferrer"
                          style={{
                            backgroundColor: '#2563eb', color: '#ffffff', textDecoration: 'none',
                            padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px', display: 'inline-block'
                          }}
                        >
                          Launch Official Site ↗
                        </a>
                      )}
                      <button 
                        onClick={() => setActiveDocumentView(null)}
                        style={{
                          backgroundColor: '#0f172a', color: '#ffffff', border: 'none',
                          padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px'
                        }}
                      >
                        Return to Dashboard
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* <h3 style={{ marginTop: '35px', color: '#2d3748' }}>🔀 Live Notaire.be Document Scraper (SSE Stream)</h3>
              <div style={{ 
                backgroundColor: '#0f172a', color: '#38bdf8', padding: '20px', 
                borderRadius: '10px', fontFamily: '"Fira Code", monospace', fontSize: '13px',
                boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.8)', border: '1px solid #334155',
                maxHeight: '220px', overflowY: 'auto'
              }}>
                {streamedLogs.length === 0 && <p style={{ color: '#64748b', margin: 0, fontStyle: 'italic' }}>⚡ System idle. Select an entity to spin up real-time stream engine...</p>}
                {streamedLogs.map((log, index) => {
                  const isDone = log.status?.toLowerCase() === 'completed';
                  return (
                    <div key={index} style={{ marginBottom: '8px', display: 'flex', alignItems: 'flex-start', borderBottom: '1px style #1e293b', paddingBottom: '4px' }}>
                      <span style={{ 
                        color: isDone ? '#4ade80' : '#fbbf24', 
                        backgroundColor: isDone ? 'rgba(74,222,128,0.1)' : 'rgba(251,191,36,0.1)',
                        padding: '2px 6px', borderRadius: '4px', marginRight: '10px', fontSize: '11px', fontWeight: 'bold'
                      }}>
                        {log.status ? log.status.toUpperCase() : 'INFO'}
                      </span>
                      <div style={{ flex: 1, color: isDone ? '#e2e8f0' : '#94a3b8' }}>
                        {log.message || `Found act metadata link: ${log.doc?.type || 'Statuts'} (${log.doc?.date || 'N/A'})`}
                        {log.doc?.url && (
                          <a href={log.doc.url} target="_blank" rel="noreferrer" style={{ 
                            color: '#38bdf8', textDecoration: 'none', marginLeft: '12px', 
                            padding: '2px 8px', borderRadius: '4px', backgroundColor: '#1e293b', border: '1px solid #0284c7' 
                          }}
                          onMouseEnter={(e) => e.target.style.backgroundColor = '#0284c7'}
                          onMouseLeave={(e) => e.target.style.backgroundColor = '#1e293b'}
                          >
                            PDF View ↗
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div> */}

              {/* 📊 DUAL-AXIS FINANCIAL CHART SAFELY GUARDED BY BOUNDARY */}
              {chartData.length > 0 && (
                <ChartErrorBoundary>
                  <div style={{ marginTop: '35px', padding: '20px', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#f8fafc' }}>
                    <h4 style={{ margin: '0 0 15px 0', color: '#1a202c' }}>📈 Financial Performance Overview</h4>
                    <div style={{ width: '100%', minWidth: '300px', height: '300px' }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={chartData} margin={{ top: 10, right: 5, left: -10, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="year" stroke="#4a5568" fontSize={12} />
                          <YAxis yAxisId="left" stroke="#3b82f6" fontSize={12} tickFormatter={formatCurrency} />
                          <YAxis yAxisId="right" orientation="right" stroke="#10b981" fontSize={12} tickFormatter={formatCurrency} />
                          <Tooltip formatter={(value) => formatCurrency(value)} />
                          <Legend verticalAlign="top" height={36} />
                          <Bar yAxisId="left" name="Turnover (€)" dataKey="turnover" fill="#3b82f6" maxBarSize={45} />
                          <Line yAxisId="right" type="monotone" name="Gross Margin (€)" dataKey="grossMargin" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </ChartErrorBoundary>
              )}


              {/* UNIFIED FINANCIAL HISTORY */}
              {/* <h3 style={{ color: '#2d3748', marginTop: '25px' }}>💰 Unified Financial History (Gold Layer)</h3>
              {selectedProfile.years && selectedProfile.years.length > 0 ? (
                <table border="0" cellPadding="10" style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#edf2f7', color: '#4a5568', textAlign: 'left' }}>
                      <th>Year</th>
                      <th>Turnover (ca)</th>
                      <th>Gross Margin</th>
                      <th>EBIT</th>
                      <th>Net Result</th>
                      <th>ROE (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedProfile.years.map((f, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #edf2f7' }}>
                        <td><strong>{f.year}</strong></td>
                        <td>{f.ca?.toLocaleString()} €</td>
                        <td>{f.marge_brute?.toLocaleString()} €</td>
                        <td>{f.ebit?.toLocaleString()} €</td>
                        <td>{f.resultat_net?.toLocaleString()} €</td>
                        <td>{f.ratios?.roe_pct?.toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p style={{ color: 'orange' }}>⚠️ No financial exercises matched this layout schema.</p>
              )} */}


              <h3 style={{ marginTop: '35px', color: '#2d3748' }}> Overview of Financial Performance </h3>
              {/* 🚀 NEW: SECTOR FINANCE ANALYTICS CARD BLOCK */}
              <div style={{ 
                display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', 
                marginBottom: '25px', padding: '15px', borderRadius: '10px', 
                backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' 
              }}>
                {/* <div style={{ padding: '10px', textAlign: 'center', borderRight: '1px solid #bbf7d0' }}>
                  <div style={{ fontSize: '12px', color: '#166534', fontWeight: 'bold', textTransform: 'uppercase' }}>Total Gold Market Cap (Turnover)</div>
                  <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#14532d', marginTop: '4px' }}>{formatCurrency(globalFinance.total_turnover)}</div>
                </div> */}
                <div style={{ padding: '10px', textAlign: 'center', borderRight: '1px solid #bbf7d0' }}>
                  <div style={{ fontSize: '12px', color: '#166534', fontWeight: 'bold', textTransform: 'uppercase' }}>Avg Sector Gross Margin</div>
                  <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#14532d', marginTop: '4px' }}>{formatCurrency(globalFinance.average_margin)}</div>
                </div>
                <div style={{ padding: '10px', textAlign: 'center' }}>
                  <div style={{ fontSize: '12px', color: '#166534', fontWeight: 'bold', textTransform: 'uppercase' }}>👑 Market Revenue Leader</div>
                  <div style={{ fontSize: '15px', fontWeight: 'bold', color: '#14532d', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {globalFinance.market_leader}
                  </div>
                  <div style={{ fontSize: '11px', color: '#15803d' }}>({formatCurrency(globalFinance.market_leader_revenue)})</div>
                </div>
              </div>


            </div>
          ) : (
            <p style={{ color: '#718096', padding: '40px 0', textAlign: 'center', fontStyle: 'italic' }}>Select an enterprise from the left column to parse information matrix.</p>
          )}
        </div>

        <hr style={{ border: '0', borderTop: '1px solid #e2e8f0', marginBottom: '25px' }} />
      </div>
    </div>
  );
}

export default App;


// --------
// import React, { useState, useEffect, Component } from 'react';
// import { useDispatch, useSelector } from 'react-redux';
// import { searchCompanies, fetchCompanyProfile } from './store/companySlice';
// import axios from 'axios';
// import { ResponsiveContainer, ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts';

// class ChartErrorBoundary extends Component {
//   constructor(props) {
//     super(props);
//     this.state = { hasError: false };
//   }
//   static getDerivedStateFromError(error) {
//     return { hasError: true };
//   }
//   componentDidCatch(error, errorInfo) {
//     console.error("Chart Error Caught:", error, errorInfo);
//   }
//   render() {
//     if (this.state.hasError) {
//       return (
//         <div style={{ marginTop: '30px', padding: '15px', border: '1px solid #ffcccb', borderRadius: '6px', backgroundColor: '#fff5f5', color: '#cc0000' }}>
//           <h4>📈 Financial Performance Chart</h4>
//           <p style={{ fontSize: '14px' }}>Could not render chart component. Check browser console logs for bundle issues.</p>
//         </div>
//       );
//     }
//     return this.props.children;
//   }
// }

// function App() {
//   const [cities, setCities] = useState([]);
//   const [selectedCity, setSelectedCity] = useState('');
//   const [searchTerm, setSearchTerm] = useState('');
//   const [isDropdownOpen, setIsDropdownOpen] = useState(false);
//   const [streamedLogs, setStreamedLogs] = useState([]);
  
//   const [globalFinance, setGlobalFinance] = useState({
//     total_turnover: 0,
//     average_margin: 0,
//     market_leader: 'Loading...',
//     market_leader_revenue: 0
//   });

//   const dispatch = useDispatch();
//   const { searchResults, selectedProfile, loading } = useSelector((state) => state.company);

//   const ambientGlowStyle = {
//     boxShadow: '0 0 15px rgba(173, 216, 230, 0.6), inset 0 0 10px rgba(173, 216, 230, 0.2)',
//     border: '1px solid rgba(135, 206, 250, 0.5)',
//     borderRadius: '12px',
//     padding: '20px',
//     backgroundColor: '#ffffff'
//   };

//   useEffect(() => {
//     axios.get('http://127.0.0.1:8000/api/cities')
//       .then(res => setCities(res.data))
//       .catch(err => console.error("Error loading cities", err));
      
//     axios.get('http://127.0.0.1:8000/api/analytics/finance')
//       .then(res => setGlobalFinance(res.data))
//       .catch(err => console.error("Error loading global analytics", err));
//   }, [searchResults]);

//   const handleCitySelect = (city) => {
//     setSelectedCity(city);
//     setSearchTerm(city);
//     setIsDropdownOpen(false);
//     if (city) {
//       dispatch(searchCompanies(city));
//     }
//   };

//   const triggerNotaryStream = (bce) => {
//     setStreamedLogs([]);
//     const eventSource = new EventSource(`http://127.0.0.1:8000/api/companies/${bce}/statutes/stream`);
//     eventSource.onmessage = (event) => {
//       const data = JSON.parse(event.data);
//       setStreamedLogs((prev) => [...prev, data]);
//       if (data.status === 'completed') eventSource.close();
//     };
//     eventSource.onerror = () => eventSource.close();
//   };

//   const formatCurrency = (value) => {
//     if (!value) return '0 €';
//     if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M €`;
//     if (value >= 1000) return `${(value / 1000).toFixed(0)}k €`;
//     return `${value} €`;
//   };

//   const filteredCities = cities.filter(city => 
//     city.toLowerCase().includes(searchTerm.toLowerCase())
//   );

//   // Parse years block for Recharts visual execution
//   const chartData = selectedProfile?.years
//     ? [...selectedProfile.years]
//         .map((f) => ({
//           year: String(f?.year || ''),
//           turnover: Number(f?.ca || 0),
//           grossMargin: Number(f?.marge_brute || 0),
//         }))
//         .filter(f => f.year)
//         .sort((a, b) => a.year.localeCompare(b.year))
//     : [];

//   return (
//     <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1300px', margin: '0 auto' }}>
//       <h1>🇧🇪 Belgium Enterprise Analytics Dashboard </h1>
      
//       {/* KPI METRICS STATUS BAR */}
//       <div style={{ display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '20px', fontSize: '14px', fontWeight: 'bold' }}>
//         <span style={{ color: '#cd7f32', backgroundColor: '#fdf5e6', padding: '6px 12px', borderRadius: '20px', border: '1px solid #cd7f32' }}>
//           🥉 Bronze: 24,531 records
//         </span>
//         <span style={{ color: '#718096', backgroundColor: '#f7fafc', padding: '6px 12px', borderRadius: '20px', border: '1px solid #cbd5e0' }}>
//           🥈 Silver: 12,404 records
//         </span>
//         <span style={{ color: '#d4af37', backgroundColor: '#fffdf0', padding: '6px 12px', borderRadius: '20px', border: '1px solid #d4af37' }}>
//           👑 Gold: {searchResults?.length || 0} active keys | Status: <span style={{ color: selectedProfile ? '#2f855a' : '#c53030' }}>{selectedProfile ? "Synced" : "Awaiting Selection"}</span>
//         </span>
//       </div>

//       {/* MACRO SECTOR FINANCE ANALYTICS CARDS */}
//       <div style={{ 
//         display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', 
//         marginBottom: '25px', padding: '15px', borderRadius: '10px', 
//         backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' 
//       }}>
//         <div style={{ padding: '10px', textAlign: 'center', borderRight: '1px solid #bbf7d0' }}>
//           <div style={{ fontSize: '12px', color: '#166534', fontWeight: 'bold', textTransform: 'uppercase' }}>Total Gold Market Cap (Turnover)</div>
//           <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#14532d', marginTop: '4px' }}>{formatCurrency(globalFinance.total_turnover)}</div>
//         </div>
//         <div style={{ padding: '10px', textAlign: 'center', borderRight: '1px solid #bbf7d0' }}>
//           <div style={{ fontSize: '12px', color: '#166534', fontWeight: 'bold', textTransform: 'uppercase' }}>Avg Sector Gross Margin</div>
//           <div style={{ fontSize: '22px', fontWeight: 'bold', color: '#14532d', marginTop: '4px' }}>{formatCurrency(globalFinance.average_margin)}</div>
//         </div>
//         <div style={{ padding: '10px', textAlign: 'center' }}>
//           <div style={{ fontSize: '12px', color: '#166534', fontWeight: 'bold', textTransform: 'uppercase' }}>👑 Market Revenue Leader</div>
//           <div style={{ fontSize: '15px', fontWeight: 'bold', color: '#14532d', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
//             {globalFinance.market_leader}
//           </div>
//           <div style={{ fontSize: '11px', color: '#15803d' }}>({formatCurrency(globalFinance.market_leader_revenue)})</div>
//         </div>
//       </div>

//       <hr style={{ border: '0', borderTop: '1px solid #e2e8f0', marginBottom: '25px' }} />

//       {/* SEARCH DROPDOWN INPUT SELECTOR */}
//       <section style={{ margin: '20px 0', position: 'relative', width: '350px' }}>
//         <label htmlFor="city-search-input" style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#4a5568' }}>
//           Filter by Corporate City Hub:
//         </label>
//         <div style={{ position: 'relative' }}>
//           <input 
//             id="city-search-input"
//             type="text"
//             placeholder="Type to search city..."
//             value={searchTerm}
//             onChange={(e) => {
//               setSearchTerm(e.target.value);
//               setIsDropdownOpen(true);
//             }}
//             onFocus={() => setIsDropdownOpen(true)}
//             style={{ width: '100%', padding: '10px', fontSize: '15px', borderRadius: '6px', border: '1px solid #cbd5e0', boxSizing: 'border-box' }}
//           />
//           {searchTerm && (
//             <button 
//               onClick={() => { setSearchTerm(''); setSelectedCity(''); setIsDropdownOpen(true); }}
//               style={{ position: 'absolute', right: '10px', top: '25%', border: 'none', background: 'none', cursor: 'pointer', color: '#a0aec0' }}
//             >
//               ✕
//             </button>
//           )}
//         </div>
        
//         {isDropdownOpen && (
//           <ul style={{ 
//             position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 1000, 
//             backgroundColor: '#fff', border: '1px solid #cbd5e0', borderRadius: '6px', 
//             maxHeight: '200px', overflowY: 'auto', margin: '4px 0 0 0', padding: 0, listStyle: 'none',
//             boxShadow: '0 4px 6px rgba(0,0,0,0.1)' 
//           }}>
//             {filteredCities.length > 0 ? (
//               filteredCities.map((city, idx) => (
//                 <li 
//                   key={idx} 
//                   onClick={() => handleCitySelect(city)}
//                   style={{ padding: '10px', cursor: 'pointer', backgroundColor: selectedCity === city ? '#ebf8ff' : '#fff', borderBottom: '1px solid #edf2f7' }}
//                 >
//                   📍 {city}
//                 </li>
//               ))
//             ) : (
//               <li style={{ padding: '10px', color: '#a0aec0', fontStyle: 'italic' }}>No matching cities found</li>
//             )}
//           </ul>
//         )}
//       </section>

//       {/* MAIN DASHBOARD PANEL COMPONENT */}
//       <div style={{ display: 'flex', gap: '30px', ...ambientGlowStyle }} onClick={() => setIsDropdownOpen(false)}>
        
//         {/* LEFT COLUMN: COMPANY LIST */}
//         <div style={{ flex: 1, maxHeight: '950px', overflowY: 'auto', paddingRight: '10px' }}>
//           <h3 style={{ borderBottom: '2px solid #edf2f7', paddingBottom: '8px', color: '#2d3748' }}>🏢 Found Entities</h3>
//           {loading && <p>Loading data layers...</p>}
//           <ul style={{ listStyle: 'none', padding: 0 }}>
//             {searchResults && searchResults.map((company, idx) => (
//               <li key={idx} style={{ marginBottom: '12px' }}>
//                 <button 
//                   onClick={(e) => {
//                     e.stopPropagation();
//                     dispatch(fetchCompanyProfile(company.bce || company.enterprise_number));
//                     triggerNotaryStream(company.bce || company.enterprise_number);
//                   }}
//                   style={{ 
//                     textAlign: 'left', width: '100%', padding: '12px', cursor: 'pointer',
//                     borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc'
//                   }}
//                 >
//                   <strong style={{ color: '#2b6cb0', fontSize: '15px' }}>{company.company_name || `Enterprise ${company.enterprise_number}`}</strong> <span style={{ color: '#4a5568' }}>({company.city})</span><br />
//                   <div style={{ marginTop: '5px', fontSize: '12px', color: '#718096' }}>
//                     <span>🆔 BCE: {company.bce || company.enterprise_number}</span>
//                   </div>
//                 </button>
//               </li>
//             ))}
//           </ul>
//         </div>

//         {/* RIGHT COLUMN: DETAIL WORKSPACE */}
//         <div style={{ flex: 2.2, borderLeft: '1px solid #e2e8f0', paddingLeft: '30px' }}>
//           {selectedProfile ? (
//             <div>
//               <h2 style={{ color: '#1a202c', marginTop: 0 }}>📋 Entity Sheet: {selectedProfile.company_name || `Enterprise ${selectedProfile.enterprise_number}`}</h2>
              
//               {/* 🚀 NEW STEP: 1 COMPLETE MASTER DATA TABLE INFRASTRUCTURE */}
//               <h3 style={{ color: '#2d3748', marginTop: '20px' }}>🗂️ Complete Entity Master Profile Sheet</h3>
//               <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid #cbd5e0', borderRadius: '8px', overflow: 'hidden', marginBottom: '25px' }}>
//                 <tbody>
//                   <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
//                     <td style={{ backgroundColor: '#f7fafc', padding: '10px', fontWeight: 'bold', width: '30%', color: '#4a5568' }}>Internal MongoDB Database ID</td>
//                     <td style={{ padding: '10px', fontFamily: 'monospace', color: '#1a202c' }}>{selectedProfile._id || 'N/A'}</td>
//                   </tr>
//                   <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
//                     <td style={{ backgroundColor: '#f7fafc', padding: '10px', fontWeight: 'bold', color: '#4a5568' }}>Official Corporate Name</td>
//                     <td style={{ padding: '10px', color: '#1a202c', fontWeight: 'bold' }}>{selectedProfile.company_name || `Enterprise ${selectedProfile.enterprise_number}`}</td>
//                   </tr>
//                   <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
//                     <td style={{ backgroundColor: '#f7fafc', padding: '10px', fontWeight: 'bold', color: '#4a5568' }}>Belgian BCE Enterprise Number</td>
//                     <td style={{ padding: '10px', fontFamily: 'monospace', color: '#2b6cb0', fontWeight: 'bold' }}>{selectedProfile.enterprise_number || 'N/A'}</td>
//                   </tr>
//                   <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
//                     <td style={{ backgroundColor: '#f7fafc', padding: '10px', fontWeight: 'bold', color: '#4a5568' }}>Registered HQ Corporate City</td>
//                     <td style={{ padding: '10px', color: '#1a202c' }}>📍 {selectedProfile.city || 'N/A'}</td>
//                   </tr>
//                   <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
//                     <td style={{ backgroundColor: '#f7fafc', padding: '10px', fontWeight: 'bold', color: '#4a5568' }}>Medallion Data Structure Schema Type</td>
//                     <td style={{ padding: '10px', color: '#1a202c' }}>
//                       <span style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>
//                         {selectedProfile.schema_type || 'Full Layout'}
//                       </span>
//                     </td>
//                   </tr>
//                   <tr>
//                     <td style={{ backgroundColor: '#f7fafc', padding: '10px', fontWeight: 'bold', color: '#4a5568' }}>Last Pipeline Sync Timestamp (Gold Layer)</td>
//                     <td style={{ padding: '10px', color: '#718096', fontSize: '13px' }}>🕒 {selectedProfile.last_updated || 'N/A'}</td>
//                   </tr>
//                 </tbody>
//               </table>

//               {/* UNIFIED FINANCIAL HISTORY */}
//               <h3 style={{ color: '#2d3748', marginTop: '25px' }}>💰 Unified Financial History (Gold Layer)</h3>
//               {selectedProfile.years && selectedProfile.years.length > 0 ? (
//                 <table border="0" cellPadding="10" style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
//                   <thead>
//                     <tr style={{ backgroundColor: '#edf2f7', color: '#4a5568', textAlign: 'left' }}>
//                       <th>Year</th>
//                       <th>Turnover (ca)</th>
//                       <th>Gross Margin</th>
//                       <th>EBIT</th>
//                       <th>Net Result</th>
//                       <th>ROE (%)</th>
//                     </tr>
//                   </thead>
//                   <tbody>
//                     {selectedProfile.years.map((f, i) => (
//                       <tr key={i} style={{ borderBottom: '1px solid #edf2f7' }}>
//                         <td><strong>{f.year}</strong></td>
//                         <td>{f.ca?.toLocaleString()} €</td>
//                         <td>{f.marge_brute?.toLocaleString()} €</td>
//                         <td>{f.ebit?.toLocaleString()} €</td>
//                         <td>{f.resultat_net?.toLocaleString()} €</td>
//                         <td>{f.ratios?.roe_pct?.toFixed(2)}%</td>
//                       </tr>
//                     ))}
//                   </tbody>
//                 </table>
//               ) : (
//                 <p style={{ color: 'orange' }}>⚠️ No financial exercises matched this layout schema.</p>
//               )}

//               {/* LIVE SCRAPER STREAM */}
//               <h3 style={{ marginTop: '35px', color: '#2d3748' }}>🔀 Live Notaire.be Document Scraper (SSE Stream)</h3>
//               <div style={{ 
//                 backgroundColor: '#0f172a', color: '#38bdf8', padding: '20px', 
//                 borderRadius: '10px', fontFamily: '"Fira Code", monospace', fontSize: '13px',
//                 boxShadow: 'inset 0 2px 8px rgba(0,0,0,0.8)', border: '1px solid #334155',
//                 maxHeight: '220px', overflowY: 'auto'
//               }}>
//                 {streamedLogs.length === 0 && <p style={{ color: '#64748b', margin: 0, fontStyle: 'italic' }}>⚡ System idle. Select an entity to spin up real-time stream engine...</p>}
//                 {streamedLogs.map((log, index) => {
//                   const isDone = log.status?.toLowerCase() === 'completed';
//                   return (
//                     <div key={index} style={{ marginBottom: '8px', display: 'flex', alignItems: 'flex-start' }}>
//                       <span style={{ 
//                         color: isDone ? '#4ade80' : '#fbbf24', 
//                         backgroundColor: isDone ? 'rgba(74,222,128,0.1)' : 'rgba(251,191,36,0.1)',
//                         padding: '2px 6px', borderRadius: '4px', marginRight: '10px', fontSize: '11px', fontWeight: 'bold'
//                       }}>
//                         {log.status ? log.status.toUpperCase() : 'INFO'}
//                       </span>
//                       <div style={{ flex: 1, color: isDone ? '#e2e8f0' : '#94a3b8' }}>
//                         {log.message || `Found act metadata link: ${log.doc?.type || 'Statuts'} (${log.doc?.date || 'N/A'})`}
//                         {log.doc?.url && (
//                           <a href={log.doc.url} target="_blank" rel="noreferrer" style={{ 
//                             color: '#38bdf8', textDecoration: 'none', marginLeft: '12px', 
//                             padding: '2px 8px', borderRadius: '4px', backgroundColor: '#1e293b', border: '1px solid #0284c7' 
//                           }}>
//                             PDF View ↗
//                           </a>
//                         )}
//                       </div>
//                     </div>
//                   );
//                 })}
//               </div>

//               {/* DUAL-AXIS CHART */}
//               {chartData.length > 0 && (
//                 <ChartErrorBoundary>
//                   <div style={{ marginTop: '35px', padding: '20px', border: '1px solid #e2e8f0', borderRadius: '8px', backgroundColor: '#f8fafc' }}>
//                     <h4 style={{ margin: '0 0 15px 0', color: '#1a202c' }}>📈 Financial Performance Overview</h4>
//                     <div style={{ width: '100%', minWidth: '300px', height: '300px' }}>
//                       <ResponsiveContainer width="100%" height="100%">
//                         <ComposedChart data={chartData} margin={{ top: 10, right: 5, left: -10, bottom: 5 }}>
//                           <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
//                           <XAxis dataKey="year" stroke="#4a5568" fontSize={12} />
//                           <YAxis yAxisId="left" stroke="#3b82f6" fontSize={12} tickFormatter={formatCurrency} />
//                           <YAxis yAxisId="right" orientation="right" stroke="#10b981" fontSize={12} tickFormatter={formatCurrency} />
//                           <Tooltip formatter={(value) => formatCurrency(value)} />
//                           <Legend verticalAlign="top" height={36} />
//                           <Bar yAxisId="left" name="Turnover (€)" dataKey="turnover" fill="#3b82f6" maxBarSize={45} />
//                           <Line yAxisId="right" type="monotone" name="Gross Margin (€)" dataKey="grossMargin" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
//                         </ComposedChart>
//                       </ResponsiveContainer>
//                     </div>
//                   </div>
//                 </ChartErrorBoundary>
//               )}

//             </div>
//           ) : (
//             <p style={{ color: '#718096', padding: '40px 0', textAlign: 'center', fontStyle: 'italic' }}>Select an enterprise from the left column to parse information matrix.</p>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;