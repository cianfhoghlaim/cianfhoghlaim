/**
 * BAML Schema definitions and utilities
 * This file contains TypeScript types that mirror BAML schema definitions
 */

/**
 * Analytics Query Schema
 * Used for generating analytical queries from natural language
 */
export interface AnalyticsQuery {
  query: string;
  description: string;
  expectedFields: string[];
  queryType: 'aggregation' | 'timeseries' | 'cohort' | 'funnel';
}

/**
 * Event Schema Definition
 * Represents a structured event in the analytics system
 */
export interface EventSchema {
  eventId: string;
  userId: string;
  eventType: string;
  properties: Record<string, any>;
  timestamp: Date;
  metadata?: {
    source?: string;
    version?: string;
    sessionId?: string;
  };
}

/**
 * User Schema Definition
 */
export interface UserSchema {
  userId: string;
  username: string;
  email: string;
  properties?: Record<string, any>;
  createdAt: Date;
  updatedAt?: Date;
}

/**
 * Analytics Report Schema
 * Structure for generated analytics reports
 */
export interface AnalyticsReport {
  title: string;
  summary: string;
  metrics: Metric[];
  insights: Insight[];
  recommendations?: string[];
  generatedAt: Date;
}

export interface Metric {
  name: string;
  value: number | string;
  unit?: string;
  change?: {
    value: number;
    direction: 'up' | 'down' | 'stable';
    period: string;
  };
}

export interface Insight {
  category: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  actionable: boolean;
}

/**
 * Data Transformation Schema
 * For ETL and data pipeline definitions
 */
export interface DataTransformation {
  name: string;
  description: string;
  source: {
    type: 'duckdb' | 'redis' | 'api' | 's3' | 'parquet';
    location: string;
    query?: string;
  };
  transformations: TransformationStep[];
  destination: {
    type: 'duckdb' | 'redis' | 'parquet' | 'json';
    location: string;
  };
}

export interface TransformationStep {
  type: 'filter' | 'aggregate' | 'join' | 'pivot' | 'custom';
  config: Record<string, any>;
  sql?: string;
}

/**
 * Cache Strategy Schema
 * Defines caching behavior for different data types
 */
export interface CacheStrategy {
  key: string;
  pattern: 'cache-aside' | 'read-through' | 'write-through' | 'write-behind';
  ttl: number;
  invalidationRules?: {
    onEvent?: string[];
    onTime?: string; // cron expression
    onCondition?: string;
  };
}

/**
 * Query Generation Schema
 * For AI-powered SQL query generation
 */
export interface QueryGeneration {
  naturalLanguageQuery: string;
  context?: {
    tables: string[];
    previousQueries?: string[];
    userIntent?: string;
  };
  generatedQuery: string;
  explanation: string;
  confidence: number;
}

/**
 * Dashboard Schema
 * Configuration for analytics dashboards
 */
export interface DashboardConfig {
  id: string;
  name: string;
  description: string;
  widgets: DashboardWidget[];
  filters?: DashboardFilter[];
  refreshInterval?: number; // seconds
}

export interface DashboardWidget {
  id: string;
  type: 'chart' | 'table' | 'metric' | 'text';
  title: string;
  query: string;
  visualization?: {
    chartType?: 'line' | 'bar' | 'pie' | 'scatter';
    xAxis?: string;
    yAxis?: string;
  };
  cacheStrategy?: CacheStrategy;
}

export interface DashboardFilter {
  field: string;
  type: 'date' | 'select' | 'multiselect' | 'range';
  defaultValue?: any;
  options?: any[];
}

/**
 * Data Quality Schema
 * For data validation and quality checks
 */
export interface DataQualityRule {
  name: string;
  description: string;
  table: string;
  column?: string;
  rule: {
    type: 'not_null' | 'unique' | 'range' | 'pattern' | 'custom';
    condition: string;
  };
  severity: 'warning' | 'error';
}

export interface DataQualityReport {
  timestamp: Date;
  table: string;
  totalRows: number;
  rulesChecked: number;
  rulesPassed: number;
  rulesFailed: number;
  issues: DataQualityIssue[];
}

export interface DataQualityIssue {
  rule: string;
  severity: 'warning' | 'error';
  affectedRows: number;
  sample?: any[];
  recommendation?: string;
}

/**
 * Schema Registry
 * Tracks all schemas in the system
 */
export interface SchemaRegistryEntry {
  name: string;
  version: string;
  type: 'event' | 'user' | 'analytics' | 'custom';
  schema: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
  compatibility?: 'backward' | 'forward' | 'full' | 'none';
}

/**
 * Utility functions for schema validation
 */
export class SchemaValidator {
  static validateEvent(data: any): data is EventSchema {
    return (
      typeof data.eventId === 'string' &&
      typeof data.userId === 'string' &&
      typeof data.eventType === 'string' &&
      typeof data.properties === 'object'
    );
  }

  static validateUser(data: any): data is UserSchema {
    return (
      typeof data.userId === 'string' &&
      typeof data.username === 'string' &&
      typeof data.email === 'string'
    );
  }

  static validateAnalyticsQuery(data: any): data is AnalyticsQuery {
    return (
      typeof data.query === 'string' &&
      typeof data.description === 'string' &&
      Array.isArray(data.expectedFields) &&
      ['aggregation', 'timeseries', 'cohort', 'funnel'].includes(data.queryType)
    );
  }
}

/**
 * Schema transformation utilities
 */
export class SchemaTransformer {
  static toBAMLClass(schema: Record<string, any>): string {
    const className = schema.name || 'GeneratedClass';
    let bamlClass = `class ${className} {\n`;

    for (const [field, type] of Object.entries(schema.properties || {})) {
      bamlClass += `  ${field} ${this.mapTypeToBAML(type)}\n`;
    }

    bamlClass += '}\n';
    return bamlClass;
  }

  private static mapTypeToBAML(type: any): string {
    if (typeof type === 'string') {
      switch (type) {
        case 'string': return 'string';
        case 'number': return 'int';
        case 'boolean': return 'bool';
        case 'date': return 'string';
        default: return 'string';
      }
    }
    return 'string';
  }
}
