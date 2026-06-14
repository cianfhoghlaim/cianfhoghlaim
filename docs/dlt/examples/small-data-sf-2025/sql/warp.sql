SELECT
    year,
    month,
    sum(star_count) AS star_count
FROM
WHERE
    repo_name = 'warpdotdev/Warp'
GROUP BY
    year,
    month
ORDER BY
    year,
    month;