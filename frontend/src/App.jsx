import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { searchCompanies, fetchCompanyProfile } from './store/companySlice';
import axios from 'axios';

function App() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [streamedLogs, setStreamedLogs] = useState([]);
  const dispatch = useDispatch();
  
  const { searchResults, selectedProfile, loading } = useSelector((state) => state.company);

  console.log("🏙️ Cities Dropdown Data Received:", cities);
  // 🏙️ Fetch available cities on component load
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/cities')
      .then(res => setCities(res.data))
      .catch(err => console.error("Error loading cities", err));
  }, []);

  // Trigger search automatically when a dropdown item is picked
  const handleCityChange = (e) => {
    const city = e.target.value;
    setSelectedCity(city);
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

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>🇧🇪 Belgium Enterprise Analytics Dashboard (Day 3)</h1>
      <hr />

      {/* DROPDOWN SELECTOR */}
      <section style={{ margin: '20px 0' }}>
        <label htmlFor="city-select" style={{ marginRight: '10px', fontWeight: 'bold' }}>Filter by Corporate City Hub: </label>
        <select 
          id="city-select"
          value={selectedCity} 
          onChange={handleCityChange}
          style={{ padding: '10px', width: '320px', fontSize: '16px', cursor: 'pointer' }}
        >
          <option value="">-- Choose an existing city --</option>
          {cities.map((city, idx) => (
            <option key={idx} value={city}>{city}</option>
          ))}
        </select>
      </section>

      <div style={{ display: 'flex', gap: '40px' }}>
        {/* LEFT COLUMN: RESULTS */}
        <div style={{ flex: 1 }}>
          <h3>🏢 Found Entities</h3>
          {loading && <p>Loading data layers...</p>}
          <ul>
            {searchResults.map((company, idx) => (
              <li key={idx} style={{ marginBottom: '10px' }}>
                <button 
                  onClick={() => {
                    dispatch(fetchCompanyProfile(company.bce));
                    triggerNotaryStream(company.bce);
                  }}
                  style={{ textAlign: 'left', width: '100%', padding: '8px', cursor: 'pointer' }}
                >
                  <strong>{company.company_name}</strong> ({company.city}) <br />
                  <small>BCE: {company.bce} | Sector: {company.sector}</small>
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* RIGHT COLUMN: ANALYTICS PROFILE */}
        <div style={{ flex: 2, borderLeft: '1px solid #ccc', paddingLeft: '20px' }}>
          {selectedProfile ? (
            <div>
              <h2>📋 Profile Sheet: {selectedProfile.metadata.company_name}</h2>
              <p><strong>BCE Number:</strong> {selectedProfile.metadata.bce}</p>
              <p><strong>HQ City:</strong> {selectedProfile.metadata.city} ({selectedProfile.metadata.zipcode})</p>

              <h3>💰 Unified Financial History (Gold Layer)</h3>

              {selectedProfile.financials.length > 0 ? (
                <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f2f2f2' }}>
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
                      <tr key={i}>
                        <td>{f.year}</td>
                        <td>{f.ca?.toLocaleString()}</td>
                        <td>{f.marge_brute?.toLocaleString()}</td>
                        <td>{f.ratios.roe_pct}%</td>
                        <td>{f.ratios.liquidite}</td>
                        <td>{f.ratios.taux_endettement_pct}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p style={{ color: 'orange' }}>⚠️ No financial exercises matched.</p>
              )}

              <h3 style={{ marginTop: '30px' }}>🔀 Live Notaire.be Document Scraper (SSE Stream)</h3>
              <div style={{ backgroundColor: '#1e1e1e', color: '#00ff00', padding: '15px', borderRadius: '5px', fontFamily: 'monospace' }}>
                {streamedLogs.length === 0 && <p style={{ color: '#aaa' }}>Waiting for selection...</p>}
                {streamedLogs.map((log, index) => (
                  <div key={index} style={{ marginBottom: '5px' }}>
                    [{log.status.toUpperCase()}] {log.message || `Found act link: ${log.doc?.type} (${log.doc?.date})`}
                    {log.doc && <a href={log.doc.url} target="_blank" rel="noreferrer" style={{ color: '#00bfff', marginLeft: '10px' }}>Open PDF</a>}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p style={{ color: '#666' }}>Select an enterprise from the left column to parse information.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

// import React, { useState, useEffect } from 'react';
// import { useDispatch, useSelector } from 'react-redux';
// import { searchCompanies, fetchCompanyProfile } from './store/companySlice';

// function App() {
//   const [query, setQuery] = useState('');
//   const [streamedLogs, setStreamedLogs] = useState([]);
//   const dispatch = useDispatch();
  
//   const { searchResults, selectedProfile, loading } = useSelector((state) => state.company);

//   const handleSearch = (e) => {
//     e.preventDefault();
//     if (query.length >= 2) dispatch(searchCompanies(query));
//   };

//   // 🔀 SSE Notary Scraper Connection Manager
//   const triggerNotaryStream = (bce) => {
//     setStreamedLogs([]);
//     const eventSource = new EventSource(`http://127.0.0.1:8000/api/companies/${bce}/statutes/stream`);

//     eventSource.onmessage = (event) => {
//       const data = JSON.parse(event.data);
//       setStreamedLogs((prev) => [...prev, data]);
//       if (data.status === 'completed') {
//         eventSource.close();
//       }
//     };

//     eventSource.onerror = () => {
//       eventSource.close();
//     };
//   };

//   return (
//     <div style={{ padding: '20px', fontFamily: 'sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
//       <h1>🇧🇪 Belgium Enterprise Analytics Dashboard (Day 3)</h1>
//       <hr />

//       {/* SEARCH SECTION */}
//       <section style={{ margin: '20px 0' }}>
//         <form onSubmit={handleSearch}>
//           <input 
//             type="text" 
//             placeholder="Search by city or name (e.g. Namur)..." 
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             style={{ padding: '10px', width: '300px', marginRight: '10px' }}
//           />
//           <button type="submit" style={{ padding: '10px 20px', cursor: 'pointer' }}>Search</button>
//         </form>
//       </section>

//       <div style={{ display: 'flex', gap: '40px' }}>
//         {/* LEFT COLUMN: RESULTS */}
//         <div style={{ flex: 1 }}>
//           <h3>🏢 Found Entities</h3>
//           {loading && <p>Loading data layers...</p>}
//           <ul>
//             {searchResults.map((company, idx) => (
//               <li key={idx} style={{ marginBottom: '10px' }}>
//                 <button 
//                   onClick={() => {
//                     dispatch(fetchCompanyProfile(company.bce));
//                     triggerNotaryStream(company.bce);
//                   }}
//                   style={{ textAlign: 'left', width: '100%', padding: '8px', cursor: 'pointer' }}
//                 >
//                   <strong>{company.company_name}</strong> ({company.city}) <br />
//                   <small>BCE: {company.bce} | Sector: {company.sector}</small>
//                 </button>
//               </li>
//             ))}
//           </ul>
//         </div>

//         {/* RIGHT COLUMN: ANALYTICS PROFILE */}
//         <div style={{ flex: 2, borderLeft: '1px solid #ccc', paddingLeft: '20px' }}>
//           {selectedProfile ? (
//             <div>
//               <h2>📋 Profile Sheet: {selectedProfile.metadata.company_name}</h2>
//               <p><strong>BCE Number:</strong> {selectedProfile.metadata.bce}</p>
//               <p><strong>HQ City:</strong> {selectedProfile.metadata.city} ({selectedProfile.metadata.zipcode})</p>

//               {/* FINANCIAL GOLD MATRIX */}
//               <h3>💰 Unified Financial History (Gold Layer)</h3>
//               {selectedProfile.financials.length > 0 ? (
//                 <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
//                   <thead>
//                     <tr style={{ backgroundColor: '#f2f2f2' }}>
//                       <th>Year</th>
//                       <th>Turnover (€)</th>
//                       <th>Gross Margin (€)</th>
//                       <th>ROE (%)</th>
//                       <th>Liquidity Ratio</th>
//                       <th>Debt Ratio (%)</th>
//                     </tr>
//                   </thead>
//                   <tbody>
//                     {selectedProfile.financials.map((f, i) => (
//                       <tr key={i}>
//                         <td>{f.year}</td>
//                         <td>{f.ca?.toLocaleString()}</td>
//                         <td>{f.marge_brute?.toLocaleString()}</td>
//                         <td>{f.ratios.roe_pct}%</td>
//                         <td>{f.ratios.liquidite}</td>
//                         <td>{f.ratios.taux_endettement_pct}%</td>
//                       </tr>
//                     ))}
//                   </tbody>
//                 </table>
//               ) : (
//                 <p style={{ color: 'orange' }}>⚠️ No financial exercises matched in Gold Layer for this entity type.</p>
//               )}

//               {/* NOTARY STATUTES STREAM */}
//               <h3 style={{ marginTop: '30px' }}>🔀 Live Notaire.be Document Scraper (SSE Stream)</h3>
//               <div style={{ backgroundColor: '#1e1e1e', color: '#00ff00', padding: '15px', borderRadius: '5px', fontFamily: 'monospace' }}>
//                 {streamedLogs.length === 0 && <p style={{ color: '#aaa' }}>Waiting for selection to spin up worker pipeline...</p>}
//                 {streamedLogs.map((log, index) => (
//                   <div key={index} style={{ marginBottom: '5px' }}>
//                     [{log.status.toUpperCase()}] {log.message || `Found act link: ${log.doc?.type} (${log.doc?.date})`}
//                     {log.doc && <a href={log.doc.url} target="_blank" rel="noreferrer" style={{ color: '#00bfff', marginLeft: '10px' }}>Open PDF</a>}
//                   </div>
//                 ))}
//               </div>
//             </div>
//           ) : (
//             <p style={{ color: '#666' }}>Select an enterprise from the left column to parse Silver information combined with Gold financial ratio matrices.</p>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;