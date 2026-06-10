// VisualizationExplorer.jsx - Full-page visualization explorer for the Cairo Genizah collection
// Refactored to use backend Python libraries (scikit-learn, umap-learn) instead of JavaScript implementations
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Plot from 'react-plotly.js';

const VisualizationExplorer = ({ onDocumentClick = null }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [documents, setDocuments] = useState(null);
  const [plotData, setPlotData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const [method, setMethod] = useState('tsne');
  const [colorBy, setColorBy] = useState('language');
  const [numDocuments, setNumDocuments] = useState(1000);
  const [loadFullIndex, setLoadFullIndex] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [availableIndices, setAvailableIndices] = useState([]);
  const [umapParams, setUmapParams] = useState({
    nNeighbors: 15,
    minDist: 0.1,
    iterations: 300
  });
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [similarityMatrix, setSimilarityMatrix] = useState(null);
  const [showSimilarityMatrix, setShowSimilarityMatrix] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [queryPoints, setQueryPoints] = useState([]); // Array of query points
  const [isProjectingQuery, setIsProjectingQuery] = useState(false);
  const [selectedQueryIndex, setSelectedQueryIndex] = useState(null); // Index of selected query for showing neighbors
  const [isFullIndexMode, setIsFullIndexMode] = useState(false);
  const plotRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Compute cosine similarity between two vectors
  const cosineSimilarity = (a, b) => {
    if (a.length !== b.length) return 0;

    let dotProduct = 0;
    let normA = 0;
    let normB = 0;

    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    if (normA === 0 || normB === 0) return 0;

    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  };

  // Compute similarity matrix for selected documents.
  const computeSimilarityMatrix = () => {
    if (selectedDocuments.length < 2) return;

    const embeddings = selectedDocuments.map(doc => doc.embedding).filter(Boolean);
    if (embeddings.length !== selectedDocuments.length) {
      alert('Some selected documents are missing embeddings');
      return;
    }

    const matrix = [];
    for (let i = 0; i < embeddings.length; i++) {
      const row = [];
      for (let j = 0; j < embeddings.length; j++) {
        if (i === j) {
          row.push(1.0); // Self-similarity
        } else {
          row.push(cosineSimilarity(embeddings[i], embeddings[j]));
        }
      }
      matrix.push(row);
    }

    setSimilarityMatrix(matrix);
    setShowSimilarityMatrix(true);
  };

  // Handle document selection from plot
  const handlePlotSelection = (event) => {
    if (!event.points || event.points.length === 0) return;

    const selectedIndices = event.points.map(point => {
      const traceIndex = point.curveNumber;
      const pointIndex = point.pointIndex;

      if (plotData && plotData[traceIndex] && plotData[traceIndex].customdata) {
        return plotData[traceIndex].customdata[pointIndex];
      }
      return pointIndex;
    });

    const selectedDocs = selectedIndices.map(index => documents.results[index]).filter(Boolean);
    setSelectedDocuments(selectedDocs);
  };

  // Clear selection
  const clearSelection = () => {
    setSelectedDocuments([]);
    setSimilarityMatrix(null);
    setShowSimilarityMatrix(false);
  };

  // Generate a unique color for each query
  const getQueryColor = (index) => {
    const colors = [
      '#FF6B6B', // Red
      '#4ECDC4', // Teal
      '#45B7D1', // Blue
      '#FFA07A', // Light Salmon
      '#98D8C8', // Mint
      '#F7DC6F', // Yellow
      '#BB8FCE', // Purple
      '#85C1E2', // Sky Blue
      '#F8B739', // Orange
      '#52BE80', // Green
    ];
    return colors[index % colors.length];
  };

  // Project query onto visualization
  const projectQuery = async () => {
    if (!queryText.trim() || !documents || !plotData) {
      return;
    }

    setIsProjectingQuery(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/visualization-explorer/project-query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryText,
          method: method,
          n_neighbors: 10
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to project query');
      }

      const result = await response.json();

      // Create new query point with unique ID
      const newQueryPoint = {
        id: Date.now(), // Use timestamp as unique ID
        x: result.coordinates.x,
        y: result.coordinates.y,
        text: result.query,
        method: result.method,
        nearestNeighbors: result.nearest_neighbors
          .map(nn => {
            if (nn.index >= 0 && nn.index < documents.results.length) {
              return {
                ...documents.results[nn.index],
                similarity: nn.similarity
              };
            }
            return null;
          })
          .filter(Boolean)
      };

      // Add to query points array and select the newly added query
      setQueryPoints(prev => {
        const updated = [...prev, newQueryPoint];
        setSelectedQueryIndex(prev.length); // Select the newly added query
        return updated;
      });

      // Clear input
      setQueryText('');

    } catch (err) {
      console.error('Query projection failed:', err);
      setError({
        message: err.message || 'Failed to project query onto visualization',
        type: 'projection'
      });
    } finally {
      setIsProjectingQuery(false);
    }
  };

  // Clear all query projections
  const clearAllQueries = () => {
    setQueryPoints([]);
    setSelectedQueryIndex(null);
    setQueryText('');
  };

  // Clear a specific query.
  const clearQuery = (queryId) => {
    setQueryPoints(prev => {
      const filtered = prev.filter(qp => qp.id !== queryId);
      // Adjust selected index if needed
      if (selectedQueryIndex !== null && selectedQueryIndex >= filtered.length) {
        setSelectedQueryIndex(filtered.length > 0 ? filtered.length - 1 : null);
      }
      return filtered;
    });
  };

  // Fetch available indices on component mount
  useEffect(() => {
    const fetchIndices = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/indices`);
        const data = await response.json();

        if (data.indices && data.indices.length > 0) {
          setAvailableIndices(data.indices);
          // Set default index if available
          if (data.default_index && data.indices.some(idx => idx.name === data.default_index)) {
            setSelectedIndex(data.default_index);
          } else if (data.indices.length > 0) {
            setSelectedIndex(data.indices[0].name);
          }
        }
      } catch (err) {
        console.error('Failed to fetch indices:', err);
      }
    };

    fetchIndices();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Check for navigation state to load full index automatically
  useEffect(() => {
    if (location.state?.loadFullIndex && !documents && !isLoading) {
      // Clear state to prevent reloading on re-renders if we wanted, 
      // but for now just loading is fine.
      loadPrecomputedFullIndex();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  const loadDocuments = async () => {
    setIsLoading(true);
    setError(null);
    setIsFullIndexMode(false);

    try {
      const requestBody = {
        num_documents: numDocuments,
        load_full_index: loadFullIndex,
        include_embeddings: true,
        index_name: selectedIndex || undefined
      };

      const response = await fetch(`${API_BASE_URL}/visualization-explorer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();

      if (response.ok) {
        setDocuments(data);
        calculateVisualization(data);
      } else {
        setError({
          message: data.detail || 'Failed to load documents',
          type: 'api'
        });
      }
    } catch (err) {
      setError({
        message: 'Network error. Please check your connection and try again.',
        type: 'network'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadPrecomputedFullIndex = async () => {
    setIsLoading(true);
    setError(null);
    setLoadFullIndex(true);
    setIsFullIndexMode(true);

    try {
      const idxParam = selectedIndex ? `?index_name=${encodeURIComponent(selectedIndex)}` : '';
      const response = await fetch(`${API_BASE_URL}/visualization-explorer/full-index${idxParam}`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to load full index visualization');
      }

      // Yield to main thread to allow loading spinner to render before heavy JSON parsing
      await new Promise(resolve => setTimeout(resolve, 50));

      const data = await response.json();

      // Transform data to match expected format
      const transformedDocuments = {
        count: data.count,
        results: data.documents.map(doc => ({
          doc_id: doc.doc_id,
          metadata: doc.metadata,
          similarity_score: 1.0 // Default for full index
        })),
        embedding_data: {
          dimension: 0, // Not needed for pre-computed
          tsne: data.documents.map(doc => doc.tsne),
          umap: data.documents.map(doc => doc.umap)
        }
      };

      setDocuments(transformedDocuments);

      // Set plot data immediately
      visualizePrecomputed(transformedDocuments, method);

    } catch (err) {
      console.error('Failed to load full index:', err);
      setError({
        message: err.message || 'Failed to load full index visualization. Please try again later.',
        type: 'load'
      });
      // Only reset if it was a genuine failure, not a cancellation
      if (err.name !== 'AbortError') {
        setLoadFullIndex(false);
        setIsFullIndexMode(false);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const visualizePrecomputed = (data, currentMethod) => {
    if (!data || !data.results) return;

    let coords = [];

    // Try to get coordinates from embedding_data first (new format)
    if (data.embedding_data) {
      if (currentMethod === 'tsne' && data.embedding_data.tsne) {
        coords = data.embedding_data.tsne;
      } else if (currentMethod === 'umap' && data.embedding_data.umap) {
        coords = data.embedding_data.umap;
      }
    }

    // Fallback to checking individual results (legacy format)
    if (!coords || coords.length === 0) {
      coords = data.results.map(doc => {
        if (currentMethod === 'tsne') return doc.tsne_coords;
        if (currentMethod === 'umap') return doc.umap_coords;
        return null;
      }).filter(Boolean);
    }

    if (!coords || coords.length === 0) {
      console.warn(`No coordinates found for method ${currentMethod} in pre-computed data`);
      // Do NOT fallback to calculateVisualization here as it will fail without embeddings
      // Just return or show a toast
      setError({
        message: `No pre-computed ${currentMethod.toUpperCase()} coordinates available for this index.`,
        type: 'visualization'
      });
      return;
    }

    // Generate color mapping based on selected attribute
    const colorMapping = generateColorMapping(data.results, colorBy);

    // Create plot traces
    const plotTraces = [];

    Object.entries(colorMapping).forEach(([category, indices]) => {
      if (indices.length > 0) {
        const trace = {
          x: indices.map(i => coords[i][0]),
          y: indices.map(i => coords[i][1]),
          mode: 'markers',
          type: 'scatter',
          name: category,
          marker: {
            size: 5, // Slightly smaller for full index
            color: getColorForCategory(category, colorBy),
            opacity: 0.6,
            line: { width: 0 } // No border for performance
          },
          text: indices.map(i => {
            const doc = data.results[i];
            const metadata = doc.metadata || {};
            return `<b>${metadata.title || 'Document'}</b><br>` +
              `Language: ${metadata.language || metadata.main_language || 'Unknown'}<br>` +
              `Type: ${metadata.document_type || 'Unknown'}<br>` +
              `Collection: ${metadata.collection || 'Unknown'}<br>` +
              `ID: ${doc.doc_id}`;
          }),
          hovertemplate: '%{text}<extra></extra>',
          showlegend: true,
          customdata: indices
        };
        plotTraces.push(trace);
      }
    });

    setPlotData(plotTraces);
  };

  const calculateVisualization = async (data = documents) => {
    if (!data || !data.results.length) return;

    // If we are in full index mode, use pre-computed coordinates
    if (isFullIndexMode) {
      visualizePrecomputed(data, method);
      return;
    }

    setIsCalculating(true);
    setError(null);

    try {
      const embeddings = data.results.map(r => r.embedding).filter(Boolean);

      if (!embeddings.length) {
        throw new Error('No embeddings available for visualization');
      }

      // Prepare request body based on method
      const requestBody = {
        embeddings: embeddings,
        method: method,
        random_state: 42
      };

      // Add method-specific parameters
      if (method === 'pca') {
        requestBody.n_components = 2;
      } else if (method === 'tsne') {
        // Auto-calculate perplexity if not set
        const autoPerplexity = Math.min(30, Math.floor(embeddings.length / 3));
        requestBody.perplexity = autoPerplexity;
        requestBody.n_iter = 1000;
        requestBody.learning_rate = 200.0;
        requestBody.early_exaggeration = 12.0;
      } else if (method === 'umap') {
        requestBody.n_neighbors = Math.min(umapParams.nNeighbors, Math.floor(embeddings.length / 3));
        requestBody.min_dist = umapParams.minDist;
        requestBody.n_components = 2;
        requestBody.metric = 'cosine';
      }

      // Call backend endpoint for visualization calculation
      const response = await fetch(`${API_BASE_URL}/visualization-explorer/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to calculate visualization');
      }

      const result = await response.json();
      const coords = result.coordinates;

      if (!coords || coords.length !== embeddings.length) {
        throw new Error('Invalid coordinates returned from backend');
      }

      // Generate color mapping based on selected attribute
      const colorMapping = generateColorMapping(data.results, colorBy);

      // Create plot traces
      const plotTraces = [];

      Object.entries(colorMapping).forEach(([category, indices]) => {
        if (indices.length > 0) {
          const trace = {
            x: indices.map(i => coords[i][0]),
            y: indices.map(i => coords[i][1]),
            mode: 'markers',
            type: 'scatter',
            name: category,
            marker: {
              size: 6,
              color: getColorForCategory(category, colorBy),
              opacity: 0.7,
              line: { width: 0.5, color: '#FFF' }
            },
            text: indices.map(i => {
              const doc = data.results[i];
              const metadata = doc.metadata || {};
              return `<b>${metadata.title || 'Document'}</b><br>` +
                `Language: ${metadata.language || metadata.main_language || 'Unknown'}<br>` +
                `Type: ${metadata.document_type || 'Unknown'}<br>` +
                `Collection: ${metadata.collection || 'Unknown'}<br>` +
                `ID: ${doc.doc_id}`;
            }),
            hovertemplate: '%{text}<extra></extra>',
            showlegend: true,
            customdata: indices
          };
          plotTraces.push(trace);
        }
      });

      // Add all query points that match current method
      queryPoints.forEach((qp, originalIndex) => {
        if (qp.method === method) {
          const queryTrace = {
            x: [qp.x],
            y: [qp.y],
            mode: 'markers',
            type: 'scatter',
            name: `Query ${originalIndex + 1}: ${qp.text.substring(0, 30)}${qp.text.length > 30 ? '...' : ''}`,
            marker: {
              size: 30,
              color: getQueryColor(originalIndex),
              symbol: 'star',
              line: { width: 3, color: '#FFFFFF' },
              opacity: 1.0
            },
            hovertemplate: `<b>Query ${originalIndex + 1}: ${qp.text}</b><br>` +
              `Coordinates: (${qp.x.toFixed(3)}, ${qp.y.toFixed(3)})<extra></extra>`,
            showlegend: true,
            customdata: [qp.id] // Store query ID for identification
          };
          plotTraces.push(queryTrace);
        }
      });

      setPlotData(plotTraces);

    } catch (err) {
      console.error('Visualization calculation failed:', err);
      setError({
        message: err.message || 'Failed to generate visualization',
        type: 'calculation'
      });
    } finally {
      setIsCalculating(false);
    }
  };

  const generateColorMapping = (results, attribute) => {
    const mapping = {};

    results.forEach((result, index) => {
      let value = 'Unknown';

      switch (attribute) {
        case 'language':
          value = result.metadata?.language || result.metadata?.main_language || 'Unknown';
          break;
        case 'document_type':
          value = result.metadata?.document_type || 'Unknown';
          break;
        case 'collection':
          value = result.metadata?.collection || 'Unknown';
          break;
        case 'institution':
          value = result.metadata?.institution || 'Unknown';
          break;
        case 'period':
          value = result.metadata?.period || 'Unknown';
          break;
        case 'material':
          value = result.metadata?.material || 'Unknown';
          break;
        case 'material':
          value = result.metadata?.material || 'Unknown';
          break;
        case 'title':
          value = result.metadata?.title || 'Unknown';
          break;
        case 'author':
          value = result.metadata?.author || (result.metadata?.authors && result.metadata.authors[0]) || 'Unknown';
          break;
        default:
          value = 'Unknown';
      }

      // Handle multi-value strings (e.g., "Hebrew; Arabic")
      const primaryValue = value.split(';')[0].trim();

      if (!mapping[primaryValue]) {
        mapping[primaryValue] = [];
      }
      mapping[primaryValue].push(index);
    });

    return mapping;
  };

  // Generate a consistent color from a string using hash
  const generateColorFromString = (str) => {
    // Simple hash function
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Use HSL color space for better color distribution
    // Hue: 0-360 (full spectrum)
    // Saturation: 60-90% (vibrant but not too intense)
    // Lightness: 45-65% (visible but not too dark/light)
    const hue = Math.abs(hash) % 360;
    const saturation = 60 + (Math.abs(hash * 7) % 30); // 60-90%
    const lightness = 45 + (Math.abs(hash * 11) % 20); // 45-65%

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  const getColorForCategory = (category, attribute) => {
    const colorPalettes = {
      language: {
        'Hebrew': '#2E8B57',
        'Arabic': '#8B008B',
        'Aramaic': '#4169E1',
        'Judeo-Arabic': '#DAA520',
        'Judaeo-Arabic': '#DAA520', // Alternative spelling
        'Greek': '#9932CC',
        'Latin': '#FF8C00',
        'Persian': '#20B2AA',
        'Syriac': '#696969',
        'Coptic': '#4B0082',
        'Unknown': '#A9A9A9'
      },
      document_type: {
        'legal': '#E74C3C',
        'liturgical': '#3498DB',
        'literary': '#2ECC71',
        'commercial': '#F39C12',
        'personal': '#9B59B6',
        'religious': '#1ABC9C',
        'administrative': '#34495E',
        'Unknown': '#A9A9A9'
      },
      collection: {
        'taylor_schechter': '#E74C3C',
        'adler': '#3498DB',
        'gottheil_worrell': '#2ECC71',
        'cambridge': '#F39C12',
        'princeton': '#9B59B6',
        'jts': '#1ABC9C',
        'Unknown': '#A9A9A9'
      },
      institution: {
        'cambridge': '#E74C3C',
        'jewish_theological_seminary': '#3498DB',
        'princeton': '#2ECC71',
        'oxford': '#F39C12',
        'manchester': '#9B59B6',
        'Unknown': '#A9A9A9'
      },
      period: {
        'medieval': '#E74C3C',
        'early_medieval': '#3498DB',
        'late_medieval': '#2ECC71',
        'early_modern': '#F39C12',
        'modern': '#9B59B6',
        'Unknown': '#A9A9A9'
      },
      material: {
        'parchment': '#8B4513',
        'paper': '#F5DEB3',
        'papyrus': '#D2B48C',
        'vellum': '#DEB887',
        'Unknown': '#A9A9A9'
      },
      title: {
        'Unknown': '#A9A9A9'
      },
      author: {
        'Unknown': '#A9A9A9'
      }
    };

    const palette = colorPalettes[attribute] || colorPalettes.language;

    // Check if category exists in predefined palette
    if (palette[category]) {
      return palette[category];
    }

    // For "Unknown", return gray
    if (category === 'Unknown') {
      return palette['Unknown'];
    }

    // Generate a vibrant color for unmapped categories
    // Include attribute in hash to ensure different colors for same category name across attributes
    return generateColorFromString(`${attribute}:${category}`);
  };

  // Helper to fetch full document details if needed
  const fetchFullDocumentIfNeeded = async (doc) => {
    let metadata = doc.metadata || {};

    // If in full index mode, or if metadata is sparse, we need to fetch the full document
    const isSparse = !metadata.image_urls && !metadata.actual_image_url && !metadata.transcription_full_text;

    if (isFullIndexMode || isSparse) {
      try {
        const idxParam = selectedIndex ? `?index_name=${encodeURIComponent(selectedIndex)}` : '';
        const response = await fetch(`${API_BASE_URL}/document/${encodeURIComponent(doc.doc_id)}${idxParam}`);

        if (response.ok) {
          const fullMetadata = await response.json();
          // Merge full metadata with existing result
          metadata = { ...metadata, ...fullMetadata };
        }
      } catch (err) {
        console.error("Failed to fetch full document details:", err);
      }
    }

    return {
      title: metadata.title || `Document ${doc.doc_id}`,
      description: metadata.description || "Historical manuscript from the Cairo Genizah collection.",
      image_url: (() => {
        if (metadata.actual_image_url) return metadata.actual_image_url;
        if (metadata.image_urls && metadata.image_urls.length > 0) {
          const validUrls = metadata.image_urls.filter(url => url && url.trim());
          if (validUrls.length > 0) return validUrls[0];
        }
        if (metadata.image_url) return metadata.image_url;
        if (metadata.thumbnail_url) return metadata.thumbnail_url;
        return "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop";
      })(),
      date: metadata.date || "Unknown",
      language: metadata.language || metadata.main_language || "Hebrew",
      material: metadata.material || "Parchment",
      institution: metadata.institution,
      collection: metadata.collection,
      shelfmark: metadata.shelf_mark || metadata.shelfmark,
      transcription: metadata.transcription_full_text,
      translation: metadata.translation_full_text,
      tags: metadata.tags,
      period: metadata.period,
      location: metadata.location,
      dimensions: metadata.dimensions,
      document_type: metadata.document_type,
      doc_id: doc.doc_id,
      similarity_score: doc.similarity_score,
      ...metadata,
      metadata: metadata,
      index_name: selectedIndex || metadata.index_name || doc.index_name
    };
  };

  const handleDocumentListClick = async (doc) => {
    if (!onDocumentClick) return;
    const displayData = await fetchFullDocumentIfNeeded(doc);
    onDocumentClick(displayData);
  };

  const handlePlotClick = async (event) => {
    if (!onDocumentClick || !event.points || event.points.length === 0) return;

    const point = event.points[0];
    const pointIndex = point.pointIndex;
    const traceIndex = point.curveNumber;

    // Get the actual result index from customdata
    let resultIndex = pointIndex;

    if (plotData && plotData[traceIndex] && plotData[traceIndex].customdata) {
      resultIndex = plotData[traceIndex].customdata[pointIndex];
    }

    if (resultIndex >= 0 && resultIndex < documents.results.length) {
      const result = documents.results[resultIndex];
      const displayData = await fetchFullDocumentIfNeeded(result);
      onDocumentClick(displayData);
    }
  };

  // Recalculate visualization when query points change (but only if method matches)
  useEffect(() => {
    if (documents && plotData) {
      // Recalculate to include all query points
      calculateVisualization();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryPoints.length]); // Only trigger when number of queries changes

  useEffect(() => {
    if (documents) {
      // If in full index mode, we handle visualization differently
      if (isFullIndexMode) {
        visualizePrecomputed(documents, method);
      } else {
        calculateVisualization();
      }
      // Clear queries that don't match the current method
      setQueryPoints(prev => prev.filter(qp => qp.method === method));
      setSelectedQueryIndex(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [method, colorBy]);

  // Auto-reload documents when switching index after initial fetch
  useEffect(() => {
    // Only trigger reload if we already showed setup indices and have a selection
    if (selectedIndex && (documents || availableIndices.length > 0)) {
      // Reset existing visualization state and reload from new index
      if (documents) {
        setDocuments(null);
        setPlotData(null);
      }
      // Load from the newly selected index
      // Debounce slightly to avoid double fires on rapid changes
      const t = setTimeout(() => {
        if (isFullIndexMode) {
          loadPrecomputedFullIndex();
        } else {
          loadDocuments();
        }
      }, 50);
      return () => clearTimeout(t);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedIndex]);

  const layout = {
    title: {
      text: `Cairo Genizah Collection Explorer (${method.toUpperCase()})${isFullIndexMode ? ' - Full Index' : ''}`,
      font: { size: 18, family: 'Arial, sans-serif' }
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
    margin: { l: 60, r: 200, t: 80, b: 60 },
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
      font: { size: 12 },
      title: {
        text: `<b>${colorBy.replace('_', ' ').toUpperCase()}</b>`,
        font: { size: 13 }
      }
    },
    annotations: documents ? [{
      text: `${documents.count} documents visualized`,
      showarrow: false,
      x: 0.02,
      y: 0.02,
      xref: 'paper',
      yref: 'paper',
      xanchor: 'left',
      yanchor: 'bottom',
      font: { size: 12, color: '#666' }
    }] : []
  };

  const config = {
    displayModeBar: true,
    modeBarButtonsToRemove: [
      'pan2d', 'autoScale2d',
      'hoverClosestCartesian', 'hoverCompareCartesian'
    ],
    displaylogo: false,
    responsive: true,
    toImageButtonOptions: {
      format: 'png',
      filename: `genizah_explorer_${method}_${colorBy}`,
      width: 1200,
      height: 800
    }
  };

  if (error) {
    return (
      <div className="visualization-explorer error">
        <div className="error-message">
          <span>⚠️ {error.message || error}</span>
          <button onClick={loadDocuments} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="visualization-explorer loading">
        <div className="loading-content">
          <div className="spinner"></div>
          <p>Loading documents from the Cairo Genizah collection...</p>
          <p className="loading-details">
            {loadFullIndex ? 'Loading entire collection' : `Loading ${numDocuments} documents`}
          </p>
        </div>
      </div>
    );
  }

  if (!documents) {
    return (
      <div className="visualization-explorer setup">
        <div className="setup-content">
          <h2>Collection Explorer Setup</h2>
          <p>Configure how many documents to load for visualization:</p>

          <div className="setup-controls">
            <div className="control-group">
              <label>
                Select Index:
                <select
                  value={selectedIndex || ''}
                  onChange={(e) => setSelectedIndex(e.target.value)}
                  className="index-select"
                >
                  {availableIndices.map((idx) => (
                    <option key={idx.name} value={idx.name}>
                      {idx.name} ({idx.document_count.toLocaleString()} documents{idx.is_default ? ' - default' : ''})
                    </option>
                  ))}
                </select>
              </label>
              {selectedIndex && (
                <small style={{ color: '#666', marginTop: '4px', display: 'block' }}>
                  {availableIndices.find(idx => idx.name === selectedIndex)?.description || ''}
                </small>
              )}
            </div>

            <div className="control-group">
              <label>
                <input
                  type="checkbox"
                  checked={loadFullIndex}
                  onChange={(e) => setLoadFullIndex(e.target.checked)}
                />
                Load entire collection
              </label>
            </div>

            {!loadFullIndex && (
              <div className="control-group">
                <label>
                  Number of documents:
                  <input
                    type="number"
                    value={numDocuments}
                    onChange={(e) => setNumDocuments(parseInt(e.target.value) || 1000)}
                    min="10"
                    max="10000"
                  />
                </label>
              </div>
            )}

            <div className="action-buttons" style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
              <button
                onClick={loadDocuments}
                className="load-btn"
                style={{ padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              >
                Load Sample
              </button>

              <button
                onClick={loadPrecomputedFullIndex}
                className="load-full-btn"
                style={{ padding: '10px 20px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              >
                Show Full Index (Pre-computed)
              </button>
            </div>
          </div>

          <button onClick={loadDocuments} className="load-btn" disabled={!selectedIndex}>
            Load Documents
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="visualization-explorer">
      <div className="explorer-header">
        <div className="header-left">
          <h1>Cairo Genizah Collection Explorer</h1>
          <p>Explore the semantic relationships in the collection</p>
        </div>

        <div className="header-right">
          {availableIndices && availableIndices.length > 0 && (
            <div className="index-switcher">
              <label>
                Index
                <select
                  value={selectedIndex || ''}
                  onChange={(e) => setSelectedIndex(e.target.value)}
                  className="header-index-select"
                >
                  {availableIndices.map((idx) => (
                    <option key={idx.name} value={idx.name}>
                      {idx.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}
          <button onClick={() => navigate('/')} className="back-btn">
            ← Back to Search
          </button>
        </div>
      </div>

      <div className="explorer-controls">
        <div className="control-group">
          <label>
            Visualization Method:
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              disabled={isCalculating}
            >
              <option value="pca">PCA (Fast)</option>
              <option value="tsne">t-SNE (Detailed)</option>
              <option value="umap">UMAP (Balanced)</option>
            </select>
          </label>
        </div>

        <div className="control-group">
          <label>
            Color By:
            <select
              value={colorBy}
              onChange={(e) => setColorBy(e.target.value)}
              disabled={isCalculating}
            >
              {selectedIndex && selectedIndex.startsWith('bibliography_') ? (
                <>
                  <option value="title">Title</option>
                  <option value="author">Author</option>
                </>
              ) : (
                <>
                  <option value="language">Language</option>
                  <option value="document_type">Document Type</option>
                  <option value="collection">Collection</option>
                  <option value="institution">Institution</option>
                  <option value="period">Period</option>
                  <option value="material">Material</option>
                </>
              )}
            </select>
          </label>
        </div>

        <div className="control-group">
          <button
            onClick={() => calculateVisualization()}
            disabled={isCalculating}
            className="recalculate-btn"
          >
            {isCalculating ? 'Calculating...' : 'Recalculate'}
          </button>
        </div>

        <div className="control-group">
          <div className="selection-controls">
            <button
              onClick={computeSimilarityMatrix}
              disabled={selectedDocuments.length < 2}
              className="similarity-btn"
            >
              Compute Similarities ({selectedDocuments.length} selected)
            </button>
            <button
              onClick={clearSelection}
              disabled={selectedDocuments.length === 0}
              className="clear-btn"
            >
              Clear Selection
            </button>
          </div>
        </div>
      </div>

      <div className="query-projector">
        <div className="query-input-panel">
          <h4>Project Query onto Visualization</h4>
          <p className="query-hint">Enter search queries to see where they map in the embedding space. Multiple queries can be projected simultaneously.</p>
          <div className="query-input-group">
            <input
              type="text"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isProjectingQuery && projectQuery()}
              placeholder="e.g., trade letters from Egypt, legal documents, Hebrew poetry..."
              className="query-input"
              disabled={isProjectingQuery || !plotData}
            />
            <button
              onClick={projectQuery}
              disabled={isProjectingQuery || !queryText.trim() || !plotData}
              className="project-btn"
            >
              {isProjectingQuery ? 'Projecting...' : '🎯 Project Query'}
            </button>
            {queryPoints.length > 0 && (
              <button
                onClick={clearAllQueries}
                className="clear-all-queries-btn"
              >
                Clear All ({queryPoints.length})
              </button>
            )}
          </div>
        </div>

        {queryPoints.length > 0 && (
          <div className="query-list-panel">
            <h5>Projected Queries ({queryPoints.length}):</h5>
            <div className="query-list">
              {queryPoints.map((qp, index) => (
                <div
                  key={qp.id}
                  className={`query-item ${selectedQueryIndex === index ? 'selected' : ''}`}
                  onClick={() => setSelectedQueryIndex(index)}
                  style={{ borderLeftColor: getQueryColor(index) }}
                >
                  <div className="query-item-header">
                    <span className="query-number" style={{ backgroundColor: getQueryColor(index) }}>
                      {index + 1}
                    </span>
                    <span className="query-text">{qp.text}</span>
                    <button
                      className="remove-query-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        clearQuery(qp.id);
                      }}
                      title="Remove this query"
                    >
                      ×
                    </button>
                  </div>
                  <div className="query-coords">
                    Coordinates: ({qp.x.toFixed(3)}, {qp.y.toFixed(3)})
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {method === 'umap' && (
        <div className="umap-params">
          <h4>UMAP Parameters:</h4>
          <div className="param-controls">
            <div className="param-group">
              <label>
                nNeighbors: {umapParams.nNeighbors}
                <input
                  type="range"
                  min="5"
                  max="50"
                  value={umapParams.nNeighbors}
                  onChange={(e) => setUmapParams(prev => ({ ...prev, nNeighbors: parseInt(e.target.value) }))}
                  disabled={isCalculating}
                />
              </label>
            </div>
            <div className="param-group">
              <label>
                minDist: {umapParams.minDist}
                <input
                  type="range"
                  min="0.01"
                  max="1.0"
                  step="0.01"
                  value={umapParams.minDist}
                  onChange={(e) => setUmapParams(prev => ({ ...prev, minDist: parseFloat(e.target.value) }))}
                  disabled={isCalculating}
                />
              </label>
            </div>
            <div className="param-group">
              <label>
                iterations: {umapParams.iterations}
                <input
                  type="range"
                  min="100"
                  max="1000"
                  step="50"
                  value={umapParams.iterations}
                  onChange={(e) => setUmapParams(prev => ({ ...prev, iterations: parseInt(e.target.value) }))}
                  disabled={isCalculating}
                />
              </label>
            </div>
          </div>
        </div>
      )}

      {isCalculating && (
        <div className="calculation-overlay">
          <div className="calculation-content">
            <div className="spinner"></div>
            <p>Calculating {method.toUpperCase()} visualization...</p>
          </div>
        </div>
      )}

      <div className="plot-container" ref={plotRef}>
        {plotData && (
          <Plot
            data={plotData}
            layout={layout}
            config={config}
            style={{ width: '100%', height: '70vh' }}
            useResizeHandler={true}
            onClick={handlePlotClick}
            onSelected={handlePlotSelection}
          />
        )}
      </div>

      <div className="explorer-info">
        <p>
          <strong>What this shows:</strong> This {method.toUpperCase()} plot visualizes semantic relationships
          between documents in the Cairo Genizah collection. Documents closer together are more semantically similar.
          Colors represent different {colorBy.replace('_', ' ')} categories. Click on any point to view document details.
        </p>

        <div className="debug-info">
          <h4>Debug Information:</h4>
          <p><strong>Method:</strong> {method.toUpperCase()}</p>
          <p><strong>Documents:</strong> {documents?.count || 0}</p>
          <p><strong>Embedding Dimension:</strong> {documents?.embedding_data?.dimension || 'Unknown'}</p>
          <p><strong>Color Categories:</strong> {plotData ? Object.keys(generateColorMapping(documents.results, colorBy)).length : 0}</p>

          <div className="coordinate-stats">
            <h5>Coordinate Statistics:</h5>
            {plotData && plotData.length > 0 && (
              <div>
                <p>X Range: {Math.min(...plotData.flatMap(trace => trace.x)).toFixed(3)} to {Math.max(...plotData.flatMap(trace => trace.x)).toFixed(3)}</p>
                <p>Y Range: {Math.min(...plotData.flatMap(trace => trace.y)).toFixed(3)} to {Math.max(...plotData.flatMap(trace => trace.y)).toFixed(3)}</p>
                <p>Total Points: {plotData.reduce((sum, trace) => sum + trace.x.length, 0)}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {selectedQueryIndex !== null && queryPoints[selectedQueryIndex] && queryPoints[selectedQueryIndex].nearestNeighbors && queryPoints[selectedQueryIndex].nearestNeighbors.length > 0 && (
        <div className="query-neighbors-section">
          <div className="query-neighbors-header">
            <h3>Nearest Documents to Query {selectedQueryIndex + 1}: "{queryPoints[selectedQueryIndex].text}"</h3>
            <p className="query-coords">Query coordinates: ({queryPoints[selectedQueryIndex].x.toFixed(3)}, {queryPoints[selectedQueryIndex].y.toFixed(3)})</p>
            <button
              className="close-neighbors-btn"
              onClick={() => setSelectedQueryIndex(null)}
            >
              Close
            </button>
          </div>
          <div className="neighbors-list">
            {queryPoints[selectedQueryIndex].nearestNeighbors.slice(0, 10).map((doc, i) => (
              <div
                key={i}
                className="neighbor-item clickable"
                onClick={() => handleDocumentListClick(doc)}
                title="Click to view document details"
              >
                <div className="neighbor-header">
                  <strong>#{i + 1}:</strong> {doc.metadata?.title || doc.doc_id}
                  <span className="similarity-badge">{(doc.similarity * 100).toFixed(1)}%</span>
                </div>
                <small>
                  Language: {doc.metadata?.language || doc.metadata?.main_language || 'Unknown'} |
                  Type: {doc.metadata?.document_type || 'Unknown'}
                </small>
              </div>
            ))}
          </div>
        </div>
      )}

      {showSimilarityMatrix && similarityMatrix && (
        <div className="similarity-matrix">
          <h3>Cosine Similarity Matrix</h3>
          <p>Selected {selectedDocuments.length} documents. Values range from -1 (completely dissimilar) to 1 (identical).</p>

          <div className="matrix-container">
            <table className="similarity-table">
              <thead>
                <tr>
                  <th></th>
                  {selectedDocuments.map((doc, i) => (
                    <th key={i} title={doc.metadata?.title || doc.doc_id}>
                      Doc {i + 1}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {similarityMatrix.map((row, i) => (
                  <tr key={i}>
                    <th title={selectedDocuments[i]?.metadata?.title || selectedDocuments[i]?.doc_id}>
                      Doc {i + 1}
                    </th>
                    {row.map((value, j) => (
                      <td
                        key={j}
                        className={`similarity-cell ${i === j ? 'diagonal' : ''}`}
                        style={{
                          backgroundColor: i === j
                            ? '#E8F4FD'
                            : `rgba(52, 152, 219, ${Math.max(0, value)})`,
                          color: value < 0.3 ? '#666' : '#000'
                        }}
                        title={`${selectedDocuments[i]?.metadata?.title || selectedDocuments[i]?.doc_id} ↔ ${selectedDocuments[j]?.metadata?.title || selectedDocuments[j]?.doc_id}: ${value.toFixed(3)}`}
                      >
                        {value.toFixed(3)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="selected-docs-info">
            <h4>Selected Documents:</h4>
            <p className="click-hint">💡 Click on any document below to view its details</p>
            <div className="doc-list">
              {selectedDocuments.map((doc, i) => (
                <div
                  key={i}
                  className="doc-item clickable"
                  onClick={() => handleDocumentListClick(doc)}
                  title="Click to view document details"
                >
                  <div className="doc-header">
                    <strong>Doc {i + 1}:</strong> {doc.metadata?.title || doc.doc_id}
                    <span className="click-icon">👆</span>
                  </div>
                  <small>
                    Language: {doc.metadata?.language || doc.metadata?.main_language || 'Unknown'} |
                    Type: {doc.metadata?.document_type || 'Unknown'} |
                    ID: {doc.doc_id}
                  </small>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .visualization-explorer {
          min-height: 100vh;
          background: #FAFAFA;
          padding: 0;
        }
        
        .explorer-header {
          background: #2C3E50;
          color: white;
          padding: 20px 40px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .header-left h1 {
          margin: 0 0 8px 0;
          font-size: 28px;
          font-weight: 600;
        }
        
        .header-left p {
          margin: 0;
          font-size: 16px;
          opacity: 0.9;
        }
        
        .back-btn {
          padding: 12px 24px;
          background: #3498DB;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .back-btn:hover {
          background: #2980B9;
        }
        
        .index-switcher {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-right: 12px;
        }
        
        .index-switcher label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
        }
        
        .header-index-select {
          padding: 8px 12px;
          border: 1px solid #DDD;
          border-radius: 4px;
          background: white;
          font-size: 14px;
          cursor: pointer;
        }
        
        .header-index-select:focus {
          outline: none;
          border-color: #3498DB;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.25);
        }
        
        .explorer-controls {
          background: white;
          padding: 20px 40px;
          border-bottom: 1px solid #E5E5E5;
          display: flex;
          gap: 30px;
          align-items: center;
          flex-wrap: wrap;
        }
        
        .control-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .control-group label {
          font-size: 14px;
          font-weight: 500;
          color: #2C3E50;
        }
        
        .control-group select {
          padding: 8px 12px;
          border: 1px solid #DDD;
          border-radius: 4px;
          background: white;
          font-size: 14px;
          cursor: pointer;
        }
        
        .control-group select:focus {
          outline: none;
          border-color: #3498DB;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.25);
        }
        
        .recalculate-btn {
          padding: 8px 16px;
          background: #27AE60;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .recalculate-btn:hover:not(:disabled) {
          background: #229954;
        }
        
        .recalculate-btn:disabled {
          background: #95A5A6;
          cursor: not-allowed;
        }
        
        .plot-container {
          padding: 20px 40px;
          background: white;
          margin: 0;
        }
        
        .explorer-info {
          background: #F8F9FA;
          padding: 20px 40px;
          border-top: 1px solid #E5E5E5;
        }
        
        .explorer-info p {
          margin: 0;
          font-size: 14px;
          color: #666;
          line-height: 1.5;
        }
        
        .debug-info {
          margin-top: 20px;
          padding: 16px;
          background: #F8F9FA;
          border-radius: 6px;
          border: 1px solid #E9ECEF;
        }
        
        .debug-info h4 {
          margin: 0 0 12px 0;
          font-size: 16px;
          color: #2C3E50;
        }
        
        .debug-info h5 {
          margin: 12px 0 8px 0;
          font-size: 14px;
          color: #34495E;
        }
        
        .debug-info p {
          margin: 4px 0;
          font-size: 13px;
          color: #666;
        }
        
        .coordinate-stats {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid #DEE2E6;
        }
        
        .umap-params {
          background: white;
          padding: 20px 40px;
          border-bottom: 1px solid #E5E5E5;
        }
        
        .umap-params h4 {
          margin: 0 0 16px 0;
          color: #2C3E50;
          font-size: 16px;
        }
        
        .param-controls {
          display: flex;
          gap: 30px;
          flex-wrap: wrap;
        }
        
        .param-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
          min-width: 200px;
        }
        
        .param-group label {
          font-size: 14px;
          font-weight: 500;
          color: #2C3E50;
        }
        
        .param-group input[type="range"] {
          width: 100%;
          margin-top: 4px;
        }
        
        .calculation-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.9);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .calculation-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          background: white;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .loading, .error, .setup {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: #FAFAFA;
        }
        
        .loading-content, .setup-content {
          text-align: center;
          background: white;
          padding: 40px;
          border-radius: 8px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
          max-width: 500px;
        }
        
        .setup-content h2 {
          margin: 0 0 16px 0;
          color: #2C3E50;
        }
        
        .setup-controls {
          margin: 24px 0;
          text-align: left;
        }
        
        .setup-controls .control-group {
          margin: 16px 0;
        }
        
        .setup-controls label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #2C3E50;
          flex-direction: column;
          align-items: flex-start;
        }
        
        .setup-controls .index-select {
          padding: 8px 12px;
          border: 1px solid #DDD;
          border-radius: 4px;
          background: white;
          font-size: 14px;
          cursor: pointer;
          width: 100%;
          margin-top: 8px;
        }
        
        .setup-controls .index-select:focus {
          outline: none;
          border-color: #3498DB;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.25);
        }
        
        .setup-controls input[type="number"] {
          padding: 8px 12px;
          border: 1px solid #DDD;
          border-radius: 4px;
          width: 120px;
          margin-left: 8px;
        }
        
        .load-btn {
          padding: 12px 24px;
          background: #3498DB;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .load-btn:hover {
          background: #2980B9;
        }
        
        .loading-details {
          font-size: 14px;
          color: #666;
          margin-top: 8px;
        }
        
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #E5E5E5;
          border-top: 4px solid #3498DB;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        .error-message {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 16px;
          color: #E74C3C;
          font-size: 16px;
        }
        
        .retry-btn {
          padding: 8px 16px;
          background: #E74C3C;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }
        
        .retry-btn:hover {
          background: #C0392B;
        }
        
        .selection-controls {
          display: flex;
          gap: 12px;
          align-items: center;
        }
        
        .similarity-btn {
          padding: 8px 16px;
          background: #3498DB;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .similarity-btn:hover:not(:disabled) {
          background: #2980B9;
        }
        
        .similarity-btn:disabled {
          background: #95A5A6;
          cursor: not-allowed;
        }
        
        .clear-btn {
          padding: 8px 16px;
          background: #E74C3C;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .clear-btn:hover:not(:disabled) {
          background: #C0392B;
        }
        
        .clear-btn:disabled {
          background: #95A5A6;
          cursor: not-allowed;
        }
        
        .similarity-matrix {
          background: white;
          padding: 20px 40px;
          border-top: 1px solid #E5E5E5;
        }
        
        .similarity-matrix h3 {
          margin: 0 0 8px 0;
          color: #2C3E50;
          font-size: 20px;
        }
        
        .similarity-matrix p {
          margin: 0 0 20px 0;
          color: #666;
          font-size: 14px;
        }
        
        .matrix-container {
          overflow-x: auto;
          margin-bottom: 20px;
        }
        
        .similarity-table {
          border-collapse: collapse;
          width: 100%;
          min-width: 300px;
        }
        
        .similarity-table th,
        .similarity-table td {
          border: 1px solid #DDD;
          padding: 8px;
          text-align: center;
          font-size: 12px;
        }
        
        .similarity-table th {
          background: #F8F9FA;
          font-weight: 600;
          color: #2C3E50;
        }
        
        .similarity-cell {
          font-weight: 500;
          min-width: 60px;
        }
        
        .similarity-cell.diagonal {
          font-weight: 700;
        }
        
        .selected-docs-info {
          background: #F8F9FA;
          padding: 16px;
          border-radius: 6px;
          border: 1px solid #E9ECEF;
        }
        
        .selected-docs-info h4 {
          margin: 0 0 12px 0;
          color: #2C3E50;
          font-size: 16px;
        }
        
        .click-hint {
          margin: 0 0 12px 0;
          color: #3498DB;
          font-size: 13px;
          font-style: italic;
          background: #E8F4FD;
          padding: 8px 12px;
          border-radius: 4px;
          border-left: 3px solid #3498DB;
        }
        
        .doc-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .doc-item {
          padding: 8px;
          background: white;
          border-radius: 4px;
          border: 1px solid #E9ECEF;
          font-size: 13px;
        }
        
        .doc-item.clickable {
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .doc-item.clickable:hover {
          background: #F8F9FA;
          border-color: #3498DB;
          box-shadow: 0 2px 4px rgba(52, 152, 219, 0.1);
          transform: translateY(-1px);
        }
        
        .doc-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
        }
        
        .click-icon {
          font-size: 12px;
          opacity: 0.6;
          transition: opacity 0.2s;
        }
        
        .doc-item.clickable:hover .click-icon {
          opacity: 1;
        }
        
        .doc-item strong {
          color: #2C3E50;
        }
        
        .doc-item small {
          color: #666;
        }
        
        .query-projector {
          background: white;
          padding: 20px 40px;
          border-bottom: 1px solid #E5E5E5;
        }
        
        .query-projector h4 {
          margin: 0 0 8px 0;
          color: #2C3E50;
          font-size: 16px;
        }
        
        .query-hint {
          margin: 0 0 16px 0;
          color: #666;
          font-size: 13px;
          font-style: italic;
        }
        
        .query-input-group {
          display: flex;
          gap: 12px;
          align-items: center;
        }
        
        .query-input {
          flex: 1;
          padding: 10px 16px;
          border: 1px solid #DDD;
          border-radius: 4px;
          font-size: 14px;
        }
        
        .query-input:focus {
          outline: none;
          border-color: #3498DB;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.25);
        }
        
        .query-input:disabled {
          background: #F5F5F5;
          cursor: not-allowed;
        }
        
        .project-btn {
          padding: 10px 20px;
          background: #E74C3C;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }
        
        .project-btn:hover:not(:disabled) {
          background: #C0392B;
        }
        
        .project-btn:disabled {
          background: #95A5A6;
          cursor: not-allowed;
        }
        
        .clear-all-queries-btn {
          padding: 10px 16px;
          background: #95A5A6;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background-color 0.2s;
        }
        
        .clear-all-queries-btn:hover {
          background: #7F8C8D;
        }
        
        .query-list-panel {
          margin-top: 16px;
          padding: 16px;
          background: #F8F9FA;
          border-radius: 4px;
          border: 1px solid #E9ECEF;
        }
        
        .query-list-panel h5 {
          margin: 0 0 12px 0;
          color: #2C3E50;
          font-size: 14px;
          font-weight: 600;
        }
        
        .query-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .query-item {
          padding: 12px;
          background: white;
          border-radius: 4px;
          border: 1px solid #E9ECEF;
          border-left: 4px solid;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .query-item:hover {
          background: #F8F9FA;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .query-item.selected {
          background: #E8F4FD;
          border-color: #3498DB;
          box-shadow: 0 2px 6px rgba(52, 152, 219, 0.2);
        }
        
        .query-item-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 6px;
        }
        
        .query-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          color: white;
          font-size: 12px;
          font-weight: 600;
          flex-shrink: 0;
        }
        
        .query-text {
          flex: 1;
          font-weight: 500;
          color: #2C3E50;
          font-size: 14px;
        }
        
        .remove-query-btn {
          width: 24px;
          height: 24px;
          border: none;
          background: #E74C3C;
          color: white;
          border-radius: 50%;
          cursor: pointer;
          font-size: 18px;
          line-height: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background-color 0.2s;
          flex-shrink: 0;
        }
        
        .remove-query-btn:hover {
          background: #C0392B;
        }
        
        .query-coords {
          font-size: 12px;
          color: #666;
          margin-left: 36px;
        }
        
        .query-neighbors-section {
          background: white;
          padding: 20px 40px;
          border-top: 1px solid #E5E5E5;
        }
        
        .query-neighbors-header {
          margin-bottom: 20px;
          position: relative;
        }
        
        .query-neighbors-header h3 {
          margin: 0 0 8px 0;
          color: #2C3E50;
          font-size: 20px;
        }
        
        .query-neighbors-header .query-coords {
          margin: 0;
          color: #666;
          font-size: 14px;
        }
        
        .close-neighbors-btn {
          position: absolute;
          top: 0;
          right: 0;
          padding: 8px 16px;
          background: #95A5A6;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background-color 0.2s;
        }
        
        .close-neighbors-btn:hover {
          background: #7F8C8D;
        }
        
        .neighbors-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .neighbor-item {
          padding: 10px;
          background: white;
          border-radius: 4px;
          border: 1px solid #E9ECEF;
          font-size: 13px;
        }
        
        .neighbor-item.clickable {
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .neighbor-item.clickable:hover {
          background: #F8F9FA;
          border-color: #3498DB;
          box-shadow: 0 2px 4px rgba(52, 152, 219, 0.1);
          transform: translateY(-1px);
        }
        
        .neighbor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
        }
        
        .neighbor-header strong {
          color: #2C3E50;
        }
        
        .similarity-badge {
          background: #3498DB;
          color: white;
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
        }
        
        .neighbor-item small {
          color: #666;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
          .explorer-header {
            padding: 16px 20px;
            flex-direction: column;
            gap: 16px;
            text-align: center;
          }
          
          .explorer-controls {
            padding: 16px 20px;
            flex-direction: column;
            align-items: stretch;
            gap: 16px;
          }
          
          .plot-container {
            padding: 16px 20px;
          }
          
          .explorer-info {
            padding: 16px 20px;
          }
          
          .query-projector {
            padding: 16px 20px;
          }
          
          .query-input-group {
            flex-direction: column;
            align-items: stretch;
          }
          
          .query-input {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default VisualizationExplorer;
