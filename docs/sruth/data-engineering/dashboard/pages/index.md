---
title: Python 🐍 OLAP Tool Popularity Comparison
---

<BigValue 
  title='Data last updated on'
  data={last_refresh_date} 
  value=max_date
/>

<Dropdown data={projects} name=project value=project>
    <DropdownOption value="%" valueLabel="All Projects"/>
</Dropdown>

<Dropdown data={projects} name=year value=year>
    <DropdownOption value=% valueLabel="All Years"/>
</Dropdown>

<LineChart 
    data={downloads_by_project} 
    x=month
    y=downloads 
    series=project
/>


## Downloads by Python Version in the Last 30 Days

<BarChart
    data={download_python_version}
    x=python_version
    y=total_downloads
    series=project
    type=grouped
    swapXY=true
/>

## Downloads by Country in the Last 30 Days

<BarChart 
    data={download_country}
    x=country_code
    y=total_downloads 
    series=project
    swapXY=true
/>



## Build Your Own Insights on Any Python Package
This dashboard is powered by [Evidence](https://evidence.dev/), [DuckDB](https://duckdb.org/), and [MotherDuck](https://motherduck.com/). 

You can find the code for this dashboard on [GitHub](https://github.com/foghlaimeoir/data-engineering).

## Accessing the raw data
You can query the raw data directly from any DuckDB client, with a free MotherDuck account by attach the [shared database to your workspace](https://motherduck.com/docs/getting-started/sample-data-queries/pypi)

```bash
ATTACH 'md:_share/remote_pypi_analytics_share/eda449f4-c286-4d7b-be3c-72d9e42ae38f' AS pypi_analytics;
```

```sql last_refresh_date
select max_date from refresh_date
```

```sql projects
  select
      distinct project, year
  from weekly_download
```

```sql downloads_by_project
  select 
      date_trunc('month', week_start_date) as month,
      sum(weekly_download_sum) as downloads,
      project
  from weekly_download
  where project like '${inputs.project.value}'
  and date_part('year', week_start_date) like '${inputs.year.value}'
  group by all
  order by downloads desc
```

```sql last_4_weeks
SELECT DISTINCT week_start_date
FROM 
    weekly_download
WHERE 
    week_start_date >= DATE_TRUNC('week', CURRENT_DATE - INTERVAL '4 weeks')
ORDER BY 
    week_start_date DESC
```

```sql download_python_version
WITH top_python_versions AS (
    SELECT
        python_version,
        SUM(weekly_download_sum) AS total_downloads
    FROM
        weekly_download
    WHERE
        week_start_date IN (SELECT week_start_date FROM ${last_4_weeks})
    GROUP BY
        python_version
    ORDER BY
        total_downloads DESC
    LIMIT 6
)
SELECT
    project,
    python_version,
    SUM(weekly_download_sum) AS total_downloads
FROM
    weekly_download
WHERE
    week_start_date IN (SELECT week_start_date FROM ${last_4_weeks})
AND
    python_version IN (SELECT python_version FROM top_python_versions)
GROUP BY
    python_version, project
-- HAVING
--     SUM(weekly_download_sum) > 1000
ORDER BY
    total_downloads DESC
```

```sql download_country
WITH top_countries AS (
    SELECT 
        country_code,
        SUM(weekly_download_sum) AS total_downloads
    FROM 
        weekly_download
    WHERE 
        week_start_date IN (SELECT week_start_date FROM ${last_4_weeks})
    GROUP BY 
        country_code
    ORDER BY 
        total_downloads DESC
    LIMIT 5
)
SELECT 
    country_code,
    project,
    SUM(weekly_download_sum) AS total_downloads
FROM 
    weekly_download
WHERE 
    week_start_date IN (SELECT week_start_date FROM ${last_4_weeks})
AND 
    country_code IN (SELECT country_code FROM top_countries)
GROUP BY 
    country_code, project
ORDER BY 
    total_downloads DESC
```