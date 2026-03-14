// ============================================================================
// Cairo Genizah Knowledge Graph Schema - Princeton Data POC
// ============================================================================
// This schema is designed for Neo4j Community Edition via Neo4j Desktop
// Based on Princeton Geniza Project (PGP) data structure

// ============================================================================
// CONSTRAINTS AND INDEXES
// ============================================================================

// Create unique constraints (these also create indexes)
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.doc_id IS UNIQUE;
CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT place_name IF NOT EXISTS FOR (pl:Place) REQUIRE pl.name IS UNIQUE;
CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT collection_name IF NOT EXISTS FOR (c:Collection) REQUIRE c.name IS UNIQUE;

// Additional indexes for performance
CREATE INDEX document_shelfmark IF NOT EXISTS FOR (d:Document) ON (d.shelfmark);
CREATE INDEX document_pgpid IF NOT EXISTS FOR (d:Document) ON (d.pgpid);
CREATE INDEX person_role IF NOT EXISTS FOR (p:Person) ON (p.role);

// ============================================================================
// SAMPLE DATA INGESTION - Single Document Example
// ============================================================================

// Create a sample document from Princeton data
MERGE (d:Document {doc_id: 'uuid-example-001'})
SET d.pgpid = 12345,
    d.shelfmark = 'T-S 13J22.4',
    d.title = 'Letter from Halfon ben Nethanel to Abū Saʿīd Ḥalfon',
    d.description = 'Commercial letter discussing trade routes',
    d.document_type = 'Letter',
    d.dating = '1140-1160 CE',
    d.status = 'Published',
    d.collection = 'Princeton',
    d.text_direction = 'rtl',
    d.url = 'https://example.com/document/12345',
    d.created_at = datetime(),
    d.updated_at = datetime();

// Create Collection node
MERGE (coll:Collection {name: 'Princeton Geniza Project'})
SET coll.institution = 'Princeton University',
    coll.abbreviation = 'PGP';

// Link document to collection
MERGE (d)-[:PART_OF]->(coll);

// Create Language nodes
MERGE (lang_judeo_arabic:Language {name: 'Judaeo-Arabic'})
SET lang_judeo_arabic.script = 'Hebrew',
    lang_judeo_arabic.language_family = 'Semitic';

MERGE (lang_hebrew:Language {name: 'Hebrew'})
SET lang_hebrew.script = 'Hebrew',
    lang_hebrew.language_family = 'Semitic';

// Link document to languages
MERGE (d)-[:WRITTEN_IN {primary: true}]->(lang_judeo_arabic);
MERGE (d)-[:WRITTEN_IN {primary: false}]->(lang_hebrew);

// Create Person nodes (from people array in PGP data)
MERGE (p1:Person {name: 'Halfon ben Nethanel'})
SET p1.normalized_name = 'Halfon b. Nethanel',
    p1.role_in_corpus = 'Merchant';

MERGE (p2:Person {name: 'Abū Saʿīd Ḥalfon'})
SET p2.normalized_name = 'Abu Said Halfon',
    p2.role_in_corpus = 'Merchant';

// Create relationships for people
MERGE (d)-[:WRITTEN_BY]->(p1);
MERGE (d)-[:ADDRESSED_TO]->(p2);
MERGE (d)-[:MENTIONS]->(p1);
MERGE (d)-[:MENTIONS]->(p2);

// Create Place nodes
MERGE (place_alexandria:Place {name: 'Alexandria'})
SET place_alexandria.country = 'Egypt',
    place_alexandria.region = 'Mediterranean',
    place_alexandria.latitude = 31.2001,
    place_alexandria.longitude = 29.9187;

MERGE (place_fustat:Place {name: 'Fustat'})
SET place_fustat.country = 'Egypt',
    place_fustat.region = 'Cairo',
    place_fustat.latitude = 30.0044,
    place_fustat.longitude = 31.2357;

// Link document to places
MERGE (d)-[:MENTIONS_PLACE]->(place_alexandria);
MERGE (d)-[:MENTIONS_PLACE]->(place_fustat);
MERGE (d)-[:WRITTEN_IN_LOCATION]->(place_fustat);

// Create Tag nodes (topics/subjects)
MERGE (tag_trade:Tag {name: 'Trade'})
SET tag_trade.category = 'Commerce';

MERGE (tag_correspondence:Tag {name: 'Correspondence'})
SET tag_correspondence.category = 'Document Type';

MERGE (tag_merchants:Tag {name: 'Merchants'})
SET tag_merchants.category = 'Social Group';

// Link document to tags
MERGE (d)-[:HAS_TAG]->(tag_trade);
MERGE (d)-[:HAS_TAG]->(tag_correspondence);
MERGE (d)-[:HAS_TAG]->(tag_merchants);

// ============================================================================
// DOCUMENT JOINS (Fragment relationships)
// ============================================================================

// Create a second document that joins with the first
MERGE (d2:Document {doc_id: 'uuid-example-002'})
SET d2.pgpid = 12346,
    d2.shelfmark = 'T-S 13J22.5',
    d2.title = 'Letter fragment (continuation)',
    d2.collection = 'Princeton';

// Create JOIN relationship (fragments that belong together)
MERGE (d)-[:JOINS_WITH {
    join_type: 'physical',
    confidence: 'certain',
    notes: 'Same letter, different fragments'
}]->(d2);

// ============================================================================
// TEMPORAL MODELING
// ============================================================================

// Create TimePeriod node for dating
MERGE (period:TimePeriod {name: '1140-1160 CE'})
SET period.start_year = 1140,
    period.end_year = 1160,
    period.century = '12th',
    period.islamic_century = '6th';

// Link document to time period
MERGE (d)-[:DATED_TO]->(period);

// ============================================================================
// EXAMPLE QUERIES FOR ANALYSIS
// ============================================================================

// Query 1: Find all documents written by a specific person
// MATCH (p:Person {name: 'Halfon ben Nethanel'})-[:WRITTEN_BY]-(d:Document)
// RETURN d.title, d.shelfmark, d.dating
// ORDER BY d.dating;

// Query 2: Find documents mentioning multiple places
// MATCH (d:Document)-[:MENTIONS_PLACE]->(p:Place)
// WITH d, COLLECT(p.name) AS places
// WHERE SIZE(places) > 1
// RETURN d.title, places;

// Query 3: Find connected document fragments (joins)
// MATCH path = (d1:Document)-[:JOINS_WITH*1..3]-(d2:Document)
// RETURN path;

// Query 4: Find documents by language and time period
// MATCH (d:Document)-[:WRITTEN_IN]->(l:Language),
//       (d)-[:DATED_TO]->(t:TimePeriod)
// WHERE l.name = 'Judaeo-Arabic' 
//   AND t.start_year >= 1100 
//   AND t.end_year <= 1200
// RETURN d.title, d.shelfmark, t.name;

// Query 5: Social network - people who appear together in documents
// MATCH (p1:Person)<-[:MENTIONS]-(d:Document)-[:MENTIONS]->(p2:Person)
// WHERE p1 <> p2
// RETURN p1.name, p2.name, COUNT(d) AS shared_documents
// ORDER BY shared_documents DESC;

// Query 6: Geographic distribution of documents
// MATCH (d:Document)-[:MENTIONS_PLACE]->(p:Place)
// RETURN p.name, p.country, COUNT(d) AS document_count
// ORDER BY document_count DESC;

// Query 7: Find documents with similar tags (content similarity)
// MATCH (d1:Document)-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(d2:Document)
// WHERE d1 <> d2
// WITH d1, d2, COLLECT(t.name) AS shared_tags
// WHERE SIZE(shared_tags) >= 2
// RETURN d1.title, d2.title, shared_tags;

// Query 8: Merchant correspondence network
// MATCH (merchant:Person)-[:WRITTEN_BY]-(letter:Document)-[:ADDRESSED_TO]->(recipient:Person)
// WHERE 'Merchant' IN merchant.role_in_corpus
// RETURN merchant.name, recipient.name, COUNT(letter) AS letters_sent
// ORDER BY letters_sent DESC;

// ============================================================================
// BULK IMPORT TEMPLATE (for Python integration)
// ============================================================================

/*
// This would be used in a Python script with the Neo4j driver:

from neo4j import GraphDatabase
import json

class GenizahKG:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def create_document(self, doc_data):
        with self.driver.session() as session:
            return session.execute_write(self._create_document_tx, doc_data)
    
    @staticmethod
    def _create_document_tx(tx, doc_data):
        query = '''
        MERGE (d:Document {doc_id: $doc_id})
        SET d += $properties
        
        WITH d
        UNWIND $languages AS lang
        MERGE (l:Language {name: lang.name})
        MERGE (d)-[:WRITTEN_IN {primary: lang.primary}]->(l)
        
        WITH d
        UNWIND $people AS person
        MERGE (p:Person {name: person.name})
        SET p.role_in_corpus = person.role
        MERGE (d)-[:MENTIONS]->(p)
        
        WITH d
        UNWIND $tags AS tag
        MERGE (t:Tag {name: tag})
        MERGE (d)-[:HAS_TAG]->(t)
        
        RETURN d.doc_id AS doc_id
        '''
        result = tx.run(query, doc_data)
        return result.single()

# Example usage:
kg = GenizahKG("bolt://localhost:7687", "neo4j", "password")
doc_data = {
    "doc_id": "uuid-001",
    "properties": {
        "pgpid": 12345,
        "title": "Letter...",
        "shelfmark": "T-S 13J22.4"
    },
    "languages": [{"name": "Judaeo-Arabic", "primary": True}],
    "people": [{"name": "Halfon ben Nethanel", "role": "Merchant"}],
    "tags": ["Trade", "Correspondence"]
}
kg.create_document(doc_data)
*/
