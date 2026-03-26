// BAML Configuration for Data Unified Example
// Learn more at: https://docs.boundaryml.com

// ============================================================================
// Client Configuration
// ============================================================================

client<llm> OpenAI_GPT4 {
  provider openai
  options {
    model "gpt-4o"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> OpenAI_GPT4_Mini {
  provider openai
  options {
    model "gpt-4o-mini"
    api_key env.OPENAI_API_KEY
  }
}

client<llm> Anthropic_Claude {
  provider anthropic
  options {
    model "claude-3-5-sonnet-20241022"
    api_key env.ANTHROPIC_API_KEY
  }
}

// Fallback strategy for reliability
client<llm> ReliableClient {
  provider fallback
  options {
    strategy [OpenAI_GPT4_Mini, Anthropic_Claude]
  }
}

// ============================================================================
// Schema Definitions
// ============================================================================

class AnalyticsQuery {
  query string @description("The SQL query to execute")
  description string @description("Human-readable description of what the query does")
  expectedFields string[] @description("Fields expected in the result set")
  queryType ("aggregation" | "timeseries" | "cohort" | "funnel") @description("Type of analytics query")
}

class EventData {
  eventId string @description("Unique identifier for the event")
  userId string @description("User who triggered the event")
  eventType string @description("Type of event (e.g., page_view, click, purchase)")
  properties map<string, string> @description("Additional event properties")
  timestamp string @description("ISO 8601 timestamp")
}

class AnalyticsInsight {
  category string @description("Category of insight (e.g., growth, engagement, retention)")
  description string @description("Detailed description of the insight")
  severity ("low" | "medium" | "high") @description("Importance level")
  actionable bool @description("Whether this insight requires action")
  recommendation string? @description("Optional recommendation for action")
}

class AnalyticsReport {
  title string @description("Report title")
  summary string @description("Executive summary")
  insights AnalyticsInsight[] @description("Key insights from the data")
  metrics MetricValue[] @description("Important metrics")
  generatedAt string @description("When this report was generated")
}

class MetricValue {
  name string @description("Metric name")
  value (int | float) @description("Metric value")
  unit string? @description("Unit of measurement")
  trend string? @description("Trend direction (up, down, stable)")
  change float? @description("Percentage change from previous period")
}

class DataTransformation {
  name string @description("Name of the transformation")
  description string @description("What this transformation does")
  sourceType ("duckdb" | "redis" | "api" | "s3" | "parquet") @description("Source data type")
  sourceQuery string @description("Query or path to source data")
  transformationSteps string[] @description("Steps to transform the data")
  outputFormat ("json" | "parquet" | "csv") @description("Desired output format")
}

class CacheStrategy {
  key string @description("Cache key pattern")
  pattern ("cache-aside" | "read-through" | "write-through" | "write-behind") @description("Caching pattern to use")
  ttl int @description("Time to live in seconds")
  invalidateOn string[] @description("Events that trigger cache invalidation")
}

// ============================================================================
// Functions
// ============================================================================

function GenerateAnalyticsQuery(userQuestion: string, availableTables: string[]) -> AnalyticsQuery {
  client OpenAI_GPT4_Mini
  prompt #"
    You are a SQL expert specializing in DuckDB analytics queries.

    User Question: {{ userQuestion }}

    Available Tables: {{ availableTables }}

    Generate an optimized DuckDB SQL query that answers the user's question.
    Consider using window functions, CTEs, and aggregations where appropriate.

    {{ ctx.output_format }}
  "#
}

function AnalyzeQueryResults(query: string, results: string) -> AnalyticsReport {
  client Anthropic_Claude
  prompt #"
    You are a data analyst. Analyze the following query results and provide insights.

    Query: {{ query }}

    Results (JSON):
    {{ results }}

    Provide:
    1. Key insights from the data
    2. Important metrics and trends
    3. Actionable recommendations

    {{ ctx.output_format }}
  "#
}

function GenerateCacheStrategy(queryPattern: string, updateFrequency: string, dataType: string) -> CacheStrategy {
  client OpenAI_GPT4_Mini
  prompt #"
    Design an optimal caching strategy for the following scenario:

    Query Pattern: {{ queryPattern }}
    Update Frequency: {{ updateFrequency }}
    Data Type: {{ dataType }}

    Consider:
    - Read/write patterns
    - Data freshness requirements
    - Performance vs consistency tradeoffs

    {{ ctx.output_format }}
  "#
}

function GenerateDataTransformation(sourceDescription: string, targetDescription: string) -> DataTransformation {
  client Anthropic_Claude
  prompt #"
    Create a data transformation pipeline from source to target.

    Source: {{ sourceDescription }}
    Target: {{ targetDescription }}

    Define the ETL steps needed, including:
    1. Data extraction method
    2. Transformation steps
    3. Output format

    {{ ctx.output_format }}
  "#
}

function ExtractEventSchema(eventSample: string) -> EventData {
  client OpenAI_GPT4_Mini
  prompt #"
    Extract and structure the event data from this sample:

    {{ eventSample }}

    {{ ctx.output_format }}
  "#
}

function OptimizeQuery(slowQuery: string, executionPlan: string) -> AnalyticsQuery {
  client Anthropic_Claude
  prompt #"
    Optimize the following DuckDB query based on the execution plan.

    Original Query:
    {{ slowQuery }}

    Execution Plan:
    {{ executionPlan }}

    Provide an optimized version with:
    1. Better indexing hints
    2. Rewritten joins or subqueries
    3. Reduced data scanning

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Test Cases
// ============================================================================

test TestQueryGeneration {
  functions [GenerateAnalyticsQuery]
  args {
    userQuestion "Show me the top 10 users by event count in the last 7 days"
    availableTables ["events", "users"]
  }
}

test TestAnalysisGeneration {
  functions [AnalyzeQueryResults]
  args {
    query "SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type"
    results #"
      [
        {"event_type": "page_view", "count": 1500},
        {"event_type": "click", "count": 800},
        {"event_type": "purchase", "count": 120}
      ]
    "#
  }
}

test TestCacheStrategyGeneration {
  functions [GenerateCacheStrategy]
  args {
    queryPattern "User activity dashboard"
    updateFrequency "Real-time with minute-level granularity"
    dataType "Time-series event data"
  }
}
