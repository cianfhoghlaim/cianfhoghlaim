WITH pre_aggregated_data AS (
    SELECT
        timestamp::date as download_date,
        details.system.name as system_name,
        details.system.release as system_release,
        file.version as version,
        project,
        country_code,
        details.cpu as cpu,
        CASE
            WHEN details.python IS NULL THEN NULL
            ELSE CONCAT(
                    SPLIT_PART(details.python, '.', 1),
                    '.',
                    SPLIT_PART(details.python, '.', 2)
             )
        END as python_version
    FROM {{ source('pypi_analytics', 'downloads') }}
)

SELECT
    MD5(CONCAT_WS('|', download_date, system_name, system_release, version, project, country_code, cpu, python_version)) as id,
    download_date,
    system_name,
    system_release,
    version,
    project,
    country_code,
    cpu,
    python_version,
    COUNT(*) as daily_download_sum
FROM
    pre_aggregated_data
GROUP BY
    ALL
