import React from 'react';

const SearchResults = ({ results, loading, query, processingTime, onDocumentClick, onLoadMore, isLoadingMore, currentSearchMode }) => {
    if (loading) {
        return (
            <div className="results-section">
                <div className="loading">
                    <div className="spinner"></div>
                    <span>Searching through historical manuscripts...</span>
                </div>
            </div>
        );
    }

    if (!results) return null;

    return (
        <div className="results-section">
            <div className="results-header">
                <h3>Search Results for: "{query}"</h3>
                <div className="results-meta">
                    <span>{results.count} results found</span>
                    {processingTime && <span>({processingTime}ms)</span>}
                    {results.index_name && (
                        <span className="index-info">
                            📊 Index: {results.index_name}
                        </span>
                    )}
                </div>
            </div>

            {results.count === 0 ? (
                <div className="no-results">
                    <p>No results found. Try different search terms or adjust your filters.</p>
                    <div className="search-tips">
                        <h4>Search Tips:</h4>
                        <ul>
                            <li>Try broader terms like "marriage", "religious", or "legal"</li>
                            <li>Use different language filters</li>
                            <li>Remove some filters to expand results</li>
                            <li>Try historical terms like "ketubah", "responsa", or "halakhic"</li>
                        </ul>
                    </div>
                </div>
            ) : (
                <div className="results-grid">
                    {results.results.map((result, index) => {
                        const metadata = result.metadata || {};
                        const fallbackData = {
                            title: `Document ${result.doc_id}`,
                            description: "Historical manuscript from the Cairo Genizah collection.",
                            image_url: "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop",
                            date: "Unknown",
                            language: "Hebrew",
                            material: "Parchment"
                        };

                        // Determine if this is a legacy index
                        const isLegacyIndex = results.index_name === 'cairo_genizah_text_only_v1.0.6';

                        const displayData = {
                            title: metadata.title || fallbackData.title,
                            description: metadata.description || fallbackData.description,
                            image_url: (() => {
                                console.log(`[SearchResults] Image selection for doc ${result.doc_id}:`);
                                console.log(`  - Index: ${results.index_name}`);
                                console.log(`  - Is legacy: ${isLegacyIndex}`);
                                console.log(`  - Has actual_image_url: ${!!metadata.actual_image_url}`);
                                console.log(`  - Has image_urls: ${!!metadata.image_urls}`);
                                console.log(`  - image_urls value:`, metadata.image_urls);
                                
                                // If legacy index: use actual_image_url
                                if (isLegacyIndex && metadata.actual_image_url) {
                                    console.log(`  ✅ Using actual_image_url for legacy index`);
                                    return metadata.actual_image_url;
                                }
                                
                                // For new indices or if legacy check fails: use image_urls array
                                if (metadata.image_urls && Array.isArray(metadata.image_urls) && metadata.image_urls.length > 0) {
                                    const validUrls = metadata.image_urls
                                        .filter(url => url && typeof url === 'string' && url.trim())
                                        .map(url => {
                                            // Clean URLs by removing srcset descriptors like "1440w"
                                            const cleaned = url.split(/\s+/)[0];
                                            return cleaned;
                                        })
                                        .filter(url => url && url.trim() && !url.endsWith('w'));
                                    
                                    if (validUrls.length > 0) {
                                        console.log(`  ✅ Using image_urls array, returning first of ${validUrls.length} URLs`);
                                        return validUrls[0];
                                    }
                                    console.log(`  ⚠️ image_urls array exists but no valid URLs after filtering`);
                                }
                                
                                // Fallback: actual_image_url (in case metadata isn't set properly)
                                if (metadata.actual_image_url) {
                                    console.log(`  ✅ Fallback: Using actual_image_url`);
                                    return metadata.actual_image_url;
                                }
                                
                                // Priority 3: image_url
                                if (metadata.image_url) {
                                    console.log(`  ✅ Using image_url`);
                                    return metadata.image_url;
                                }
                                
                                // Priority 4: thumbnail_url
                                if (metadata.thumbnail_url) {
                                    console.log(`  ✅ Using thumbnail_url`);
                                    return metadata.thumbnail_url;
                                }
                                
                                // Fallback to placeholder
                                console.log(`  ❌ No valid image found, using fallback unsplash`);
                                return fallbackData.image_url;
                            })(),
                            date: metadata.date || fallbackData.date,
                            language: metadata.language || fallbackData.language,
                            material: metadata.material || fallbackData.material,
                            institution: metadata.institution,
                            collection: metadata.collection,
                            shelfmark: metadata.shelf_mark,
                            transcription: metadata.transcription,
                            translation: metadata.translation,
                            tags: metadata.tags,
                            period: metadata.period,
                            location: metadata.location,
                            dimensions: metadata.dimensions,
                            document_type: metadata.document_type
                        };

                        return (
                            <div
                                key={result.doc_id}
                                className="result-item enhanced-result-item"
                                onClick={() => onDocumentClick({ ...displayData, doc_id: result.doc_id, ...result, index_name: results.index_name })}
                            >
                                <div className="result-image">
                                    <img
                                        src={displayData.image_url}
                                        alt={displayData.title}
                                        onError={(e) => {
                                            e.target.src = "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop";
                                        }}
                                    />
                                    <div className="similarity-badge">
                                        {(result.similarity_score * 100).toFixed(1)}% match
                                    </div>
                                </div>

                                <div className="result-content">
                                    <h4 className="result-title">{displayData.title}</h4>
                                    <p className="result-description">{displayData.description}</p>

                                    <div className="result-metadata">
                                        <span className="metadata-item">{displayData.date}</span>
                                        <span className="metadata-item">{displayData.language}</span>
                                        <span className="metadata-item">{displayData.material}</span>
                                    </div>

                                    {displayData.shelfmark && (
                                        <div className="result-shelfmark">{displayData.shelfmark}</div>
                                    )}

                                    <div className="result-footer">
                                        <div className="result-id">ID: {result.doc_id}</div>
                                        <div className="view-details">View Details →</div>
                                    </div>

                                    <div className="similarity-progress">
                                        <div
                                            className="progress-fill"
                                            style={{ width: `${result.similarity_score * 100}%` }}
                                        ></div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Temporary: Always show load more button for testing */}
            {results && currentSearchMode !== 'shelfmark' && (
                <div className="pagination-controls">
                    <button className="load-more-button" onClick={onLoadMore} disabled={isLoadingMore}>
                        {isLoadingMore ? 'Loading...' : 'Load more results'}
                    </button>
                    <div className="pagination-meta">
                        <span>Page {results.page} of {results.total_pages}</span>
                        <span> • {results.total} total matches</span>
                        <span> • Mode: {currentSearchMode}</span>
                        <span> • Has more: {String(results.has_more)}</span>
                    </div>
                </div>
            )}
            
            {/* Debug info - remove this after testing */}
            {results && (
                <div style={{fontSize: '12px', color: '#666', marginTop: '10px'}}>
                    Debug: has_more={String(results.has_more)}, currentSearchMode={currentSearchMode}, 
                    page={results.page}, total_pages={results.total_pages}, total={results.total}
                </div>
            )}
        </div>
    );
};

export default SearchResults;