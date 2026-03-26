SELECT
    REPLACE(p.filename, '·', '/') AS repo_name,
    p.programming_language,
    p.license,
    p.description,
    s.star_count,
    s.year,
    s.month
FROM
    github.main.perplexity AS p
LEFT OUTER JOIN
    stars AS s
ON
    REPLACE(p.filename, '·', '/') = s.repo_name;