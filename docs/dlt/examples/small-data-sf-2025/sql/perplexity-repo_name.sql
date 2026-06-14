SELECT
    REPLACE(filename, '·', '/') AS repo_name,
    programming_language,
    license,
    description
FROM
    github.main.perplexity;