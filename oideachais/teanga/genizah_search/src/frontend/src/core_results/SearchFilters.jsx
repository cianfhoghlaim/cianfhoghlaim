import React from 'react';

const SearchFilters = ({ filters, filterOptions, onFilterChange }) => (
    <div className="filters-section">
        <h4>Filters</h4>
        <div className="filters-grid">
            <div className="filter-group">
                <label>Language:</label>
                <select
                    value={filters.language || ''}
                    onChange={(e) => onFilterChange('language', e.target.value || null)}
                >
                    <option value="">Any</option>
                    {filterOptions.languages?.map(lang => (
                        <option key={lang} value={lang}>{lang}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Document Type:</label>
                <select
                    value={filters.document_type || ''}
                    onChange={(e) => onFilterChange('document_type', e.target.value || null)}
                >
                    <option value="">Any</option>
                    {filterOptions.document_types?.map(type => (
                        <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                    ))}
                </select>
            </div>

            <div className="filter-group">
                <label>Collection:</label>
                <select
                    value={filters.collection || ''}
                    onChange={(e) => {
                        const newCollection = e.target.value || null;
                        onFilterChange('collection', newCollection);
                        // Clear sub_collection when collection changes
                        if (newCollection !== filters.collection) {
                            onFilterChange('sub_collection', null);
                        }
                    }}
                >
                    <option value="">Any</option>
                    {filterOptions.collections?.map(coll => (
                        <option key={coll} value={coll}>
                            {coll.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </option>
                    ))}
                </select>
            </div>

            {filters.collection && filterOptions.sub_collections && filterOptions.sub_collections[filters.collection] && filterOptions.sub_collections[filters.collection].length > 0 && (
                <div className="filter-group">
                    <label>Sub-Collection:</label>
                    <select
                        value={filters.sub_collection || ''}
                        onChange={(e) => onFilterChange('sub_collection', e.target.value || null)}
                    >
                        <option value="">All sub-collections</option>
                        {filterOptions.sub_collections[filters.collection].map(subColl => (
                            <option key={subColl} value={subColl}>
                                {subColl.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </option>
                        ))}
                    </select>
                </div>
            )}

            <div className="filter-group">
                <label>Content:</label>
                <div className="checkbox-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={filters.has_transcriptions === true}
                            onChange={(e) => onFilterChange('has_transcriptions', e.target.checked ? true : null)}
                        />
                        <span className="checkmark"></span>
                        Has Transcriptions
                    </label>
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={filters.has_translations === true}
                            onChange={(e) => onFilterChange('has_translations', e.target.checked ? true : null)}
                        />
                        <span className="checkmark"></span>
                        Has Translations
                    </label>
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={filters.has_bib === true}
                            onChange={(e) => onFilterChange('has_bib', e.target.checked ? true : null)}
                        />
                        <span className="checkmark"></span>
                        Has Bibliography Data
                    </label>
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={filters.has_joins === true}
                            onChange={(e) => onFilterChange('has_joins', e.target.checked ? true : null)}
                        />
                        <span className="checkmark"></span>
                        Has Joins Data
                    </label>
                </div>
            </div>
        </div>
    </div>
);

export default SearchFilters;