# SQL Insertion Scripts for Genizah Documents

This directory contains scripts for inserting Genizah document data from JSON files into PostgreSQL database tables using the `genizah_schema.sql` schema.

## Files

- `sql_insert_genizah_documents.py` - Main insertion script for processing individual JSON files
- `bulk_insert_all_documents.py` - Bulk processing script for all available JSON files
- `test_sql_insertion.py` - Test script for verifying the insertion process
- `db_config_template.json` - Template for database configuration
- `genizah_schema.sql` - PostgreSQL schema for the database tables

## Prerequisites

1. **PostgreSQL Database**: Ensure you have a PostgreSQL database running and accessible
2. **Python Dependencies**: Install required packages:
   ```bash
   pip install psycopg2-binary
   ```
3. **Database Schema**: Create the database tables using the schema:
   ```bash
   psql -d your_database -f genizah_schema.sql
   ```

## Setup

1. **Configure Database**: Copy `db_config_template.json` to `db_config.json` and update with your database credentials:
   ```json
   {
       "host": "localhost",
       "port": 5432,
       "database": "genizah_db",
       "user": "genizah_user",
       "password": "your_password_here"
   }
   ```

2. **Create Database Tables**: Run the schema creation script:
   ```bash
   psql -d genizah_db -f genizah_schema.sql
   ```

## Usage

### Test the Insertion Process

First, test with a small sample to ensure everything works:

```bash
python test_sql_insertion.py
```

This will:
- Create a test document
- Insert it into the database
- Verify the insertion process works correctly

### Process Individual Files

To process a specific JSON file:

```bash
python sql_insert_genizah_documents.py \
    --config db_config.json \
    --input-dir /path/to/json/files \
    --source-name cambridge
```

Parameters:
- `--config`: Database configuration file
- `--input-dir`: Directory containing JSON files
- `--source-name`: Source identifier (e.g., "cambridge", "princeton")
- `--test-mode`: Process only first 10 documents for testing

### Bulk Process All Documents

To process all available JSON files at once:

```bash
python bulk_insert_all_documents.py --config db_config.json
```

For testing with a limited number of documents:

```bash
python bulk_insert_all_documents.py --config db_config.json --test-mode
```

## Supported File Formats

The scripts support Cambridge, Princeton, and Rylands document formats:

### Cambridge Format
- Files with `"documents"` array containing document objects
- Documents with TEI metadata (`{http://www.tei-c.org/ns/1.0}*` fields)
- Shelf marks in format `MS-TS-AS-00001-00001`
- Example: `cambridge_full_08_scrape.json`

### Princeton Format
- Files with document IDs as keys
- Documents with `related_people`, `related_places`, `bibliography` fields
- Various shelf mark formats
- Example: `f_docs_updated.json`

### Rylands Format
- Similar to Princeton format but with `joins_data` field
- Contains `joinedManuscripts` array with fragment relationships
- Shelf marks in format `Manchester: A 445`
- Example: `rylands_friedberger_documents.json`

## Database Tables

The insertion process populates the following tables:

### Core Tables
- `genizah_documents` - Main document records with canonical shelf marks
- `document_source_records` - Source tracking for each document
- `shelf_mark_variants` - Alternative forms of shelf marks
- `genizah_images` - Image records linked to documents

### Supporting Tables
- `bibliographic_sources` - Bibliographic references
- `document_source_mentions` - Links between documents and bibliography
- `bibliographic_chunks` - Text chunks for embedding
- `embedding_models` - Tracking of embedding models used
- `chunk_embeddings` - Embedding status per chunk

## Data Processing

The scripts perform the following operations:

1. **Document Standardization**: Convert different JSON formats to standardized `GenizahDocument` objects
2. **Shelf Mark Extraction**: Extract canonical shelf marks from various sources
3. **Deduplication**: Prevent duplicate documents based on shelf marks
4. **Source Tracking**: Maintain provenance information for each document
5. **Metadata Extraction**: Extract temporal, language, physical, and institutional information
6. **Image Processing**: Link images to documents with proper ordering
7. **Quality Assessment**: Calculate completeness scores for documents
8. **Joins Data Processing**: Extract fragment relationships from Rylands `joins_data` field
9. **Shelf Mark Variants**: Create variant records for all known forms of shelf marks

## Error Handling

The scripts include comprehensive error handling:

- **File-level errors**: Continue processing other files if one fails
- **Document-level errors**: Skip problematic documents and continue
- **Database errors**: Rollback transactions on errors
- **Validation errors**: Log warnings for missing or invalid data

## Monitoring Progress

The scripts provide detailed logging and statistics:

- **Progress tracking**: Shows current file and document being processed
- **Statistics**: Counts of documents processed, inserted, and errors
- **Error reporting**: Detailed error messages for debugging

## Example Output

```
2024-01-15 10:30:00 - INFO - Processing file: talmud_full_cambridge_documents.json
2024-01-15 10:30:01 - INFO - Found 1250 documents in talmud_full_cambridge_documents.json
2024-01-15 10:30:02 - INFO - Processing document 1/1250: MS-TS-AS-00001-00001
2024-01-15 10:30:03 - INFO - Inserted document: MS-TS-AS-00001-00001
...
2024-01-15 10:35:00 - INFO - === Processing Statistics ===
2024-01-15 10:35:00 - INFO - Documents processed: 1250
2024-01-15 10:35:00 - INFO - Documents inserted: 1248
2024-01-15 10:35:00 - INFO - Source records inserted: 1248
2024-01-15 10:35:00 - INFO - Shelf mark variants inserted: 1250
2024-01-15 10:35:00 - INFO - Images inserted: 3120
2024-01-15 10:35:00 - INFO - Errors: 2
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials in config file
   - Ensure PostgreSQL is running
   - Check network connectivity

2. **Schema Errors**
   - Ensure `genizah_schema.sql` has been executed
   - Check for table existence: `\dt` in psql

3. **JSON Format Errors**
   - Verify JSON files are valid
   - Check file encoding (should be UTF-8)
   - Review file format compatibility

4. **Memory Issues**
   - Process files in smaller batches
   - Use `--test-mode` for large files
   - Monitor system memory usage

### Debugging

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about document processing and database operations.

## Performance Considerations

- **Batch Processing**: Files are processed one at a time to manage memory
- **Transaction Management**: Each file is committed separately
- **Indexing**: Database indexes are created by the schema for performance
- **Caching**: Document UUIDs are cached to avoid duplicate lookups

For large datasets, consider:
- Running during off-peak hours
- Monitoring database disk space
- Using database connection pooling for concurrent processing
