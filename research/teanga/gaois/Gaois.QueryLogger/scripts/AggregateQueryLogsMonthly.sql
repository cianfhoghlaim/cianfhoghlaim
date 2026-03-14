USE [YOUR_DATABASE_NAME]

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Ronan Doherty
-- Create date: 2019-05-04
-- Description:	Aggregates and stores query log data for the previous month per application/host 
-- =============================================
CREATE PROCEDURE AggregateQueryLogsMonthly
	@MonthDiff int = 1
AS
BEGIN
	SET NOCOUNT ON;

	MERGE QueryLogsAggregated AS qla
	USING (
		SELECT ApplicationName, Host, DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) - @MonthDiff, 0) AS LogDate,
			COUNT(ID) AS TotalQueries, COUNT(DISTINCT QueryID) AS TotalUniqueQueries, 
			COUNT(ExecutedSuccessfully) AS ExecutedSuccessfully, AVG(CAST(ExecutionTime AS bigint)) AS AverageExecutionTime
		FROM QueryLogs
		WHERE DATEPART(m, LogDate) = DATEPART(m, DATEADD(m, -@MonthDiff, getdate())) AND DATEPART(yyyy, LogDate) = DATEPART(yyyy, DATEADD(m, -@MonthDiff, GETDATE()))
		GROUP BY ApplicationName, Host
	) AS q
		ON qla.ApplicationName = q.ApplicationName AND qla.Host = q.Host AND qla.LogDate = q.LogDate
	WHEN MATCHED THEN UPDATE
		SET qla.ApplicationName = q.ApplicationName, qla.Host = q.Host, qla.TotalQueries = q.TotalQueries,
			qla.TotalUniqueQueries = q.TotalUniqueQueries, qla.ExecutedSuccessfully = q.ExecutedSuccessfully,
			qla.AverageExecutionTime = q.AverageExecutionTime
	WHEN NOT MATCHED THEN
		INSERT (ApplicationName, Host, LogDate, TotalQueries, TotalUniqueQueries, ExecutedSuccessfully, AverageExecutionTime)
		VALUES (q.ApplicationName, q.Host, q.LogDate, q.TotalQueries, q.TotalUniqueQueries, q.ExecutedSuccessfully, q.AverageExecutionTime);
END
GO