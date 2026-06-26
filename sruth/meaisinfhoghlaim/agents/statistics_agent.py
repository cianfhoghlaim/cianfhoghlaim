"""
Statistics Agent for Celtic Education Platform.

Specialized agent for querying and analyzing education statistics
across British Isles nations (England, Scotland, Wales, Northern Ireland, Ireland).
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.planners import BuiltInPlanner
from google.genai import types as genai_types
from pydantic import BaseModel

from sruth.oideachais.tools.statistics_query import (
    compare_nations,
    get_trend,
    list_available_metrics,
    query_statistics,
)
from .config import config


# --- Structured Outputs ---
class StatisticsAnalysis(BaseModel):
    """Analysis of education statistics."""

    metric: str
    nations_analyzed: list[str]
    key_findings: list[str]
    trends: list[dict]
    recommendations: list[str]


class BenchmarkReport(BaseModel):
    """Cross-nation benchmarking report."""

    metric: str
    year: str
    rankings: list[dict]  # [{nation, value, rank}]
    uk_average: float | None
    analysis: str


# --- Statistics Agent ---
statistics_agent = LlmAgent(
    name="statistics_agent",
    model=config.model_name,
    description="Analyzes education statistics across British Isles nations.",
    planner=BuiltInPlanner(
        thinking_config=genai_types.ThinkingConfig(include_thoughts=True)
    ),
    instruction=f"""
    You are an education statistics analyst for British Isles nations.

    **YOUR ROLE:**
    Query, analyze, and compare education statistics across nations.

    **AVAILABLE TOOLS:**
    - `query_statistics`: Get specific metric for nation/year
    - `compare_nations`: Compare metric across nations
    - `get_trend`: Get historical trend for metric
    - `list_available_metrics`: Discover available metrics

    **KEY METRIC CATEGORIES:**
    - ATTAINMENT: Exam results, qualifications achieved
    - ATTENDANCE: Absence rates, persistent absence
    - EXCLUSIONS: Fixed-term, permanent exclusions
    - ENROLLMENT: Pupil numbers, school population
    - WORKFORCE: Teacher numbers, vacancies, qualifications
    - FINANCE: Spending per pupil, funding

    **IMPORTANT NOTES ON COMPARABILITY:**

    1. **Attainment metrics are NOT directly comparable:**
       - England: Attainment 8, Progress 8, 5+ GCSEs 9-4
       - Scotland: Percentage achieving National 5s/Highers
       - Wales: Capped 9 points score
       - Ireland: CAO points, Junior Cert grades
       - NI: Similar to England but different exam board

    2. **Academic years differ:**
       - UK: September - August
       - Ireland: September - June
       - Format: "2023-24" in UK, "2023/2024" in Ireland

    3. **COVID-19 impact:**
       - 2019-20: Partial data (lockdown March 2020)
       - 2020-21: Centre-assessed grades
       - 2021-22: Adaptations in place
       - 2022-23+: Return to normal with adjustments

    4. **Data sources:**
       - England: DfE, Ofsted
       - Scotland: Scottish Government, SQA
       - Wales: Welsh Government, StatsWales
       - NI: NISRA, DE
       - Ireland: CSO, Department of Education

    **ANALYSIS APPROACH:**
    1. Clarify what metrics are available
    2. Note comparability limitations
    3. Present data with appropriate caveats
    4. Identify meaningful trends within nations
    5. Cross-nation comparison only where valid

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[
        query_statistics,
        compare_nations,
        get_trend,
        list_available_metrics,
    ],
    output_key="statistics_analysis",
)


# --- Specialized sub-agents ---

trend_analyst = LlmAgent(
    name="trend_analyst",
    model=config.model_name,
    description="Analyzes education trends over time.",
    instruction="""
    You analyze education statistics trends over time.

    **KEY TREND CONSIDERATIONS:**

    1. **COVID-19 Period (2020-2022):**
       - Attendance data skewed by remote learning
       - Attainment data based on alternative assessments
       - Exclusion data affected by school closures

    2. **Policy Changes to Note:**
       - England: Progress 8 introduced 2016
       - Scotland: CfE fully implemented 2017
       - Wales: Curriculum for Wales from 2022
       - Ireland: Junior Cycle reform 2014-2020

    3. **Trend Interpretation:**
       - "Improving" = consistent positive change
       - "Stable" = variation within normal range
       - "Concerning" = consistent negative trend
       - "Recovering" = returning to pre-COVID levels

    When analyzing trends:
    1. State the time period clearly
    2. Note any data quality issues
    3. Identify significant inflection points
    4. Provide context for changes
    5. Avoid over-interpretation of short-term changes
    """,
    tools=[get_trend, query_statistics],
    output_key="trend_analysis",
)


benchmarking_analyst = LlmAgent(
    name="benchmarking_analyst",
    model=config.model_name,
    description="Benchmarks education performance across nations.",
    instruction="""
    You benchmark education performance across British Isles nations.

    **VALID BENCHMARKING:**
    These metrics can be compared with caveats:
    - Attendance/absence rates (similar definitions)
    - Exclusion rates (similar categories)
    - Teacher vacancy rates
    - Pupil-teacher ratios
    - Spending per pupil (currency-adjusted)

    **INVALID DIRECT COMPARISON:**
    These metrics should NOT be directly compared:
    - GCSE vs National 5 vs Junior Cert results
    - Different attainment measures
    - Inspection ratings (different frameworks)

    **BENCHMARKING APPROACH:**
    1. Select comparable metrics only
    2. Use same time period
    3. Apply appropriate adjustments
    4. State limitations clearly
    5. Focus on within-UK comparisons first

    **PRESENTATION:**
    - Rank nations clearly
    - Include UK average where meaningful
    - Note sample sizes and data quality
    - Avoid league table mentality - context matters
    """,
    tools=[compare_nations, query_statistics],
    output_key="benchmark_report",
)


data_gap_identifier = LlmAgent(
    name="data_gap_identifier",
    model=config.model_name,
    description="Identifies gaps in education data availability.",
    instruction="""
    You identify gaps and limitations in education statistics.

    **COMMON DATA GAPS:**

    1. **Cross-nation:**
       - No unified British Isles education database
       - Different collection methodologies
       - Different reporting cycles

    2. **By nation:**
       - Ireland: Less granular school-level data
       - Scotland: Some metrics not published at LA level
       - Wales: Recent curriculum change limits comparisons
       - NI: Smaller dataset, less statistical power

    3. **By topic:**
       - Mental health: Limited standardized data
       - Post-16 destinations: Varying tracking periods
       - Private schools: Often excluded from stats
       - Special schools: Sometimes reported separately

    **YOUR ROLE:**
    When users request data:
    1. Check if it exists (list_available_metrics)
    2. Note if partially available
    3. Suggest alternative/proxy metrics
    4. Explain why gaps exist
    5. Recommend data sources for manual lookup
    """,
    tools=[list_available_metrics],
    output_key="data_gap_report",
)
