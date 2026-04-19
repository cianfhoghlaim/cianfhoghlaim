namespace Gaois.QueryLogger
{
    /// <summary>
    /// Specifies settings that configure the query logger store
    /// </summary>
    public class QueryLoggerStoreSettings
    {
        /// <summary>
        /// The connection string for a data store
        /// </summary>
        public string ConnectionString { get; set; }

        /// <summary>
        /// The maximum possible size of the query log queue
        /// </summary>
        public int MaxQueueSize { get; set; } = 1000;

        /// <summary>
        /// The amount of time (in milliseconds) to wait between attempts to write to the log store in the case that a connection with the store cannot be established
        /// </summary>
        public int MaxQueueRetryInterval { get; set; } = 30000;

        /// <summary>
        /// The table name (optionally including schema), e.g. "dbo.QueryLogs" to use when logging queries. The default value is "QueryLogs".
        /// </summary>
        public string TableName { get; set; } = "QueryLogs";
    }
}