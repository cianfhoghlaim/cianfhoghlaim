USE [YOUR_DATABASE_NAME]

-- total queries in query log table (more efficient thant COUNT() for a very large table)
SELECT TotalQueries = SUM(st.row_count)
FROM sys.dm_db_partition_stats st
WHERE object_name(object_id) = 'QueryLogs' AND (index_id < 2)

-- unique queries per application/host
SELECT a.ApplicationName, a.Host, COUNT(1) AS UniqueQueryCount
FROM (
	SELECT DISTINCT ApplicationName, Host, QueryID
	FROM QueryLogs
	--WHERE LogDate > '2019-01-01'
) AS a
GROUP BY a.ApplicationName, a.Host
ORDER BY UniqueQueryCount DESC;

-- unique queries per application/host/query category
SELECT a.ApplicationName, a.Host, a.QueryCategory, COUNT(1) AS UniqueQueryCount
FROM (
	SELECT DISTINCT ApplicationName, Host, QueryCategory, QueryID
	FROM QueryLogs
	--WHERE LogDate > '2019-01-01'
) AS a
GROUP BY a.ApplicationName, a.Host, a.QueryCategory
ORDER BY UniqueQueryCount DESC;

-- average count of unique queries per day per application/host
SELECT ApplicationName, Host, (COUNT(DISTINCT QueryID) / COUNT(DISTINCT CONVERT(VARCHAR(10), LogDate, 111))) AS AverageUniqueQueriesPerDayCount
FROM QueryLogs
GROUP BY ApplicationName, Host
ORDER BY AverageUniqueQueriesPerDayCount DESC

-- average query execution time (milliseconds) per application/host
SELECT ApplicationName, Host, AVG(CAST(ExecutionTime AS bigint)) AS AverageExecutionTime 
FROM QueryLogs
GROUP BY ApplicationName, Host
ORDER BY AverageExecutionTime ASC;

-- average query execution time (milliseconds) per application/host/query category
SELECT ApplicationName, Host, QueryCategory, AVG(CAST(ExecutionTime AS bigint)) AS AverageExecutionTime 
FROM QueryLogs
GROUP BY QueryCategory, ApplicationName, Host
ORDER BY AverageExecutionTime ASC;

-- count of queries that returned zero results per application/host
SELECT ApplicationName, Host, COUNT(ID) AS NullSearchesCount 
FROM QueryLogs
WHERE ResultCount = 0
GROUP BY ApplicationName, Host
ORDER BY NullSearchesCount ASC;

-- most frequently queried terms per application/host
SELECT TOP 100 ApplicationName, Host, QueryTerms, COUNT(QueryTerms) AS SearchCount FROM QueryLogs
GROUP BY QueryTerms, ApplicationName, Host
ORDER BY SearchCount DESC