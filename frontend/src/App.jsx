import React, { useState } from 'react';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiSummary, setAiSummary] = useState('');
  const [metadata, setMetadata] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  // Handle file selection via input
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  // Handle Drag & Drop UX features
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setAiSummary('');
    setMetadata(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Server communication failed.");
      }

      const data = await response.json();
      
      // FAIL-SAFE: Check if the AI accidentally sent an object, and force it to be a string.
      const safeSummary = typeof data.aiSummary === 'string' 
        ? data.aiSummary 
        : JSON.stringify(data.aiSummary);
        
      setAiSummary(safeSummary);
      setMetadata(data.extractedData);
    } catch (error) {
      console.error("Error:", error);
      alert(error.message || "Make sure your FastAPI server is running on port 8000!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-light min-vh-100 pb-5">
      {/* Top Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
        <div className="container">
          <a className="navbar-brand fw-bold d-flex align-items-center" href="#!">
            <i className="bi bi-shield-plus me-2 fs-3"></i>
            MediDecode <span className="badge bg-info ms-2 fs-7 fw-normal">v2.0 Enterprise</span>
          </a>
          <span className="navbar-text text-white-50 d-none d-md-inline">
            Secure, RAG-Driven Clinical Report Parsing
          </span>
        </div>
      </nav>

      <div className="container">
        <div className="row g-4">
          
          {/* LEFT SIDEBAR: File controls */}
          <div className="col-lg-4 d-print-none">
            <div className="card border-0 shadow-sm rounded-3 mb-4">
              <div className="card-body p-4">
                <h5 className="card-title fw-bold text-dark mb-3">Analysis Console</h5>
                
                <form onSubmit={handleSubmit}>
                  {/* Custom Drag and Drop Area */}
                  <div 
                    className={`border border-2 border-dashed rounded-3 p-4 text-center mb-3 position-relative transition-all ${dragActive ? 'border-primary bg-primary bg-opacity-10' : 'border-secondary-subtle'}`}
                    onDragEnter={handleDrag}
                    onDragOver={handleDrag}
                    onDragLeave={handleDrag}
                    onDrop={handleDrop}
                    style={{ cursor: 'pointer', backgroundColor: '#fafafa' }}
                  >
                    <input 
                      type="file" 
                      className="position-absolute top-0 start-0 w-100 h-100 opacity-0"
                      onChange={handleFileChange}
                      accept=".pdf, .png, .jpg, .jpeg"
                      style={{ cursor: 'pointer' }}
                    />
                    <i className="bi bi-cloud-arrow-up-fill text-primary display-5 mb-2 d-block"></i>
                    <p className="small text-muted mb-1 fw-semibold">
                      Drag & drop your report here
                    </p>
                    <p className="text-muted mb-0" style={{ fontSize: '0.75rem' }}>
                      Supports PDF, PNG, JPG
                    </p>
                  </div>

                  {/* Selected File Badge */}
                  {file && (
                    <div className="alert alert-info py-2 px-3 rounded-3 d-flex align-items-center justify-content-between mb-3 shadow-sm border-0">
                      <div className="d-flex align-items-center text-truncate">
                        <i className={`bi ${file.name.endsWith('.pdf') ? 'bi-file-earmark-pdf-fill text-danger' : 'bi-file-earmark-image-fill text-success'} me-2 fs-5`}></i>
                        <span className="small fw-medium text-truncate">{file.name}</span>
                      </div>
                      <button type="button" className="btn-close small" style={{ fontSize: '0.65rem' }} onClick={() => setFile(null)}></button>
                    </div>
                  )}

                  <button 
                    type="submit" 
                    className="btn btn-primary w-100 fw-bold py-2 shadow-sm d-flex align-items-center justify-content-center"
                    disabled={!file || loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Analyzing Pipeline...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-cpu-fill me-2"></i> Run AI Diagnostics
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>

            {/* System Specs Card */}
            <div className="card border-0 shadow-sm rounded-3 bg-dark text-white">
              <div className="card-body p-4">
                <h6 className="fw-bold text-info mb-3 d-flex align-items-center">
                  <i className="bi bi-activity me-2"></i> Pipeline Architecture
                </h6>
                <div className="d-flex flex-column gap-2" style={{ fontSize: '0.8rem' }}>
                  <div className="d-flex justify-content-between border-bottom border-secondary pb-1">
                    <span className="text-white-50">OCR Engine:</span>
                    <span className="font-monospace text-light">Gemini Vision/PyPDF</span>
                  </div>
                  <div className="d-flex justify-content-between border-bottom border-secondary pb-1">
                    <span className="text-white-50">Knowledge Base:</span>
                    <span className="font-monospace text-light">Pinecone Vector DB</span>
                  </div>
                  <div className="d-flex justify-content-between pb-1">
                    <span className="text-white-50">LLM Core:</span>
                    <span className="font-monospace text-light">Gemini-2.5-Flash</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT SIDE: Dynamic Display & Results Output */}
          <div className="col-lg-8" id="printable-area">
            
            {!loading && !aiSummary && (
              <div className="card border-0 shadow-sm rounded-3 text-center py-5 px-4 bg-white d-print-none">
                <div className="py-4">
                  <i className="bi bi-folder2-open display-2 text-muted mb-3 d-block"></i>
                  <h4 className="fw-bold text-dark">No Report Loaded</h4>
                  <p className="text-muted mx-auto" style={{ maxWidth: '420px' }}>
                    Upload a clinical lab report in the console sidebar to spin up the multi-agent parsing network.
                  </p>
                </div>
              </div>
            )}

            {loading && (
              <div className="card border-0 shadow-sm rounded-3 p-4 bg-white d-print-none">
                <div className="d-flex align-items-center mb-4">
                  <div className="spinner-grow text-primary me-3" role="status"></div>
                  <div>
                    <h5 className="fw-bold text-dark mb-0">Processing Document Streams</h5>
                    <p className="text-muted small mb-0">Running vector cross-examinations and compiling medically grounded output...</p>
                  </div>
                </div>
                <div className="placeholder-glow">
                  <span className="placeholder col-7 bg-secondary opacity-25 rounded mb-2 d-block" style={{ height: '24px' }}></span>
                  <span className="placeholder col-10 bg-secondary opacity-25 rounded mb-2 d-block"></span>
                  <span className="placeholder col-4 bg-secondary opacity-25 rounded mb-2 d-block"></span>
                  <span className="placeholder col-12 bg-secondary opacity-25 rounded mb-2 d-block" style={{ height: '100px' }}></span>
                </div>
              </div>
            )}

            {/* COMPLETED RESULTS VIEW */}
            {aiSummary && (
              <div className="card border-0 shadow-sm rounded-3 bg-white mb-4 overflow-hidden print-card">
                
                {/* Result Header WITH PDF BUTTON */}
                <div className="card-header bg-white border-bottom py-3 px-4 d-flex align-items-center justify-content-between">
                  <div>
                    <span className="badge bg-success-subtle text-success fw-bold text-uppercase mb-1 px-2 py-1" style={{ fontSize: '0.65rem' }}>
                      Verified JSON Extraction
                    </span>
                    <h5 className="fw-bold text-dark mb-0">Patient: {metadata?.patientName || 'Unknown'}</h5>
                  </div>
                  {/* EXPORT TO PDF BUTTON */}
                  <button 
                    onClick={() => window.print()} 
                    className="btn btn-sm btn-outline-primary fw-bold d-flex align-items-center shadow-sm d-print-none"
                  >
                    <i className="bi bi-printer-fill me-2"></i> Export Report
                  </button>
                </div>

                <div className="card-body p-4">
                  {/* STRUCTURED DATA TABLE */}
                  {metadata?.biomarkers && metadata.biomarkers.length > 0 && (
                    <div className="mb-4">
                      <h6 className="fw-bold text-secondary mb-3"><i className="bi bi-clipboard2-data me-2"></i>Extracted Biomarkers</h6>
                      <div className="table-responsive">
                        <table className="table table-hover table-bordered align-middle text-sm">
                          <thead className="table-light">
                            <tr>
                              <th>Test Name</th>
                              <th>Result</th>
                              <th>Normal Range</th>
                              <th>Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {metadata.biomarkers.map((marker, index) => (
                              <tr key={index}>
                                <td className="fw-medium text-dark">{marker.name}</td>
                                <td>{marker.value} {marker.unit}</td>
                                <td className="text-muted">{marker.range}</td>
                                <td>
                                  <span className={`badge ${marker.status === 'HIGH' ? 'bg-danger' : marker.status === 'LOW' ? 'bg-warning text-dark' : 'bg-success'}`}>
                                    {marker.status}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* AI SUMMARY EXPLANATION */}
                  <h6 className="fw-bold text-secondary mb-3 border-top pt-4"><i className="bi bi-chat-right-text me-2"></i>Clinical Explanation</h6>
                  <div 
                    className="text-secondary-emphasis"
                    dangerouslySetInnerHTML={{ __html: aiSummary }} 
                    style={{ lineHeight: '1.7', fontSize: '0.95rem' }}
                  />
                </div>

                {/* Secure Disclaimer Footer */}
                <div className="card-footer bg-light border-top p-3 px-4">
                  <div className="d-flex align-items-start text-muted" style={{ fontSize: '0.75rem' }}>
                    <i className="bi bi-exclamation-triangle-fill text-warning me-2 fs-6"></i>
                    <div>
                      <strong>Automated Analysis Framework:</strong> This synthesis is a contextually grounded transcription translation compiled via decentralized AI node architectures. It does not replace a physician's diagnostic cross-reference.
                    </div>
                  </div>
                </div>

              </div>
            )}

          </div>

        </div>
      </div>
    </div>
  );
}

export default App;