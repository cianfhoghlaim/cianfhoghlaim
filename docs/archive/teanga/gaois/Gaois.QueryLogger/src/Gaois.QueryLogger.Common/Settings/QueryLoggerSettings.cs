using System.Collections.Generic;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Specifies settings that configure the query logger
    /// </summary>
    public class QueryLoggerSettings
    {
        /// <summary>
        /// Specifies a global name for your application that can be used in all queries logged
        /// </summary>
        public string ApplicationName { get; set; }

        /// <summary>
        /// Specifies whether the application is configured to log queries. The default value is true.
        /// </summary>
        public bool IsEnabled { get; set; } = true;

        /// <summary>
        /// If set, query terms longer than the specified maximum length will be truncated
        /// </summary>
        public int? MaxQueryTermsLength { get; set; }

        /// <summary>
        /// If set, query text longer than the specified maximum length will be truncated
        /// </summary>
        public int? MaxQueryTextLength { get; set; }

        /// <summary>
        /// Specifies whether the client IP address should be logged. The default value is true.
        /// </summary>
        public bool StoreClientIPAddress { get; set; } = true;

        /// <summary>
        /// Sets the level of client IP address anonymization. Defaults to partial anonymization.
        /// </summary>
        public IPAddressAnonymizationLevel AnonymizeIPAddress { get; set; } = IPAddressAnonymizationLevel.Partial;

        /// <summary>
        /// The interval of time (in milliseconds) to wait between sending alerts regarding an issue with the query logger service 
        /// </summary>
        public int AlertInterval { get; set; } = 300000;

        /// <summary>
        /// Specifies settings that configure the query logger store
        /// </summary>
        public QueryLoggerStoreSettings Store { get; set; } = new QueryLoggerStoreSettings();

        /// <summary>
        /// Specifies settings for sending e-mail notifications
        /// </summary>
        public EmailSettings Email { get; set; }

        /// <summary>
        /// Queries associated with these IP address will not be logged
        /// </summary>
        public List<ExcludedIPAddress> ExcludedIPAddresses { get; set; }
    }
}