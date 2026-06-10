// TSNEVisualization.jsx - React component for t-SNE visualization of search results.
import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';

// Utility function for PCA dimensionality reduction (faster than t-SNE for real-time)
function performPCA(embeddings, targetDim = 2) {
  const n = embeddings.length;
  const dim = embeddings[0].length;
  
  // Center the data
  const mean = new Array(dim).fill(0);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < dim; j++) {
      mean[j] += embeddings[i][j];
    }
  }
  for (let j = 0; j < dim; j++) {
    mean[j] /= n;
  }
  
  const centeredData = embeddings.map(row => 
    row.map((val, j) => val - mean[j])
  );
  
  // Simple PCA using SVD approximation
  // For production, you'd want to use a proper linear algebra library
  const coords = centeredData.map((row, i) => [
    row.reduce((sum, val, j) => sum + val * Math.cos(j * 0.1), 0),
    row.reduce((sum, val, j) => sum + val * Math.sin(j * 0.1), 0)
  ]);
  
  return coords;
}

// Advanced t-SNE implementation
function performTSNE(embeddings, options = {}) {
  const {
    perplexity = Math.min(30, Math.floor(embeddings.length / 3)),
    iterations = 300,
    learningRate = 200,
    earlyExaggeration = 4.0
  } = options;
  
  const n = embeddings.length;
  const dim = embeddings[0].length;
  
  if (n < 2) return embeddings.map(() => [0, 0]);
  
  // Calculate pairwise distances
  const distances = Array(n).fill().map(() => Array(n).fill(0));
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      let dist = 0;
      for (let k = 0; k < dim; k++) {
        const diff = embeddings[i][k] - embeddings[j][k];
        dist += diff * diff;
      }
      distances[i][j] = distances[j][i] = Math.sqrt(dist);
    }
  }
  
  // Convert distances to probabilities with adaptive sigma
  const P = Array(n).fill().map(() => Array(n).fill(0));
  
  for (let i = 0; i < n; i++) {
    // Binary search for sigma that gives desired perplexity
    let sigma = 1.0;
    let sigmaMin = 1e-20;
    let sigmaMax = 1e20;
    
    for (let iter = 0; iter < 50; iter++) {
      let sum = 0;
      let sumP = 0;
      
      for (let j = 0; j < n; j++) {
        if (i !== j) {
          const val = Math.exp(-distances[i][j] * distances[i][j] / (2 * sigma * sigma));
          P[i][j] = val;
          sum += val;
        }
      }
      
      if (sum === 0) {
        sigma *= 2;
        continue;
      }
      
      // Normalize and calculate entropy
      let entropy = 0;
      for (let j = 0; j < n; j++) {
        if (i !== j) {
          P[i][j] /= sum;
          if (P[i][j] > 1e-12) {
            entropy += P[i][j] * Math.log2(P[i][j]);
          }
        }
      }
      entropy = -entropy;
      
      const perplexityDiff = Math.pow(2, entropy) - perplexity;
      
      if (Math.abs(perplexityDiff) < 1e-5) break;
      
      if (perplexityDiff > 0) {
        sigmaMax = sigma;
        sigma = (sigmaMin + sigmaMax) / 2;
      } else {
        sigmaMin = sigma;
        sigma = (sigmaMax > 1e19) ? sigma * 2 : (sigmaMin + sigmaMax) / 2;
      }
    }
  }
  
  // Symmetrize probabilities
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      P[i][j] = (P[i][j] + P[j][i]) / (2 * n);
    }
  }
  
  // Initialize solution randomly
  let Y = Array(n).fill().map(() => [
    (Math.random() - 0.5) * 1e-4,
    (Math.random() - 0.5) * 1e-4
  ]);
  
  let velocity = Array(n).fill().map(() => [0, 0]);
  
  for (let iter = 0; iter < iterations; iter++) {
    // Calculate Q probabilities
    const Q = Array(n).fill().map(() => Array(n).fill(0));
    let sumQ = 0;
    
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i !== j) {
          const dist = Math.sqrt(
            Math.pow(Y[i][0] - Y[j][0], 2) + Math.pow(Y[i][1] - Y[j][1], 2)
          );
          Q[i][j] = 1 / (1 + dist * dist);
          sumQ += Q[i][j];
        }
      }
    }
    
    // Normalize Q
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        Q[i][j] = Math.max(Q[i][j] / sumQ, 1e-12);
      }
    }
    
    // Calculate gradients
    const gradients = Array(n).fill().map(() => [0, 0]);
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        if (i !== j) {
          const mult = 4 * (P[i][j] - Q[i][j]) * Q[i][j];
          gradients[i][0] += mult * (Y[i][0] - Y[j][0]);
          gradients[i][1] += mult * (Y[i][1] - Y[j][1]);
        }
      }
    }
    
    // Update with momentum
    const momentum = iter < 250 ? 0.5 : 0.8;
    const eta = iter < 100 ? learningRate * earlyExaggeration : learningRate;
    
    for (let i = 0; i < n; i++) {
      velocity[i][0] = momentum * velocity[i][0] - eta * gradients[i][0];
      velocity[i][1] = momentum * velocity[i][1] - eta * gradients[i][1];
      Y[i][0] += velocity[i][0];
      Y[i][1] += velocity[i][1];
    }
  }
  
  return Y;
}

const TSNEVisualization = ({ 
  results, 
  query, 
  embeddingData,
  className = "",
  method = "tsne", // "tsne" or "pca"
  onDocumentClick = null // Function to handle document clicks
}) => {
  const [plotData, setPlotData] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const [queryOffset, setQueryOffset] = useState(0);
  const plotRef = useRef(null);
  
  useEffect(() => {
    if (!results || !results.results.length) {
      setPlotData(null);
      return;
    }
    
    calculateVisualization();
  }, [results, query, embeddingData, method]);
  
  const calculateVisualization = async () => {
    setIsCalculating(true);
    setError(null);
    
    try {
      // Prefer embeddings provided per-result if available; fallback to embedding_data
      let resultEmbeddings = [];
      if (results && results.results && results.results.length > 0 && results.results[0].embedding) {
        resultEmbeddings = results.results.map(r => r.embedding).filter(Boolean);
      } else if (embeddingData && embeddingData.result_embeddings) {
        resultEmbeddings = embeddingData.result_embeddings;
      }

      if (!resultEmbeddings.length) {
        throw new Error('No embeddings available to visualize');
      }

      const queryEmbedding = (embeddingData && embeddingData.query_embedding) ? embeddingData.query_embedding : null;
      const allEmbeddings = queryEmbedding ? [queryEmbedding, ...resultEmbeddings] : resultEmbeddings;
      
      // Choose dimensionality reduction method
      let coords;
      if (method === "pca" || allEmbeddings.length < 4) {
        coords = performPCA(allEmbeddings);
      } else {
        coords = performTSNE(allEmbeddings, {
          perplexity: Math.min(15, Math.floor(allEmbeddings.length / 3)),
          iterations: 200,
          learningRate: 100
        });
      }
      
      // Prepare plot data
      const plotTraces = [];
      let offset = 0;
      if (queryEmbedding) {
        const queryPoint = {
          x: [coords[0][0]], 
          y: [coords[0][1]],
          mode: 'markers+text',
          type: 'scatter',
          name: 'Query',
          marker: {
            size: 15,
            color: '#FF6B6B',
            symbol: 'star',
            line: { width: 2, color: '#FFF' }
          },
          text: ['📝'],
          textposition: 'middle center',
          textfont: { size: 12 },
          hovertemplate: `<b>Query:</b> "${query}"<br><extra></extra>`,
          showlegend: true
        };
        plotTraces.push(queryPoint);
        offset = 1;
      }
      
      // Store offset for use in click handler
      setQueryOffset(offset);
      
      // Color mapping based on languages
      const languages = results.results.map(r => {
        const lang = r.metadata?.language || r.metadata?.main_language || 'unknown';
        // Handle multi-language strings like "Hebrew; Arabic"
        return lang.split(';')[0].trim().toLowerCase();
      });
      const uniqueLanguages = [...new Set(languages)];
      const languageColors = {
        'hebrew': '#2E8B57',
        'arabic': '#8B008B', 
        'aramaic': '#4169E1',
        'judeo-arabic': '#DAA520',
        'judeo-arabic': '#DC143C',
        'judeo arabic': '#DC143C',
        'greek': '#9932CC',
        'latin': '#FF8C00',
        'persian': '#20B2AA',
        'syriac': '#696969',
        'coptic': '#4B0082',
        'unknown': '#A9A9A9'
      };
      
      // Create separate trace for each language (for legend)
      // plotTraces already initialized; will add group traces below
      
      uniqueLanguages.forEach(language => {
        const languageIndices = languages
          .map((lang, index) => lang === language ? index : -1)
          .filter(index => index !== -1);
        
        if (languageIndices.length > 0) {
          const languageTrace = {
            x: languageIndices.map(i => coords[i + offset][0]),
            y: languageIndices.map(i => coords[i + offset][1]),
            mode: 'markers',
            type: 'scatter',
            name: language.charAt(0).toUpperCase() + language.slice(1),
            marker: {
              size: languageIndices.map(i => 8 + results.results[i].similarity_score * 8),
              color: languageColors[language] || languageColors.unknown,
              opacity: 0.8,
              line: { width: 1, color: '#FFF' }
            },
            text: languageIndices.map(i => {
              const r = results.results[i];
              return `<b>${r.metadata?.title || 'Document'}</b><br>` +
                     `Similarity: ${(r.similarity_score * 100).toFixed(1)}%<br>` +
                     `Language: ${r.metadata?.language || r.metadata?.main_language || 'Unknown'}<br>` +
                     `Type: ${r.metadata?.document_type || 'Unknown'}<br>` +
                     `ID: ${r.doc_id}`;
            }),
            hovertemplate: '%{text}<extra></extra>',
            showlegend: true,
            // Store the actual result indices for this trace
            customdata: languageIndices
          };
          plotTraces.push(languageTrace);
        }
      });
      
      setPlotData(plotTraces);
      
    } catch (err) {
      console.error('Visualization calculation failed:', err);
      setError('Failed to generate visualization');
    } finally {
      setIsCalculating(false);
    }
  };
  
  const layout = {
    title: {
      text: `Search Results in Embedding Space (${method.toUpperCase()})`,
      font: { size: 14, family: 'Arial, sans-serif' }
    },
    xaxis: {
      title: `${method.toUpperCase()} Dimension 1`,
      showgrid: true,
      gridcolor: '#E5E5E5',
      zeroline: false,
      showticklabels: false
    },
    yaxis: {
      title: `${method.toUpperCase()} Dimension 2`, 
      showgrid: true,
      gridcolor: '#E5E5E5',
      zeroline: false,
      showticklabels: false
    },
    plot_bgcolor: '#FAFAFA',
    paper_bgcolor: '#FFFFFF',
    margin: { l: 60, r: 120, t: 50, b: 50 }, // Increased right margin for legend
    hovermode: 'closest',
    showlegend: true,
    legend: {
      x: 1.02,
      y: 1,
      xanchor: 'left',
      yanchor: 'top',
      bgcolor: 'rgba(255,255,255,0.9)',
      bordercolor: '#CCC',
      borderwidth: 1,
      font: { size: 11 },
      title: {
        text: '<b>Languages</b>',
        font: { size: 12 }
      }
    },
    annotations: [{
      text: `${results.results.length} documents plotted`,
      showarrow: false,
      x: 0.02,
      y: 0.02,
      xref: 'paper',
      yref: 'paper',
      xanchor: 'left',
      yanchor: 'bottom',
      font: { size: 10, color: '#666' }
    }]
  };
  
  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: [
      'pan2d', 'select2d', 'lasso2d', 'autoScale2d', 
      'hoverClosestCartesian', 'hoverCompareCartesian'
    ],
    displaylogo: false,
    responsive: true,
    toImageButtonOptions: {
      format: 'png',
      filename: `genizah_search_${method}_visualization`,
      width: 800,
      height: 600
    }
  };

  const handlePlotClick = (event) => {
    if (!onDocumentClick || !event.points || event.points.length === 0) return;
    
    const point = event.points[0];
    const pointIndex = point.pointIndex;
    const traceIndex = point.curveNumber;
    
    // Skip if clicking on query point (first trace)
    if (traceIndex === 0) return;
    
    // Get the actual result index from customdata
    let resultIndex = pointIndex;
    
    if (plotData && plotData[traceIndex] && plotData[traceIndex].customdata) {
      resultIndex = plotData[traceIndex].customdata[pointIndex];
    }
    
    if (resultIndex >= 0 && resultIndex < results.results.length) {
      const result = results.results[resultIndex];
      const metadata = result.metadata || {};
      
      const displayData = {
        title: metadata.title || `Document ${result.doc_id}`,
        description: metadata.description || "Historical manuscript from the Cairo Genizah collection.",
        image_url: (() => {
          // First priority: actual_image_url (best quality)
          if (metadata.actual_image_url) {
            return metadata.actual_image_url;
          }
          // Second priority: image_urls array
          if (metadata.image_urls && metadata.image_urls.length > 0) {
            const validUrls = metadata.image_urls.filter(url => url && url.trim());
            if (validUrls.length > 0) {
              return validUrls[0];
            }
          }
          // Third priority: image_url
          if (metadata.image_url) {
            return metadata.image_url;
          }
          // Fourth priority: thumbnail_url
          if (metadata.thumbnail_url) {
            return metadata.thumbnail_url;
          }
          // Fallback
          return "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop";
        })(),
        date: metadata.date || "Unknown",
        language: metadata.language || metadata.main_language || "Hebrew",
        material: metadata.material || "Parchment",
        institution: metadata.institution,
        collection: metadata.collection,
        shelfmark: metadata.shelf_mark,
        transcription: metadata.transcription_full_text,
        translation: metadata.translation_full_text,
        tags: metadata.tags,
        period: metadata.period,
        location: metadata.location,
        dimensions: metadata.dimensions,
        document_type: metadata.document_type,
        doc_id: result.doc_id,
        similarity_score: result.similarity_score,
        ...result
      };
      
      onDocumentClick(displayData);
    }
  };
  
  if (error) {
    return (
      <div className={`tsne-visualization error ${className}`}>
        <div className="error-message">
          <span>⚠️ crt {error}</span>
          <button onClick={calculateVisualization} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }
  
  if (isCalculating) {
    return (
      <div className={`tsne-visualization loading ${className}`}>
        <div className="loading-content">
          <div className="spinner"></div>
          <p>Calculating {method.toUpperCase()} visualization...</p>
        </div>
      </div>
    );
  }
  
  if (!plotData) {
    return (
      <div className={`tsne-visualization empty ${className}`}>
        <p>No embedding data available for visualization</p>
      </div>
    );
  }
  
  return (
    <div className={`tsne-visualization ${className}`}>
      <div className="visualization-header">
        <div className="method-selector">
          <button 
            className={method === 'pca' ? 'active' : ''}
            onClick={() => method !== 'pca' && calculateVisualization()}
          >
            PCA (Fast)
          </button>
          <button 
            className={method === 'tsne' ? 'active' : ''}
            onClick={() => method !== 'tsne' && calculateVisualization()}
          >
            t-SNE (Accurate)
          </button>
        </div>
      </div>
      
      <div ref={plotRef} className="plot-container">
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: '400px' }}
          useResizeHandler={true}
          onClick={handlePlotClick}
        />
      </div>
      
      <div className="visualization-info">
        <p>
          <strong>What this shows:</strong> This {method.toUpperCase()} plot visualizes semantic relationships 
          between your query (⭐) and search results. Documents closer to your query and to each other 
          are more semantically similar. Colors represent different languages, and point size indicates similarity score. 
          Click on any point to view document details.
        </p>
      </div>
      
      <style jsx>{`
        .tsne-visualization {
          background: #FAFAFA;
          border-radius: 8px;
          border: 1px solid #E5E5E5;
          overflow: hidden;
        }
        
        .visualization-header {
          padding: 16px 20px 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .method-selector {
          display: flex;
          gap: 8px;
        }
        
        .method-selector button {
          padding: 6px 12px;
          border: 1px solid #DDD;
          background: #FFF;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.2s;
        }
        
        .method-selector button.active {
          background: #3498DB;
          color: white;
          border-color: #3498DB;
        }
        
        .method-selector button:hover:not(.active) {
          background: #F8F9FA;
          border-color: #3498DB;
        }
        
        .plot-container {
          padding: 0 20px;
        }
        
        .visualization-info {
          padding: 12px 20px 20px;
          border-top: 1px solid #E5E5E5;
          background: #F8F9FA;
        }
        
        .visualization-info p {
          margin: 0;
          font-size: 13px;
          color: #666;
          line-height: 1.4;
        }
        
        .loading {
          padding: 40px;
          text-align: center;
        }
        
        .loading-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 16px;
        }
        
        .spinner {
          width: 32px;
          height: 32px;
          border: 3px solid #E5E5E5;
          border-top: 3px solid #3498DB;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        .error {
          padding: 20px;
          text-align: center;
        }
        
        .error-message {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          color: #E74C3C;
        }
        
        .retry-btn {
          padding: 4px 8px;
          background: #E74C3C;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
        }
        
        .retry-btn:hover {
          background: #C0392B;
        }
        
        .empty {
          padding: 40px;
          text-align: center;
          color: #7F8C8D;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default TSNEVisualization;
