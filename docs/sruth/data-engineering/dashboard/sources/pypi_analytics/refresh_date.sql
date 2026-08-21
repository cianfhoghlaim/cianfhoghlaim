select
    max(download_date) as max_date
from
    pypi_analytics.main.pypi_daily_stats
