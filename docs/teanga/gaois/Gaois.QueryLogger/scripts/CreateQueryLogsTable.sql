USE [YOUR_DATABASE_NAME]

/**
You might want to set the length of the [QueryTerms] and [QueryText] columns with respect to your own storage requirements:
Gaois.QueryLogger's MaxQueryTermsLength and MaxQueryTextLength settings allow you to truncate values that exceed defined lengths, if necessary.
**/

IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE [TABLE_SCHEMA] = 'dbo' AND [TABLE_NAME] = 'QueryLogs')

BEGIN
	CREATE TABLE [dbo].[QueryLogs] (
		[ID] [int] IDENTITY(1,1) NOT NULL,
		[QueryID] [uniqueidentifier] NOT NULL,
		[ApplicationName] [nvarchar](50) NOT NULL,
		[QueryCategory] [nvarchar](100) NULL,
		[QueryTerms] [nvarchar](500) NULL,
		[QueryText] [nvarchar](1000) NULL,
		[Host] [nvarchar](100) NULL,
		[IPAddress] [varchar](40) NULL,
		[ExecutedSuccessfully] [bit] NOT NULL,
		[ExecutionTime] [int] NULL,
		[ResultCount] [int] NULL,
		[LogDate] [datetime] NULL,
		[JsonData] [nvarchar](max) NULL,
	 CONSTRAINT [PK_QueryLogs] PRIMARY KEY CLUSTERED ([ID] ASC)
	 WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
	) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
END

--OPTIONAL: Add indexes to the QueryLogs table
USE [YOUR_DATABASE_NAME]
GO
CREATE UNIQUE CLUSTERED INDEX [IX_QueryLogs_LogDate_ID]
ON [dbo].[QueryLogs] ([LogDate] ASC, [ID] ASC)
WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON)
ON [PRIMARY]
GO

USE [YOUR_DATABASE_NAME]
GO
CREATE NONCLUSTERED INDEX IX_QueryLogs_ApplicationName_QueryCategory
ON [dbo].[QueryLogs] ([ApplicationName],[QueryCategory])
INCLUDE ([QueryTerms])
GO

USE [YOUR_DATABASE_NAME]
GO
CREATE NONCLUSTERED INDEX IX_QueryLogs_LogDate
ON [dbo].[QueryLogs] ([LogDate])
INCLUDE ([QueryID],[ApplicationName],[Host],[QueryCategory])
GO

USE [YOUR_DATABASE_NAME]
GO
CREATE NONCLUSTERED INDEX IX_QueryLogs_ResultCount
ON [dbo].[QueryLogs] ([ResultCount])
INCLUDE ([ApplicationName])
GO