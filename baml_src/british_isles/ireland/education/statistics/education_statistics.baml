// Education Statistics Extraction Schema for British Isles
// Supports structured extraction of education metrics across all nations

// =============================================================================
// METRIC ENUMS
// =============================================================================

enum MetricCategory {
  ATTAINMENT @description("Academic achievement and exam results")
  ATTENDANCE @description("Pupil attendance and absence rates")
  EXCLUSIONS @description("Suspensions, expulsions, exclusions")
  ENROLLMENT @description("Pupil numbers and school population")
  WORKFORCE @description("Teacher numbers, qualifications, vacancies")
  FINANCE @description("Funding, spending per pupil")
  INFRASTRUCTURE @description("School facilities, class sizes")
  WELLBEING @description("Mental health, safeguarding, pastoral")
  DESTINATIONS @description("Post-school outcomes, university progression")
  DEPRIVATION @description("Socioeconomic indicators, FSM, pupil premium")
}

enum AggregationLevel {
  NATIONAL @description("Whole nation statistics")
  REGIONAL @description("Region/county level")
  LOCAL_AUTHORITY @description("LA/Council level")
  CONSTITUENCY @description("Parliamentary constituency")
  LSOA @description("Lower Super Output Area - England/Wales")
  DATA_ZONE @description("Data Zone - Scotland")
  SMALL_AREA @description("Small Area - NI/Ireland")
  SCHOOL @description("Individual school level")
}

enum TimeGranularity {
  ACADEMIC_YEAR @description("Full academic year (Sept-Aug)")
  TERM @description("School term (Autumn/Spring/Summer)")
  HALF_TERM @description("Half-term period")
  MONTHLY @description("Calendar month")
  WEEKLY @description("Calendar week")
  DAILY @description("Single day")
}

enum DataSource {
  DFE @description("Department for Education (England)")
  OFSTED @description("Office for Standards in Education (England)")
  SQA @description("Scottish Qualifications Authority")
  EDUCATION_SCOTLAND @description("Education Scotland")
  STATS_WALES @description("StatsWales / Welsh Government")
  ESTYN @description("Estyn - Welsh inspectorate")
  NISRA @description("NI Statistics and Research Agency")
  ETI @description("Education and Training Inspectorate (NI)")
  CSO @description("Central Statistics Office (Ireland)")
  NCCA @description("National Council for Curriculum and Assessment (Ireland)")
  TUSLA @description("Child and Family Agency (Ireland)")
  ONS @description("Office for National Statistics (UK)")
}

// =============================================================================
// STATISTICS STRUCTURES
// =============================================================================

class StatisticMetadata {
  source DataSource
  publication_date string? @description("ISO date of publication")
  reference_period string @description("Period data refers to (e.g., '2023-24')")
  methodology_notes string?
  data_quality_rating "high" | "medium" | "low" | "provisional"
  next_update string? @description("Expected next update date")
}

class Metric {
  name string @description("Metric name")
  description string?
  category MetricCategory
  unit string @description("Unit of measurement (%, count, GBP, etc.)")
  value float
  value_formatted string? @description("Formatted value with units")

  // Confidence/precision
  confidence_interval float[]? @description("[lower, upper] bounds")
  sample_size int?
  is_estimated bool?
  is_provisional bool?
}

class Breakdown {
  dimension string @description("Breakdown dimension (gender, ethnicity, FSM, etc.)")
  categories map<string, float> @description("Category -> value mapping")
}

class TrendPoint {
  period string @description("Time period label")
  value float
  change_from_previous float? @description("Absolute change")
  percent_change float? @description("Percentage change")
}

class StatisticRecord {
  id string? @description("Unique identifier for this record")
  metric Metric

  // Geographic context
  nation string @description("Nation name")
  aggregation_level AggregationLevel
  area_code string? @description("Geographic area code (LAD, LSOA, etc.)")
  area_name string? @description("Geographic area name")

  // Time context
  academic_year string @description("Academic year (e.g., '2023-24')")
  time_granularity TimeGranularity

  // School context (if school-level)
  school_urn string? @description("Unique Reference Number")
  school_name string?
  school_type string?

  // Disaggregations
  breakdowns Breakdown[]?

  // Trends
  trend TrendPoint[]? @description("Historical trend data")

  // Metadata
  metadata StatisticMetadata
  @@stream.done
}

// =============================================================================
// COMPARISON STRUCTURES
// =============================================================================

class NationComparison {
  metric_name string
  category MetricCategory
  academic_year string

  values_by_nation map<string, float>
  uk_average float?
  british_isles_average float?

  highest_nation string
  lowest_nation string
  spread float @description("Difference between highest and lowest")

  notes string[]?
}

class TrendAnalysis {
  metric_name string
  nation string
  start_year string
  end_year string

  trend_direction "increasing" | "decreasing" | "stable" | "volatile"
  average_annual_change float
  total_change float
  percent_total_change float

  significant_events string[]? @description("Events affecting trend (COVID, policy changes)")
  projection float? @description("Projected next year value")
}

class AreaRanking {
  metric_name string
  aggregation_level AggregationLevel
  academic_year string
  nation string

  top_areas map<string, float> @description("Top 10 areas with values")
  bottom_areas map<string, float> @description("Bottom 10 areas with values")

  median_value float
  mean_value float
  std_deviation float

  deprivation_correlation float? @description("Correlation with deprivation index")
}

// =============================================================================
// QUERY STRUCTURES
// =============================================================================

class StatisticsQuery {
  metrics MetricCategory[]
  nations string[]
  aggregation_level AggregationLevel
  academic_years string[]
  include_breakdowns bool
  include_trends bool

  // Filters
  area_codes string[]?
  school_types string[]?
  min_sample_size int?
}

class QueryResult {
  query StatisticsQuery
  total_records int
  records StatisticRecord[]
  warnings string[]?
  data_gaps string[]? @description("Missing data notes")
}

// =============================================================================
// EXTRACTION FUNCTIONS
// =============================================================================

function ExtractStatistics(
  document: string,
  expected_source: DataSource
) -> StatisticRecord[] {
  client Claude
  prompt #"
    Extract structured education statistics from this {{ expected_source }} document.

    Document:
    {{ document }}

    For each statistic found, extract:
    1. METRIC DETAILS
       - Name, description, category
       - Value with correct units
       - Confidence intervals if available

    2. GEOGRAPHIC CONTEXT
       - Nation and area level
       - Area codes and names

    3. TIME CONTEXT
       - Academic year reference
       - Time granularity

    4. BREAKDOWNS
       - Gender, ethnicity, FSM status, SEN status
       - Any other disaggregations

    5. METADATA
       - Data quality indicators
       - Methodology notes
       - Provisional/final status

    Handle different national conventions:
    - England: DfE statistical releases, GIAS data
    - Scotland: Scottish Government statistics, SIMD
    - Wales: StatsWales OData, bilingual labels
    - NI: NISRA tables, DE statistics
    - Ireland: CSO tables, Pobal data

    {{ ctx.output_format }}
  "#
}

function CompareNationStatistics(
  metric_name: string,
  category: MetricCategory,
  academic_year: string,
  statistics: StatisticRecord[]
) -> NationComparison {
  client Claude
  prompt #"
    Compare this education metric across British Isles nations.

    Metric: {{ metric_name }}
    Category: {{ category }}
    Year: {{ academic_year }}

    Statistics:
    {{ statistics }}

    Provide:
    1. Value comparison across nations
    2. UK and British Isles averages
    3. Identification of highest/lowest performers
    4. Spread analysis
    5. Notes on comparability issues

    Consider:
    - Different measurement methodologies
    - Different school types included/excluded
    - Different academic calendars
    - Definitional differences across nations

    {{ ctx.output_format }}
  "#
}

function AnalyzeTrend(
  metric_name: string,
  nation: string,
  historical_data: TrendPoint[]
) -> TrendAnalysis {
  client Claude
  prompt #"
    Analyze the trend for this education metric.

    Metric: {{ metric_name }}
    Nation: {{ nation }}
    Historical Data: {{ historical_data }}

    Analyze:
    1. Overall trend direction (increasing, decreasing, stable, volatile)
    2. Average annual change
    3. Total change over period
    4. Significant changes or inflection points

    Consider:
    - COVID-19 impact (2019-20 to 2021-22)
    - Major policy changes
    - Curriculum reforms
    - Assessment changes

    Provide projection for next year with confidence.

    {{ ctx.output_format }}
  "#
}

function RankAreas(
  metric_name: string,
  nation: string,
  aggregation_level: AggregationLevel,
  statistics: StatisticRecord[]
) -> AreaRanking {
  client Claude
  prompt #"
    Rank geographic areas by this education metric.

    Metric: {{ metric_name }}
    Nation: {{ nation }}
    Level: {{ aggregation_level }}

    Statistics:
    {{ statistics }}

    Provide:
    1. Top 10 highest-performing areas
    2. Bottom 10 lowest-performing areas
    3. Statistical summary (mean, median, std dev)
    4. Correlation with deprivation (SIMD, IMD, etc.)

    {{ ctx.output_format }}
  "#
}

function GenerateStatisticsQuery(
  natural_language_query: string
) -> StatisticsQuery {
  client ClaudeHaiku
  prompt #"
    Convert this natural language question into a structured statistics query.

    Question: {{ natural_language_query }}

    Determine:
    1. Which metric categories are needed
    2. Which nations to include
    3. What aggregation level
    4. Which years to query
    5. What breakdowns are relevant
    6. What filters to apply

    Example questions and mappings:
    - "GCSE results in England" -> ATTAINMENT, [ENGLAND], NATIONAL, latest year
    - "Teacher vacancies by local authority" -> WORKFORCE, all nations, LOCAL_AUTHORITY
    - "Attendance by deprivation" -> ATTENDANCE, all, LSOA/DATA_ZONE, include_breakdowns

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// TEST CASES
// =============================================================================

test extract_dfe_stats {
  functions [ExtractStatistics]
  args {
    document #"
      Key Stage 4 Performance 2023/24

      National statistics for England

      5+ GCSEs at grades 9-4 including English and mathematics:
      - All pupils: 45.2%
      - Boys: 41.8%
      - Girls: 48.7%
      - FSM eligible: 27.3%
      - Non-FSM: 52.1%

      Source: Department for Education
      Publication date: January 2025
      Status: Revised
    "#
    expected_source DFE
  }
}

test compare_attainment {
  functions [CompareNationStatistics]
  args {
    metric_name "5+ GCSEs equivalent at grades A*-C/9-4"
    category ATTAINMENT
    academic_year "2023-24"
    statistics []
  }
}

test natural_language_query {
  functions [GenerateStatisticsQuery]
  args {
    natural_language_query "Show me pupil attendance rates by local authority in Wales for the last 3 years, broken down by FSM status"
  }
}
