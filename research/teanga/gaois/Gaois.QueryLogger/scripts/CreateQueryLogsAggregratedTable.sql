USE [YOUR_DATABASE_NAME]

IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE [TABLE_SCHEMA] = 'dbo' AND [TABLE_NAME] = 'QueryLogsAggregated')

BEGIN
	CREATE TABLE [dbo].[QueryLogsAggregated] (
		[ID] [int] IDENTITY(1,1) NOT NULL,
		[ApplicationName] [nvarchar](50) NOT NULL,
		[Host] [nvarchar](100) NULL,
		[LogDate] [datetime] NOT NULL,
		[TotalQueries] [int] NOT NULL,
		[TotalUniqueQueries] [int] NOT NULL,
		[ExecutedSuccessfully] [int] NULL,
		[AverageExecutionTime] [int] NULL,
		[JsonData] [nvarchar](max) NULL,
	 CONSTRAINT [PK_QueryLogsAggregated] PRIMARY KEY CLUSTERED ([ID] ASC)
	 WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
	) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
END
