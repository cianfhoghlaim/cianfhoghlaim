// ============================================================================
// PRINCETON GENIZAH PROJECT - COMPLETE DATA IMPORT SCHEMA
// ============================================================================
// This imports all Princeton CSV data into Neo4j Knowledge Graph
// 
// Data Files:
// 1. documents.csv - Main document records (PGPID-based)
// 2. fragments.csv - Physical fragment metadata (shelfmark-based)  
// 3. people.csv - Person entities mentioned in documents
// 4. places.csv - Geographic locations
// 5. sources.csv - Bibliographic sources
// 6. footnotes.csv - Links documents to scholarly sources
//
// CRITICAL: Adjust file:/// paths to match your actual file locations
// ============================================================================

// ============================================================================
// STEP 1: CREATE CONSTRAINTS AND INDEXES
// ============================================================================

// Document constraints
CREATE CONSTRAINT document_pgpid IF NOT EXISTS FOR (d:Document) REQUIRE d.pgpid IS UNIQUE;
CREATE CONSTRAINT document_url IF NOT EXISTS FOR (d:Document) REQUIRE d.url IS UNIQUE;

// Fragment constraints  
CREATE CONSTRAINT fragment_shelfmark IF NOT EXISTS FOR (f:Fragment) REQUIRE f.shelfmark IS UNIQUE;

// Person constraints
CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE;

// Place constraints
CREATE CONSTRAINT place_name IF NOT EXISTS FOR (pl:Place) REQUIRE pl.name IS UNIQUE;

// Source constraints
CREATE CONSTRAINT source_citation IF NOT EXISTS FOR (s:Source) REQUIRE s.citation IS UNIQUE;

// Other entity constraints
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE;
CREATE CONSTRAINT library_name IF NOT EXISTS FOR (lib:Library) REQUIRE lib.name IS UNIQUE;
CREATE CONSTRAINT collection_name IF NOT EXISTS FOR (c:Collection) REQUIRE c.name IS UNIQUE;

// Performance indexes
CREATE INDEX document_type IF NOT EXISTS FOR (d:Document) ON (d.type);
CREATE INDEX document_shelfmark IF NOT EXISTS FOR (d:Document) ON (d.shelfmark);
CREATE INDEX person_gender IF NOT EXISTS FOR (p:Person) ON (p.gender);
CREATE INDEX place_coordinates IF NOT EXISTS FOR (pl:Place) ON (pl.coordinates);

// ============================================================================
// STEP 2: IMPORT DOCUMENTS (documents.csv)
// ============================================================================

LOAD CSV WITH HEADERS FROM 'file:///documents.csv' AS row
WITH row WHERE row.pgpid IS NOT NULL

// Create Document node
MERGE (d:Document {pgpid: toInteger(row.pgpid)})
SET d.url = row.url,
    d.shelfmark = row.shelfmark,
    d.multifragment = CASE WHEN row.multifragment = 'Y' THEN true ELSE false END,
    d.side = row.side,
    d.region = row.region,
    d.type = row.type,
    d.description = row.description,
    d.doc_date_original = row.doc_date_original,
    d.doc_date_calendar = row.doc_date_calendar,
    d.doc_date_standard = row.doc_date_standard,
    d.inferred_date_display = row.inferred_date_display,
    d.inferred_date_standard = row.inferred_date_standard,
    d.inferred_date_rationale = row.inferred_date_rationale,
    d.inferred_date_notes = row.inferred_date_notes,
    d.language_note = row.language_note,
    d.scholarship_records = row.scholarship_records,
    d.initial_entry = datetime(row.initial_entry),
    d.last_modified = datetime(row.last_modified),
    d.input_by = row.input_by,
    d.library = row.library,
    d.collection = row.collection,
    d.has_transcription = CASE WHEN row.has_transcription = 'Y' THEN true ELSE false END,
    d.has_translation = CASE WHEN row.has_translation = 'Y' THEN true ELSE false END

// Handle IIIF URLs (can be multiple, comma-separated)
WITH d, row
WHERE row.iiif_urls IS NOT NULL AND row.iiif_urls <> ''
WITH d, split(row.iiif_urls, ',') AS iiif_list
SET d.iiif_urls = [url IN iiif_list | trim(url)]

// Handle Fragment URLs
WITH d, row
WHERE row.fragment_urls IS NOT NULL AND row.fragment_urls <> ''
WITH d, split(row.fragment_urls, ',') AS frag_list  
SET d.fragment_urls = [url IN frag_list | trim(url)]

// Create Library node and relationship
WITH d, row
WHERE row.library IS NOT NULL AND row.library <> ''
WITH d, split(row.library, ' ; ') AS libraries
UNWIND libraries AS lib_name
WITH d, trim(lib_name) AS lib_name
MERGE (lib:Library {name: lib_name})
MERGE (d)-[:HELD_AT]->(lib)

// Create Collection nodes and relationships
WITH d, row
WHERE row.collection IS NOT NULL AND row.collection <> ''
WITH d, split(row.collection, ' ; ') AS collections
UNWIND collections AS coll_name
WITH d, trim(coll_name) AS coll_name
MERGE (c:Collection {name: coll_name})
MERGE (d)-[:PART_OF_COLLECTION]->(c)

// Create primary language relationships
WITH d, row
WHERE row.languages_primary IS NOT NULL AND row.languages_primary <> ''
WITH d, split(row.languages_primary, ',') AS primary_langs
UNWIND primary_langs AS lang_name
WITH d, trim(lang_name) AS lang_name
MERGE (l:Language {name: lang_name})
MERGE (d)-[:WRITTEN_IN {primary: true}]->(l)

// Create secondary language relationships
WITH d, row
WHERE row.languages_secondary IS NOT NULL AND row.languages_secondary <> ''
WITH d, split(row.languages_secondary, ',') AS secondary_langs
UNWIND secondary_langs AS lang_name
WITH d, trim(lang_name) AS lang_name
MERGE (l:Language {name: lang_name})
MERGE (d)-[:WRITTEN_IN {primary: false}]->(l)

// Create Tag relationships
WITH d, row
WHERE row.tags IS NOT NULL AND row.tags <> ''
WITH d, split(row.tags, ', ') AS tag_list
UNWIND tag_list AS tag_name
WITH d, trim(tag_name) AS tag_name
MERGE (t:Tag {name: tag_name})
MERGE (d)-[:HAS_TAG]->(t);

// ============================================================================
// STEP 3: IMPORT FRAGMENTS (fragments.csv)
// ============================================================================

LOAD CSV WITH HEADERS FROM 'file:///fragments.csv' AS row
WITH row WHERE row.shelfmark IS NOT NULL

// Create Fragment node
MERGE (f:Fragment {shelfmark: row.shelfmark})
SET f.is_multifragment = CASE WHEN row.is_multifragment = 'Y' THEN true ELSE false END,
    f.url = row.url,
    f.iiif_url = row.iiif_url,
    f.created = datetime(row.created),
    f.last_modified = datetime(row.last_modified),
    f.provenance_display = row.provenance_display,
    f.provenance = row.provenance,
    f.material_support = row.material_support,
    f.shelfmarks_historic = row.shelfmarks_historic,
    f.collection_name = row.collection_name,
    f.collection_abbrev = row.collection_abbrev

// Create Library node and relationship
WITH f, row
WHERE row.library IS NOT NULL AND row.library <> ''
MERGE (lib:Library {name: row.library})
SET lib.abbreviation = row.library_abbrev
MERGE (f)-[:HELD_AT]->(lib)

// Create Collection relationship
WITH f, row
WHERE row.collection IS NOT NULL AND row.collection <> ''
MERGE (c:Collection {name: row.collection})
SET c.abbreviation = row.collection_abbrev
MERGE (f)-[:PART_OF_COLLECTION]->(c)

// Link Fragment to Documents via PGPIDs
WITH f, row
WHERE row.pgpids IS NOT NULL AND row.pgpids <> ''
WITH f, split(row.pgpids, ';') AS pgpid_list
UNWIND pgpid_list AS pgpid_str
WITH f, trim(pgpid_str) AS pgpid_str
WHERE pgpid_str <> ''
MATCH (d:Document {pgpid: toInteger(pgpid_str)})
MERGE (d)-[:PART_OF_FRAGMENT]->(f);

// ============================================================================
// STEP 4: IMPORT PEOPLE (people.csv)
// ============================================================================

LOAD CSV WITH HEADERS FROM 'file:///people.csv' AS row
WITH row WHERE row.name IS NOT NULL

// Create Person node
MERGE (p:Person {name: row.name})
SET p.name_variants = row.name_variants,
    p.gender = row.gender,
    p.social_roles = row.social_roles,
    p.auto_date_range = row.auto_date_range,
    p.manual_date_range = row.manual_date_range,
    p.description = row.description,
    p.tags = row.tags,
    p.related_people_count = toInteger(row.related_people_count),
    p.family_traces_roots_to = row.family_traces_roots_to,
    p.home_base = row.home_base,
    p.occasional_trips_to = row.occasional_trips_to,
    p.related_documents_count = toInteger(row.related_documents_count),
    p.url = row.url;

// Note: Person-Document relationships will be created via annotation or separate linking file
// Princeton doesn't include person mentions in documents.csv tags field

// ============================================================================
// STEP 5: IMPORT PLACES (places.csv)
// ============================================================================

LOAD CSV WITH HEADERS FROM 'file:///places.csv' AS row
WITH row WHERE row.name IS NOT NULL

// Create Place node
MERGE (pl:Place {name: row.name})
SET pl.name_variants = row.name_variants,
    pl.is_region = CASE WHEN row.is_region = 'Y' THEN true ELSE false END,
    pl.coordinates = row.coordinates,
    pl.geographic_area = row.geographic_area,
    pl.notes = row.notes,
    pl.related_documents_count = toInteger(row.related_documents_count),
    pl.related_people_count = toInteger(row.related_people_count),
    pl.related_events_count = toInteger(row.related_events_count),
    pl.url = row.url

// Parse coordinates if available
WITH pl, row
WHERE row.coordinates IS NOT NULL AND row.coordinates <> ''
WITH pl, split(row.coordinates, ',') AS coord_parts
WHERE size(coord_parts) = 2
WITH pl, 
     trim(split(coord_parts[0], '″')[0]) AS lat_str,
     trim(split(coord_parts[1], '″')[0]) AS lon_str
SET pl.latitude = toFloat(replace(replace(replace(lat_str, '°', '.'), '′', ''), ' N', '')),
    pl.longitude = toFloat(replace(replace(replace(lon_str, '°', '.'), '′', ''), ' E', ''));

// Note: Place-Document relationships will need separate linking
// Princeton provides these via document descriptions and tags, not explicit fields

// ============================================================================
// STEP 6: IMPORT SOURCES (sources.csv)
// ============================================================================

LOAD CSV WITH HEADERS FROM 'file:///sources.csv' AS row
WITH row WHERE row.citation IS NOT NULL

// Create Source node
MERGE (s:Source {citation: row.citation})
SET s.source_type = row.source_type,
    s.authors = row.authors,
    s.title = row.title,
    s.journal_book = row.journal_book,
    s.volume = row.volume,
    s.issue = row.issue,
    s.year = toInteger(row.year),
    s.place_published = row.place_published,
    s.publisher = row.publisher,
    s.edition = row.edition,
    s.other_info = row.other_info,
    s.page_range = row.page_range,
    s.languages = row.languages,
    s.url = row.url,
    s.notes = row.notes,
    s.num_footnotes = toInteger(row.num_footnotes);

// ============================================================================
// STEP 7: IMPORT FOOTNOTES (footnotes.csv) - Links Documents to Sources
// ============================================================================

LOAD CSV WITH HEADERS FROM 'file:///footnotes.csv' AS row
WITH row WHERE row.document_id IS NOT NULL

// Match Document and Source, create relationship
MATCH (d:Document {pgpid: toInteger(row.document_id)})
MATCH (s:Source {citation: row.source})
MERGE (d)-[r:CITED_IN]->(s)
SET r.location = row.location,
    r.doc_relation = row.doc_relation,
    r.emendations = row.emendations,
    r.notes = row.notes,
    r.content_url = row.url,
    r.content = row.content;

// ============================================================================
// STEP 8: CREATE TEMPORAL PERIODS (from document dates)
// ============================================================================

// Extract unique time periods from inferred dates
MATCH (d:Document)
WHERE d.inferred_date_standard IS NOT NULL AND d.inferred_date_standard <> ''
WITH DISTINCT d.inferred_date_standard AS period_str
WHERE period_str <> ''

// Parse date ranges like "1089/1190" or single years
WITH period_str,
     CASE 
       WHEN period_str CONTAINS '/' THEN split(period_str, '/')
       ELSE [period_str, period_str]
     END AS date_parts
WITH period_str,
     toInteger(trim(date_parts[0])) AS start_year,
     toInteger(trim(date_parts[1])) AS end_year
WHERE start_year IS NOT NULL AND end_year IS NOT NULL

MERGE (tp:TimePeriod {period_string: period_str})
SET tp.start_year = start_year,
    tp.end_year = end_year,
    tp.century = toString(start_year / 100 + 1) + 'th'

// Link documents to time periods
WITH tp
MATCH (d:Document)
WHERE d.inferred_date_standard = tp.period_string
MERGE (d)-[:DATED_TO]->(tp);

// ============================================================================
// STEP 9: EXTRACT PERSON MENTIONS FROM DOCUMENT DESCRIPTIONS
// ============================================================================
// Note: This is a simple pattern match. May need refinement based on actual data.
// Princeton people.csv doesn't directly link to documents, so we infer from descriptions.

// This would require more sophisticated NLP or manual tagging
// For now, we'll create a placeholder pattern

// Example: Match documents that mention specific people (requires preprocessing)
// MATCH (p:Person), (d:Document)
// WHERE d.description CONTAINS p.name
// MERGE (d)-[:MENTIONS]->(p);

// ============================================================================
// STEP 10: CREATE DOCUMENT TYPE TAXONOMY
// ============================================================================

// Create document type hierarchy
MATCH (d:Document)
WHERE d.type IS NOT NULL AND d.type <> ''
WITH DISTINCT d.type AS doc_type
MERGE (dt:DocumentType {name: doc_type})

// Link documents to types
WITH dt
MATCH (d:Document {type: dt.name})
MERGE (d)-[:OF_TYPE]->(dt);

// ============================================================================
// VERIFICATION QUERIES
// ============================================================================

// Count nodes by type
// MATCH (n) RETURN labels(n)[0] AS type, count(*) AS count ORDER BY count DESC;

// Sample document with all relationships
// MATCH (d:Document {pgpid: 444})-[r]->(x)
// RETURN d, type(r), x LIMIT 25;

// Find documents by person (after person linking)
// MATCH (p:Person {name: 'Halfon ben Nethanel'})<-[:MENTIONS]-(d:Document)
// RETURN d.pgpid, d.title, d.shelfmark;

// Find documents by place
// MATCH (pl:Place {name: 'Alexandria'})<-[:MENTIONS_PLACE]-(d:Document)
// RETURN d.pgpid, d.shelfmark, d.description;

// Find documents by time period
// MATCH (tp:TimePeriod)<-[:DATED_TO]-(d:Document)
// WHERE tp.start_year >= 1100 AND tp.end_year <= 1200
// RETURN d.pgpid, d.shelfmark, tp.period_string;

// Document citation network (via sources)
// MATCH (d1:Document)-[:CITED_IN]->(s:Source)<-[:CITED_IN]-(d2:Document)
// WHERE d1 <> d2
// RETURN d1.pgpid, d2.pgpid, s.citation LIMIT 50;

// Fragment with multiple documents
// MATCH (f:Fragment {is_multifragment: true})<-[:PART_OF_FRAGMENT]-(d:Document)
// RETURN f.shelfmark, collect(d.pgpid) AS pgpids;
