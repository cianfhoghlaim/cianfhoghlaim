import React, { useState, useEffect } from 'react';

const AdvancedSearch = ({ onSearch, loading }) => {
  const [searchMode, setSearchMode] = useState('semantic'); // 'semantic', 'shelfmark', 'keyword', or 'hybrid'
  const [shelfMarkQuery, setShelfMarkQuery] = useState('');
  const [semanticQuery, setSemanticQuery] = useState('');
  const [keywordQuery, setKeywordQuery] = useState('');
  const [hybridQuery, setHybridQuery] = useState('');
  const [exactMatch, setExactMatch] = useState(false);
  const [semanticWeight, setSemanticWeight] = useState(50);
  const [keywordWeight, setKeywordWeight] = useState(50);
  const [selectedIndex, setSelectedIndex] = useState('');
  const [availableIndices, setAvailableIndices] = useState([]);
  const [loadingIndices, setLoadingIndices] = useState(false);

  // Load available indices on component mount
  useEffect(() => {
    const loadIndices = async () => {
      setLoadingIndices(true);
      try {
        const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        console.log('Loading indices from:', `${API_BASE_URL}/indices`);
        
        const response = await fetch(`${API_BASE_URL}/indices`);
        console.log('Indices response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Indices data:', data);
          setAvailableIndices(data.indices || []);
          // Set default index if available
          if (data.indices && data.indices.length > 0) {
            const defaultIndex = data.indices.find(idx => idx.is_default);
            if (defaultIndex) {
              setSelectedIndex(defaultIndex.name);
            } else {
              setSelectedIndex(data.indices[0].name);
            }
          }
        } else {
          console.error('Failed to load indices:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Failed to load indices:', error);
      } finally {
        setLoadingIndices(false);
      }
    };

    loadIndices();
  }, []);

  const handleShelfMarkSearch = (e) => {
    e.preventDefault();
    if (!shelfMarkQuery.trim()) return;
    
    onSearch({
      mode: 'shelfmark',
      query: shelfMarkQuery.trim(),
      exactMatch: exactMatch,
      indexName: selectedIndex
    });
  };

  const handleSemanticSearch = (e) => {
    e.preventDefault();
    if (!semanticQuery.trim()) return;
    
    onSearch({
      mode: 'semantic',
      query: semanticQuery.trim(),
      indexName: selectedIndex
    });
  };

  const handleKeywordSearch = (e) => {
    e.preventDefault();
    if (!keywordQuery.trim()) return;
    
    onSearch({
      mode: 'keyword',
      query: keywordQuery.trim(),
      indexName: selectedIndex
    });
  };

  const handleHybridSearch = (e) => {
    e.preventDefault();
    if (!hybridQuery.trim()) return;
    
    onSearch({
      mode: 'hybrid',
      query: hybridQuery.trim(),
      semanticWeight: semanticWeight,
      keywordWeight: keywordWeight,
      indexName: selectedIndex
    });
  };

  const handleModeChange = (mode) => {
    setSearchMode(mode);
    // Clear the other queries when switching modes
    if (mode === 'shelfmark') {
      setSemanticQuery('');
      setKeywordQuery('');
      setHybridQuery('');
    } else if (mode === 'semantic') {
      setShelfMarkQuery('');
      setKeywordQuery('');
      setHybridQuery('');
    } else if (mode === 'keyword') {
      setShelfMarkQuery('');
      setSemanticQuery('');
      setHybridQuery('');
    } else if (mode === 'hybrid') {
      setShelfMarkQuery('');
      setSemanticQuery('');
      setKeywordQuery('');
    }
  };

  return (
    <div className="advanced-search">
      <div className="search-mode-selector">
        <h3>Advanced Search</h3>
        <div className="mode-tabs">
          <button
            className={`mode-tab ${searchMode === 'shelfmark' ? 'active' : ''}`}
            onClick={() => handleModeChange('shelfmark')}
          >
            📚 Shelf Mark Search
          </button>
          <button
            className={`mode-tab ${searchMode === 'keyword' ? 'active' : ''}`}
            onClick={() => handleModeChange('keyword')}
          >
            🔤 Keyword Search
          </button>
          <button
            className={`mode-tab ${searchMode === 'semantic' ? 'active' : ''}`}
            onClick={() => handleModeChange('semantic')}
          >
            🔍 Semantic Search
          </button>
          <button
            className={`mode-tab ${searchMode === 'hybrid' ? 'active' : ''}`}
            onClick={() => handleModeChange('hybrid')}
          >
            🔀 Hybrid Search
          </button>
        </div>
      </div>

      {/* Index Selection */}
      <div className="index-selector">
        <div className="index-selector-header">
          <h4>📊 Search Index</h4>
          <p>Choose which Elasticsearch index to search</p>
        </div>
        
        <div className="index-dropdown-container">
          <select
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value)}
            className="index-dropdown"
            disabled={loadingIndices || loading}
          >
            {loadingIndices ? (
              <option value="">Loading indices...</option>
            ) : (
              availableIndices.map((index) => (
                <option key={index.name} value={index.name}>
                  {index.name} {index.is_default ? '(Default)' : ''} - {index.document_count} docs
                </option>
              ))
            )}
          </select>
          
          {selectedIndex && !loadingIndices && (
            <div className="index-info">
              {(() => {
                const index = availableIndices.find(idx => idx.name === selectedIndex);
                return index ? (
                  <div className="index-details">
                    <span className="index-description">{index.description}</span>
                    <span className="index-stats">
                      {index.document_count.toLocaleString()} documents • {index.size}
                    </span>
                  </div>
                ) : null;
              })()}
            </div>
          )}
        </div>
      </div>

      {searchMode === 'shelfmark' && (
        <div className="shelfmark-search">
          <div className="search-description">
            <p>
              <strong>Find documents by their exact shelf mark or catalog number.</strong>
              <br />
              Examples: T-S 8J5.1, MS-TS-NS-144.1, Cambridge Or.1080 J2
            </p>
          </div>
          
          <form onSubmit={handleShelfMarkSearch} className="shelfmark-form">
            <div className="input-group">
              <input
                type="text"
                value={shelfMarkQuery}
                onChange={(e) => setShelfMarkQuery(e.target.value)}
                placeholder="Enter shelf mark (e.g., T-S 8J5.1)"
                className="shelfmark-input"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !shelfMarkQuery.trim()}
                className="search-button primary"
              >
                {loading ? 'Searching...' : 'Find Document'}
              </button>
            </div>
            
            <div className="search-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={exactMatch}
                  onChange={(e) => setExactMatch(e.target.checked)}
                />
                <span className="checkmark"></span>
                Exact match only
              </label>
              <div className="help-text">
                {exactMatch 
                  ? "Only documents with exactly this shelf mark will be returned"
                  : "Documents containing this shelf mark (partial matches) will be returned"
                }
              </div>
            </div>
          </form>
        </div>
      )}

      {searchMode === 'keyword' && (
        <div className="keyword-search">
          <div className="search-description">
            <p>
              <strong>Search by keywords and text content.</strong>
              <br />
              Find documents by searching for specific words or phrases in transcriptions, translations, and descriptions.
            </p>
          </div>
          
          <form onSubmit={handleKeywordSearch} className="keyword-form">
            <div className="input-group">
              <input
                type="text"
                value={keywordQuery}
                onChange={(e) => setKeywordQuery(e.target.value)}
                placeholder="Enter keywords or phrases to search for..."
                className="keyword-input"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !keywordQuery.trim()}
                className="search-button primary"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>
      )}

      {searchMode === 'semantic' && (
        <div className="semantic-search">
          <div className="search-description">
            <p>
              <strong>Search by meaning and content.</strong>
              <br />
              Find documents based on their content, themes, or concepts using AI-powered semantic search.
            </p>
          </div>
          
          <form onSubmit={handleSemanticSearch} className="semantic-form">
            <div className="input-group">
              <input
                type="text"
                value={semanticQuery}
                onChange={(e) => setSemanticQuery(e.target.value)}
                placeholder="Search for Hebrew manuscripts, marriage contracts, religious texts, responsa..."
                className="semantic-input"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !semanticQuery.trim()}
                className="search-button primary"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>
      )}

      {searchMode === 'hybrid' && (
        <div className="hybrid-search">
          <div className="search-description">
            <p>
              <strong>Combined semantic and keyword search.</strong>
              <br />
              Get the best of both worlds by combining AI-powered semantic understanding with traditional keyword matching.
            </p>
          </div>
          
          <form onSubmit={handleHybridSearch} className="hybrid-form">
            <div className="input-group">
              <input
                type="text"
                value={hybridQuery}
                onChange={(e) => setHybridQuery(e.target.value)}
                placeholder="Search for Hebrew manuscripts, marriage contracts, religious texts, responsa..."
                className="hybrid-input"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !hybridQuery.trim()}
                className="search-button primary"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
            
            <div className="weight-controls">
              <div className="weight-slider-group">
                <label className="weight-label">
                  <span>Semantic Weight: {semanticWeight}%</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={semanticWeight}
                    onChange={(e) => {
                      const newSemanticWeight = parseInt(e.target.value);
                      setSemanticWeight(newSemanticWeight);
                      setKeywordWeight(100 - newSemanticWeight);
                    }}
                    className="weight-slider"
                    disabled={loading}
                  />
                </label>
              </div>
              
              <div className="weight-slider-group">
                <label className="weight-label">
                  <span>Keyword Weight: {keywordWeight}%</span>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={keywordWeight}
                    onChange={(e) => {
                      const newKeywordWeight = parseInt(e.target.value);
                      setKeywordWeight(newKeywordWeight);
                      setSemanticWeight(100 - newKeywordWeight);
                    }}
                    className="weight-slider"
                    disabled={loading}
                  />
                </label>
              </div>
            </div>
            
            <div className="weight-info">
              <p>
                Adjust the weights to balance semantic understanding vs keyword matching. 
                Higher semantic weight finds conceptually related documents, while higher keyword weight finds exact text matches.
              </p>
            </div>
          </form>
        </div>
      )}

      <style jsx>{`
        .advanced-search {
          background: #fff;
          border-radius: 12px;
          padding: 24px;
          margin: 20px 0;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          border: 1px solid #e1e5e9;
        }

        .search-mode-selector h3 {
          margin: 0 0 16px 0;
          color: #2c3e50;
          font-size: 1.5rem;
          font-weight: 600;
        }

        .mode-tabs {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
          border-bottom: 2px solid #f1f3f4;
        }

        .mode-tab {
          padding: 12px 20px;
          border: none;
          background: transparent;
          color: #6c757d;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          border-radius: 8px 8px 0 0;
          transition: all 0.2s ease;
          position: relative;
        }

        .mode-tab:hover {
          background: #f8f9fa;
          color: #495057;
        }

        .mode-tab.active {
          background: #007bff;
          color: white;
          box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
        }

        .index-selector {
          background: #f8f9fa;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 20px;
          border: 1px solid #e1e5e9;
        }

        .index-selector-header h4 {
          margin: 0 0 4px 0;
          color: #2c3e50;
          font-size: 1.1rem;
          font-weight: 600;
        }

        .index-selector-header p {
          margin: 0 0 12px 0;
          color: #6c757d;
          font-size: 14px;
        }

        .index-dropdown-container {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .index-dropdown {
          padding: 10px 12px;
          border: 2px solid #e1e5e9;
          border-radius: 6px;
          font-size: 14px;
          background: white;
          cursor: pointer;
          transition: border-color 0.2s ease;
        }

        .index-dropdown:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .index-dropdown:disabled {
          background: #f8f9fa;
          cursor: not-allowed;
          opacity: 0.7;
        }

        .index-info {
          background: white;
          border-radius: 6px;
          padding: 12px;
          border: 1px solid #e1e5e9;
        }

        .index-details {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .index-description {
          font-size: 13px;
          color: #495057;
          font-weight: 500;
        }

        .index-stats {
          font-size: 12px;
          color: #6c757d;
        }

        .search-description {
          background: #f8f9fa;
          padding: 16px;
          border-radius: 8px;
          margin-bottom: 20px;
          border-left: 4px solid #007bff;
        }

        .search-description p {
          margin: 0;
          color: #495057;
          line-height: 1.5;
        }

        .input-group {
          display: flex;
          gap: 12px;
          margin-bottom: 16px;
        }

        .shelfmark-input,
        .keyword-input,
        .semantic-input,
        .hybrid-input {
          flex: 1;
          padding: 12px 16px;
          border: 2px solid #e1e5e9;
          border-radius: 8px;
          font-size: 16px;
          transition: border-color 0.2s ease;
        }

        .shelfmark-input:focus,
        .keyword-input:focus,
        .semantic-input:focus,
        .hybrid-input:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .search-button {
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .search-button.primary {
          background: #007bff;
          color: white;
        }

        .search-button.primary:hover:not(:disabled) {
          background: #0056b3;
          transform: translateY(-1px);
        }

        .search-button:disabled {
          background: #6c757d;
          cursor: not-allowed;
          transform: none;
        }

        .search-options {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;
        }

        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          font-size: 14px;
          color: #495057;
          font-weight: 500;
        }

        .checkbox-label input[type="checkbox"] {
          display: none;
        }

        .checkmark {
          width: 18px;
          height: 18px;
          background-color: #fff;
          border: 2px solid #dee2e6;
          border-radius: 3px;
          position: relative;
          transition: all 0.2s;
        }

        .checkbox-label input[type="checkbox"]:checked + .checkmark {
          background-color: #007bff;
          border-color: #007bff;
        }

        .checkbox-label input[type="checkbox"]:checked + .checkmark::after {
          content: '';
          position: absolute;
          left: 5px;
          top: 2px;
          width: 4px;
          height: 8px;
          border: solid white;
          border-width: 0 2px 2px 0;
          transform: rotate(45deg);
        }

        .help-text {
          font-size: 12px;
          color: #6c757d;
          font-style: italic;
          max-width: 300px;
        }

        .weight-controls {
          margin-top: 20px;
          padding: 16px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e1e5e9;
        }

        .weight-slider-group {
          margin-bottom: 16px;
        }

        .weight-slider-group:last-child {
          margin-bottom: 0;
        }

        .weight-label {
          display: flex;
          flex-direction: column;
          gap: 8px;
          font-size: 14px;
          font-weight: 500;
          color: #495057;
        }

        .weight-label span {
          font-weight: 600;
        }

        .weight-slider {
          width: 100%;
          height: 6px;
          border-radius: 3px;
          background: #e1e5e9;
          outline: none;
          -webkit-appearance: none;
          appearance: none;
        }

        .weight-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #007bff;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .weight-slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #007bff;
          cursor: pointer;
          border: 2px solid #fff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .weight-slider:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .weight-slider:disabled::-webkit-slider-thumb {
          cursor: not-allowed;
        }

        .weight-slider:disabled::-moz-range-thumb {
          cursor: not-allowed;
        }

        .weight-info {
          margin-top: 12px;
          padding: 12px;
          background: #e3f2fd;
          border-radius: 6px;
          border-left: 4px solid #2196f3;
        }

        .weight-info p {
          margin: 0;
          font-size: 13px;
          color: #1565c0;
          line-height: 1.4;
        }

        @media (max-width: 768px) {
          .advanced-search {
            padding: 16px;
            margin: 16px 0;
          }

          .input-group {
            flex-direction: column;
          }

          .search-button {
            width: 100%;
          }

          .mode-tabs {
            flex-direction: column;
            gap: 4px;
          }

          .mode-tab {
            border-radius: 8px;
            margin-bottom: 4px;
          }
        }
      `}</style>
    </div>
  );
};

export default AdvancedSearch;
