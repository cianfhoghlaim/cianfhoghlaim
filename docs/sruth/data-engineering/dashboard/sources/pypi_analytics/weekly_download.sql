SELECT
    project,
    DATE_TRUNC('week', download_date) AS week_start_date,
    DATE_PART('year', download_date) AS year,
    version,
    country_code,
    python_version,
    SUM(daily_download_sum) AS weekly_download_sum 
FROM 
   pypi_analytics.main.pypi_daily_stats
GROUP BY 
    ALL
ORDER BY 
    week_start_date
