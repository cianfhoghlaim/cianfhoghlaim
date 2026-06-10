import React, { useState, useEffect } from 'react';
import mirador from 'mirador';

const SecondarySourceView = ({ document, onClose }) => {
    const [activeTab, setActiveTab] = useState('details');

    // Helper to format footnotes
    const formatFootnotes = (footnotes) => {
        if (!footnotes) return null;

        // Handle if footnotes is an object (map of id -> text) or list
        if (typeof footnotes === 'object' && !Array.isArray(footnotes)) {
            return Object.entries(footnotes).map(([key, value], index) => (
                <div key={key} className="footnote-item">
                    <span className="footnote-number">[{key}]</span>
                    <span className="footnote-text">{value}</span>
                </div>
            ));
        }

        if (Array.isArray(footnotes)) {
            return footnotes.map((note, index) => (
                <div key={index} className="footnote-item">
                    <span className="footnote-number">[{index + 1}]</span>
                    <span className="footnote-text">{typeof note === 'string' ? note : JSON.stringify(note)}</span>
                </div>
            ));
        }

        return <div className="footnote-text">{String(footnotes)}</div>;
    };

    // Helper to format shelfmarks mentioned
    const formatShelfmarks = (shelfmarks) => {
        if (!shelfmarks || shelfmarks.length === 0) return null;

        return (
            <div className="shelfmarks-list">
                {shelfmarks.map((sm, index) => (
                    <span key={index} className="shelfmark-tag">{sm}</span>
                ))}
            </div>
        );
    };

    // Helper to format keywords
    const formatKeywords = (keywords) => {
        if (!keywords || keywords.length === 0) return null;

        return (
            <div className="keywords-list">
                {keywords.map((kw, index) => (
                    <span key={index} className="keyword-tag">{kw}</span>
                ))}
            </div>
        );
    };

    return (
        <div className="secondary-source-view modal-overlay" onClick={onClose}>
            <div className="modal-content secondary-source-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="header-title">
                        <h2>{document.title || "Secondary Source"}</h2>
                        {document.doc_id && <div className="doc-id-badge">ID: {document.doc_id}</div>}
                    </div>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>

                <div className="modal-body secondary-source-body">
                    {/* Left Column: Metadata & Text */}
                    <div className="source-details-column">
                        {/* Authors & Date */}
                        <div className="source-meta-header">
                            {document.authors && document.authors.length > 0 && (
                                <div className="source-authors">
                                    <strong>Author(s):</strong> {document.authors.join(', ')}
                                </div>
                            )}
                            {!document.authors && document.author && (
                                <div className="source-authors">
                                    <strong>Author:</strong> {document.author}
                                </div>
                            )}

                            {document.date_display && (
                                <div className="source-date">
                                    <strong>Date:</strong> {document.date_display}
                                </div>
                            )}
                        </div>

                        {/* Description / Abstract */}
                        {document.description && (
                            <div className="source-section">
                                <h3>Description</h3>
                                <div className="source-description">
                                    {document.description}
                                </div>
                            </div>
                        )}

                        {/* Full Text Content (if available) */}
                        {document.full_text_content && (
                            <div className="source-section">
                                <h3>Full Text</h3>
                                <div className="source-full-text">
                                    {document.full_text_content}
                                </div>
                            </div>
                        )}

                        {/* Footnotes */}
                        {document.footnotes && (
                            <div className="source-section">
                                <h3>Footnotes</h3>
                                <div className="source-footnotes">
                                    {formatFootnotes(document.footnotes)}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Column: Related Info & Technical Details */}
                    <div className="source-sidebar-column">
                        {/* Shelfmarks Mentioned */}
                        {document.shelf_marks_mentioned && document.shelf_marks_mentioned.length > 0 && (
                            <div className="sidebar-section">
                                <h4>Shelfmarks Mentioned</h4>
                                {formatShelfmarks(document.shelf_marks_mentioned)}
                            </div>
                        )}

                        {/* Subject Keywords */}
                        {document.subject_keywords && document.subject_keywords.length > 0 && (
                            <div className="sidebar-section">
                                <h4>Keywords</h4>
                                {formatKeywords(document.subject_keywords)}
                            </div>
                        )}

                        {/* Technical Details */}
                        <div className="sidebar-section technical-details">
                            <h4>Details</h4>
                            <div className="detail-grid">
                                {document.isbn && (
                                    <div className="detail-item">
                                        <span className="label">ISBN:</span>
                                        <span className="value">{document.isbn}</span>
                                    </div>
                                )}
                                {document.page_number && (
                                    <div className="detail-item">
                                        <span className="label">Page:</span>
                                        <span className="value">{document.page_number}</span>
                                    </div>
                                )}
                                {document.extracted_page_number && (
                                    <div className="detail-item">
                                        <span className="label">Extracted Page:</span>
                                        <span className="value">{document.extracted_page_number}</span>
                                    </div>
                                )}
                                {document.document_type && (
                                    <div className="detail-item">
                                        <span className="label">Type:</span>
                                        <span className="value">{document.document_type}</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Image Preview (if available) */}
                        {(document.actual_image_url || (document.image_urls && document.image_urls.length > 0)) && (
                            <div className="sidebar-section image-preview">
                                <h4>Image</h4>
                                <img
                                    src={document.actual_image_url || document.image_urls[0]}
                                    alt="Source preview"
                                    className="source-thumbnail"
                                    onError={(e) => e.target.style.display = 'none'}
                                />
                            </div>
                        )}
                    </div>
                </div>
            </div>
            <style jsx>{`
                .secondary-source-content {
                    width: 90%;
                    max-width: 1200px;
                    height: 90vh;
                    display: flex;
                    flex-direction: column;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                }
                
                .secondary-source-body {
                    display: flex;
                    flex: 1;
                    overflow: hidden;
                    padding: 0;
                }
                
                .source-details-column {
                    flex: 2;
                    padding: 24px;
                    overflow-y: auto;
                    border-right: 1px solid #eee;
                }
                
                .source-sidebar-column {
                    flex: 1;
                    padding: 24px;
                    background: #f9f9f9;
                    overflow-y: auto;
                    min-width: 300px;
                    max-width: 400px;
                }
                
                .source-meta-header {
                    margin-bottom: 24px;
                    padding-bottom: 16px;
                    border-bottom: 1px solid #eee;
                }
                
                .source-authors {
                    font-size: 1.1em;
                    margin-bottom: 8px;
                }
                
                .source-date {
                    color: #666;
                }
                
                .source-section {
                    margin-bottom: 32px;
                }
                
                .source-section h3 {
                    font-size: 1.2em;
                    margin-bottom: 12px;
                    color: #2c3e50;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 6px;
                }
                
                .source-description, .source-full-text {
                    line-height: 1.6;
                    color: #333;
                }
                
                .footnote-item {
                    display: flex;
                    margin-bottom: 8px;
                    font-size: 0.9em;
                }
                
                .footnote-number {
                    font-weight: bold;
                    color: #3498db;
                    margin-right: 8px;
                    min-width: 30px;
                }
                
                .sidebar-section {
                    margin-bottom: 24px;
                    background: white;
                    padding: 16px;
                    border-radius: 6px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                }
                
                .sidebar-section h4 {
                    margin-top: 0;
                    margin-bottom: 12px;
                    font-size: 1em;
                    color: #7f8c8d;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .shelfmark-tag, .keyword-tag {
                    display: inline-block;
                    padding: 4px 8px;
                    margin: 0 6px 6px 0;
                    background: #eef2f7;
                    color: #2c3e50;
                    border-radius: 4px;
                    font-size: 0.85em;
                    border: 1px solid #e1e8ed;
                }
                
                .keyword-tag {
                    background: #f0f3f4;
                    color: #555;
                }
                
                .detail-grid {
                    display: grid;
                    gap: 8px;
                }
                
                .detail-item {
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.9em;
                    padding: 4px 0;
                    border-bottom: 1px solid #f5f5f5;
                }
                
                .detail-item .label {
                    color: #7f8c8d;
                    font-weight: 500;
                }
                
                .detail-item .value {
                    font-weight: 600;
                    color: #2c3e50;
                }
                
                .source-thumbnail {
                    width: 100%;
                    border-radius: 4px;
                    border: 1px solid #eee;
                }
                
                .doc-id-badge {
                    font-size: 0.8em;
                    background: #ecf0f1;
                    padding: 2px 6px;
                    border-radius: 4px;
                    color: #7f8c8d;
                    margin-top: 4px;
                }
            `}</style>
        </div>
    );
};

export default SecondarySourceView;
