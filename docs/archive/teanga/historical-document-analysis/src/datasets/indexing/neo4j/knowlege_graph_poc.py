#!/usr/bin/env python3
"""
Princeton Genizah Project - Neo4j Knowledge Graph Import Script

This script ingests Princeton CSV data into Neo4j to create a comprehensive
knowledge graph of Cairo Genizah documents.

Requirements:
    pip install neo4j pandas python-dotenv tqdm

Environment variables (.env file):
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_password

CSV Files (place in ./data/ directory):
    - documents.csv
    - fragments.csv
    - people.csv
    - places.csv
    - sources.csv
    - footnotes.csv
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('genizah_import.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PrincetonGenizahKG:
    """Handler for Princeton Genizah Knowledge Graph in Neo4j"""

    def __init__(self, uri: str, user: str, password: str, data_dir: str = "./data"):
        """Initialize Neo4j connection and data directory"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.data_dir = Path(data_dir)

        # Verify data directory exists
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        logger.info(f"Connected to Neo4j at {uri}")
        logger.info(f"Using data directory: {self.data_dir}")

    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        logger.info("Closed Neo4j connection")

    def verify_csv_files(self) -> Dict[str, Path]:
        """Verify all required CSV files exist"""
        required_files = [
            'documents.csv',
            'fragments.csv',
            'people.csv',
            'places.csv',
            'sources.csv',
            'footnotes.csv'
        ]

        file_paths = {}
        missing_files = []

        for filename in required_files:
            filepath = self.data_dir / filename
            if filepath.exists():
                file_paths[filename] = filepath
                logger.info(f"✓ Found {filename}")
            else:
                missing_files.append(filename)
                logger.warning(f"✗ Missing {filename}")

        if missing_files:
            raise FileNotFoundError(
                f"Missing required CSV files: {', '.join(missing_files)}"
            )

        return file_paths

    def create_constraints(self):
        """Create database constraints and indexes"""
        logger.info("Creating constraints and indexes...")

        constraints = [
            # Unique constraints
            "CREATE CONSTRAINT document_pgpid IF NOT EXISTS FOR (d:Document) REQUIRE d.pgpid IS UNIQUE",
            "CREATE CONSTRAINT fragment_shelfmark IF NOT EXISTS FOR (f:Fragment) REQUIRE f.shelfmark IS UNIQUE",
            "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT place_name IF NOT EXISTS FOR (pl:Place) REQUIRE pl.name IS UNIQUE",
            "CREATE CONSTRAINT source_citation IF NOT EXISTS FOR (s:Source) REQUIRE s.citation IS UNIQUE",
            "CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE",
            "CREATE CONSTRAINT language_name IF NOT EXISTS FOR (l:Language) REQUIRE l.name IS UNIQUE",
            "CREATE CONSTRAINT library_name IF NOT EXISTS FOR (lib:Library) REQUIRE lib.name IS UNIQUE",
            "CREATE CONSTRAINT collection_name IF NOT EXISTS FOR (c:Collection) REQUIRE c.name IS UNIQUE",

            # Indexes for performance
            "CREATE INDEX document_type IF NOT EXISTS FOR (d:Document) ON (d.type)",
            "CREATE INDEX document_shelfmark IF NOT EXISTS FOR (d:Document) ON (d.shelfmark)",
            "CREATE INDEX person_gender IF NOT EXISTS FOR (p:Person) ON (p.gender)",
        ]

        with self.driver.session() as session:
            for constraint in tqdm(constraints, desc="Creating constraints"):
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.warning(f"Constraint/index creation warning: {e}")

        logger.info("✓ Constraints and indexes created")

    def import_documents(self, df: pd.DataFrame):
        """Import documents from DataFrame"""
        logger.info(f"Importing {len(df)} documents...")

        def process_batch(tx, batch):
            """Process a batch of documents"""
            for _, row in batch.iterrows():
                # Convert row to dict, handling NaN values
                doc_data = row.where(pd.notnull(row), None).to_dict()

                query = """
                MERGE (d:Document {pgpid: $pgpid})
                SET d.url = $url,
                    d.shelfmark = $shelfmark,
                    d.multifragment = $multifragment,
                    d.side = $side,
                    d.region = $region,
                    d.type = $type,
                    d.description = $description,
                    d.doc_date_original = $doc_date_original,
                    d.doc_date_standard = $doc_date_standard,
                    d.inferred_date_display = $inferred_date_display,
                    d.inferred_date_standard = $inferred_date_standard,
                    d.language_note = $language_note,
                    d.has_transcription = $has_transcription,
                    d.has_translation = $has_translation

                // Handle tags
                WITH d
                WHERE $tags IS NOT NULL
                WITH d, split($tags, ', ') AS tag_list
                UNWIND tag_list AS tag_name
                WITH d, trim(tag_name) AS tag_name
                WHERE tag_name <> ''
                MERGE (t:Tag {name: tag_name})
                MERGE (d)-[:HAS_TAG]->(t)

                WITH d
                // Handle primary languages
                WHERE $languages_primary IS NOT NULL
                WITH d, split($languages_primary, ',') AS primary_langs
                UNWIND primary_langs AS lang_name
                WITH d, trim(lang_name) AS lang_name
                WHERE lang_name <> ''
                MERGE (l:Language {name: lang_name})
                MERGE (d)-[:WRITTEN_IN {primary: true}]->(l)
                """

                params = {
                    'pgpid': int(doc_data['pgpid']),
                    'url': doc_data.get('url'),
                    'shelfmark': doc_data.get('shelfmark'),
                    'multifragment': doc_data.get('multifragment') == 'Y',
                    'side': doc_data.get('side'),
                    'region': doc_data.get('region'),
                    'type': doc_data.get('type'),
                    'description': doc_data.get('description'),
                    'doc_date_original': doc_data.get('doc_date_original'),
                    'doc_date_standard': doc_data.get('doc_date_standard'),
                    'inferred_date_display': doc_data.get('inferred_date_display'),
                    'inferred_date_standard': doc_data.get('inferred_date_standard'),
                    'language_note': doc_data.get('language_note'),
                    'tags': doc_data.get('tags'),
                    'languages_primary': doc_data.get('languages_primary'),
                    'has_transcription': doc_data.get('has_transcription') == 'Y',
                    'has_translation': doc_data.get('has_translation') == 'Y',
                }

                tx.run(query, **params)

        # Process in batches of 100
        batch_size = 100
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size), desc="Importing documents"):
                batch = df.iloc[i:i + batch_size]
                session.execute_write(process_batch, batch)

        logger.info("✓ Documents imported")

    def import_fragments(self, df: pd.DataFrame):
        """Import fragments from DataFrame"""
        logger.info(f"Importing {len(df)} fragments...")

        def process_batch(tx, batch):
            for _, row in batch.iterrows():
                doc_data = row.where(pd.notnull(row), None).to_dict()

                query = """
                MERGE (f:Fragment {shelfmark: $shelfmark})
                SET f.is_multifragment = $is_multifragment,
                    f.url = $url,
                    f.iiif_url = $iiif_url,
                    f.collection_name = $collection_name,
                    f.provenance_display = $provenance_display

                // Link to library
                WITH f
                WHERE $library IS NOT NULL
                MERGE (lib:Library {name: $library})
                MERGE (f)-[:HELD_AT]->(lib)

                // Link to documents via PGPIDs
                WITH f
                WHERE $pgpids IS NOT NULL
                WITH f, split($pgpids, ';') AS pgpid_list
                UNWIND pgpid_list AS pgpid_str
                WITH f, trim(pgpid_str) AS pgpid_str
                WHERE pgpid_str <> ''
                MATCH (d:Document {pgpid: toInteger(pgpid_str)})
                MERGE (d)-[:PART_OF_FRAGMENT]->(f)
                """

                params = {
                    'shelfmark': doc_data['shelfmark'],
                    'is_multifragment': doc_data.get('is_multifragment') == 'Y',
                    'url': doc_data.get('url'),
                    'iiif_url': doc_data.get('iiif_url'),
                    'collection_name': doc_data.get('collection_name'),
                    'provenance_display': doc_data.get('provenance_display'),
                    'library': doc_data.get('library'),
                    'pgpids': doc_data.get('pgpids'),
                }

                tx.run(query, **params)

        batch_size = 100
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size), desc="Importing fragments"):
                batch = df.iloc[i:i + batch_size]
                session.execute_write(process_batch, batch)

        logger.info("✓ Fragments imported")

    def import_people(self, df: pd.DataFrame):
        """Import people from DataFrame"""
        logger.info(f"Importing {len(df)} people...")

        def process_batch(tx, batch):
            for _, row in batch.iterrows():
                doc_data = row.where(pd.notnull(row), None).to_dict()

                query = """
                MERGE (p:Person {name: $name})
                SET p.name_variants = $name_variants,
                    p.gender = $gender,
                    p.social_roles = $social_roles,
                    p.description = $description,
                    p.home_base = $home_base,
                    p.related_documents_count = $related_documents_count,
                    p.url = $url
                """

                params = {
                    'name': doc_data['name'],
                    'name_variants': doc_data.get('name_variants'),
                    'gender': doc_data.get('gender'),
                    'social_roles': doc_data.get('social_roles'),
                    'description': doc_data.get('description'),
                    'home_base': doc_data.get('home_base'),
                    'related_documents_count': doc_data.get('related_documents_count'),
                    'url': doc_data.get('url'),
                }

                tx.run(query, **params)

        batch_size = 100
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size), desc="Importing people"):
                batch = df.iloc[i:i + batch_size]
                session.execute_write(process_batch, batch)

        logger.info("✓ People imported")

    def import_places(self, df: pd.DataFrame):
        """Import places from DataFrame"""
        logger.info(f"Importing {len(df)} places...")

        def process_batch(tx, batch):
            for _, row in batch.iterrows():
                doc_data = row.where(pd.notnull(row), None).to_dict()

                query = """
                MERGE (pl:Place {name: $name})
                SET pl.name_variants = $name_variants,
                    pl.is_region = $is_region,
                    pl.coordinates = $coordinates,
                    pl.geographic_area = $geographic_area,
                    pl.notes = $notes,
                    pl.related_documents_count = $related_documents_count,
                    pl.url = $url
                """

                params = {
                    'name': doc_data['name'],
                    'name_variants': doc_data.get('name_variants'),
                    'is_region': doc_data.get('is_region') == 'Y',
                    'coordinates': doc_data.get('coordinates'),
                    'geographic_area': doc_data.get('geographic_area'),
                    'notes': doc_data.get('notes'),
                    'related_documents_count': doc_data.get('related_documents_count'),
                    'url': doc_data.get('url'),
                }

                tx.run(query, **params)

        batch_size = 100
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size), desc="Importing places"):
                batch = df.iloc[i:i + batch_size]
                session.execute_write(process_batch, batch)

        logger.info("✓ Places imported")

    def import_sources(self, df: pd.DataFrame):
        """Import bibliographic sources from DataFrame"""
        logger.info(f"Importing {len(df)} sources...")

        def process_batch(tx, batch):
            for _, row in batch.iterrows():
                doc_data = row.where(pd.notnull(row), None).to_dict()

                query = """
                MERGE (s:Source {citation: $citation})
                SET s.source_type = $source_type,
                    s.authors = $authors,
                    s.title = $title,
                    s.journal_book = $journal_book,
                    s.volume = $volume,
                    s.year = $year,
                    s.publisher = $publisher,
                    s.page_range = $page_range,
                    s.url = $url
                """

                params = {
                    'citation': doc_data['citation'],
                    'source_type': doc_data.get('source_type'),
                    'authors': doc_data.get('authors'),
                    'title': doc_data.get('title'),
                    'journal_book': doc_data.get('journal_book'),
                    'volume': doc_data.get('volume'),
                    'year': doc_data.get('year'),
                    'publisher': doc_data.get('publisher'),
                    'page_range': doc_data.get('page_range'),
                    'url': doc_data.get('url'),
                }

                tx.run(query, **params)

        batch_size = 100
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size), desc="Importing sources"):
                batch = df.iloc[i:i + batch_size]
                session.execute_write(process_batch, batch)

        logger.info("✓ Sources imported")

    def import_footnotes(self, df: pd.DataFrame):
        """Import footnotes (document-source relationships) from DataFrame"""
        logger.info(f"Importing {len(df)} footnote relationships...")

        def process_batch(tx, batch):
            for _, row in batch.iterrows():
                doc_data = row.where(pd.notnull(row), None).to_dict()

                # Skip rows with missing required fields
                document_id = doc_data.get('document_id')
                source = doc_data.get('source')
                
                if document_id is None or source is None:
                    continue

                query = """
                MATCH (d:Document {pgpid: $document_id})
                MATCH (s:Source {citation: $source})
                MERGE (d)-[r:CITED_IN]->(s)
                SET r.location = $location,
                    r.doc_relation = $doc_relation,
                    r.notes = $notes
                """

                params = {
                    'document_id': int(document_id),
                    'source': source,
                    'location': doc_data.get('location'),
                    'doc_relation': doc_data.get('doc_relation'),
                    'notes': doc_data.get('notes'),
                }

                try:
                    tx.run(query, **params)
                except Exception as e:
                    logger.debug(f"Footnote relationship skip: {e}")

        batch_size = 100
        with self.driver.session() as session:
            for i in tqdm(range(0, len(df), batch_size), desc="Importing footnotes"):
                batch = df.iloc[i:i + batch_size]
                session.execute_write(process_batch, batch)

        logger.info("✓ Footnotes imported")

    def run_import(self):
        """Execute full import pipeline"""
        logger.info("=" * 60)
        logger.info("PRINCETON GENIZAH PROJECT - NEO4J IMPORT")
        logger.info("=" * 60)

        try:
            # Step 1: Verify CSV files
            file_paths = self.verify_csv_files()

            # Step 2: Create constraints
            self.create_constraints()

            # Step 3: Load and import each dataset
            logger.info("\nLoading CSV files...")

            # Documents
            df_docs = pd.read_csv(file_paths['documents.csv'])
            self.import_documents(df_docs)

            # Fragments
            df_frags = pd.read_csv(file_paths['fragments.csv'])
            self.import_fragments(df_frags)

            # People
            df_people = pd.read_csv(file_paths['people.csv'])
            self.import_people(df_people)

            # Places
            df_places = pd.read_csv(file_paths['places.csv'])
            self.import_places(df_places)

            # Sources
            df_sources = pd.read_csv(file_paths['sources.csv'])
            self.import_sources(df_sources)

            # Footnotes
            df_footnotes = pd.read_csv(file_paths['footnotes.csv'])
            self.import_footnotes(df_footnotes)

            logger.info("\n" + "=" * 60)
            logger.info("✓ IMPORT COMPLETE!")
            logger.info("=" * 60)

            # Print summary statistics
            self.print_statistics()

        except Exception as e:
            logger.error(f"Import failed: {e}", exc_info=True)
            raise

    def print_statistics(self):
        """Print knowledge graph statistics"""
        logger.info("\nKnowledge Graph Statistics:")

        with self.driver.session() as session:
            # Count nodes by label
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] AS label, count(*) AS count
                ORDER BY count DESC
            """)

            print("\nNode Counts:")
            for record in result:
                print(f"  {record['label']}: {record['count']:,}")

            # Count relationships
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) AS relationship, count(*) AS count
                ORDER BY count DESC
            """)

            print("\nRelationship Counts:")
            for record in result:
                print(f"  {record['relationship']}: {record['count']:,}")


def main():
    """Main execution"""
    # Load environment variables
    load_dotenv()

    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    data_dir = os.getenv('DATA_DIR', '/Users/isaac1/Documents/pgp-metadata/data')

    if not neo4j_password:
        logger.error("NEO4J_PASSWORD environment variable not set")
        sys.exit(1)

    # Initialize and run import
    kg = PrincetonGenizahKG(neo4j_uri, neo4j_user, neo4j_password, data_dir)

    try:
        kg.run_import()
    finally:
        kg.close()


if __name__ == "__main__":
    main()