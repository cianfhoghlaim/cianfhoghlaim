import DuckDB from 'duckdb';

const { AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, R2_TOKEN, R2_ENDPOINT, R2_CATALOG } = process.env;

// Instantiate DuckDB with in-memory database
const duckDB = new DuckDB.Database(':memory:', {
  allow_unsigned_extensions: 'true',
});

// Create connection
const connection = duckDB.connect();

// Track initialization state
let isInitialized = false;

/**
 * Convert BigInt values to numbers in query results
 * DuckDB returns BigInt for COUNT(*) and other aggregate functions
 */
function convertBigIntToNumber(obj: unknown): unknown {
  if (typeof obj === 'bigint') {
    return Number(obj);
  }
  if (Array.isArray(obj)) {
    return obj.map(convertBigIntToNumber);
  }
  if (obj !== null && typeof obj === 'object') {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      result[key] = convertBigIntToNumber(value);
    }
    return result;
  }
  return obj;
}

/**
 * Promisified query method for DuckDB
 */
export const query = <T = DuckDB.TableData>(sql: string): Promise<T> => {
  return new Promise((resolve, reject) => {
    connection.all(sql, (err, res) => {
      if (err) reject(err);
      else resolve(convertBigIntToNumber(res) as T);
    });
  });
};

/**
 * Execute a query without returning results (for DDL statements)
 */
export const execute = (sql: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    connection.run(sql, (err) => {
      if (err) reject(err);
      else resolve();
    });
  });
};

/**
 * Stream query results using Arrow IPC format
 */
export const streamQuery = (sql: string): Promise<DuckDB.IpcResultStreamIterator> => {
  return connection.arrowIPCStream(sql);
};

/**
 * Initialize DuckDB with extensions and configurations
 */
export const initializeDuckDB = async () => {
  if (isInitialized) return;

  console.log('Initializing DuckDB...');

  // Set home directory for extensions
  await query("SET home_directory='/tmp';");

  // Install and load httpfs extension for remote file access
  await query("INSTALL httpfs;");
  await query("LOAD httpfs;");

  // Install and load JSON extension
  await query("INSTALL json;");
  await query("LOAD json;");

  // Install and load Parquet extension
  await query("INSTALL parquet;");
  await query("LOAD parquet;");

  // Set AWS credentials if provided
  if (AWS_REGION && AWS_ACCESS_KEY_ID && AWS_SECRET_ACCESS_KEY) {
    await query(`SET s3_region='${AWS_REGION}';`);
    await query(`SET s3_access_key_id='${AWS_ACCESS_KEY_ID}';`);
    await query(`SET s3_secret_access_key='${AWS_SECRET_ACCESS_KEY}';`);
    console.log('AWS credentials configured');
  }

  // Configure R2/Iceberg catalog if provided
  if (R2_TOKEN && R2_ENDPOINT && R2_CATALOG) {
    await query("INSTALL iceberg;");
    await query("LOAD iceberg;");
    await query(
      `CREATE OR REPLACE SECRET r2_catalog_secret (TYPE ICEBERG, TOKEN '${R2_TOKEN}', ENDPOINT '${R2_ENDPOINT}');`
    );
    await query(`ATTACH '${R2_CATALOG}' AS r2lake (TYPE ICEBERG, ENDPOINT '${R2_ENDPOINT}');`);
    console.log('R2/Iceberg catalog configured');
  }

  // Enable caching for better performance
  await query('SET enable_http_metadata_cache=true;');
  await query('SET enable_object_cache=true;');

  // Create sample analytics tables for demo
  await createSampleTables();

  isInitialized = true;
  console.log('DuckDB initialized successfully');
};

/**
 * Create sample tables for analytics demo
 */
async function createSampleTables() {
  // Create events table
  await query(`
    CREATE TABLE IF NOT EXISTS events (
      event_id VARCHAR PRIMARY KEY,
      user_id VARCHAR,
      event_type VARCHAR,
      event_data JSON,
      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  // Create users table
  await query(`
    CREATE TABLE IF NOT EXISTS users (
      user_id VARCHAR PRIMARY KEY,
      username VARCHAR,
      email VARCHAR,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  // Create analytics_cache table
  await query(`
    CREATE TABLE IF NOT EXISTS analytics_cache (
      cache_key VARCHAR PRIMARY KEY,
      cache_value JSON,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      expires_at TIMESTAMP
    );
  `);

  console.log('Sample tables created');
}

/**
 * Get DuckDB connection for advanced operations
 */
export const getConnection = () => connection;

/**
 * Close DuckDB connection
 */
export const close = () => {
  connection.close();
  duckDB.close();
};
