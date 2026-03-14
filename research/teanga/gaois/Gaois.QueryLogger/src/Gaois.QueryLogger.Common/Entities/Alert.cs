using System;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Provides information about a possible issue with the query logger service
    /// </summary>
    public class Alert
    {
        /// <summary>
        /// Provides information about a possible issue with the query logger service
        /// </summary>
        public Alert(string alertType, Query query = null, Exception exception = null)
        {
            Type = alertType;
            Query = query;
            Exception = exception;
        }

        /// <summary>
        /// The alert type
        /// </summary>
        public string Type { get; }

        /// <summary>
        /// Query metadata
        /// </summary>
        public Query Query { get; }
        
        /// <summary>
        /// Represents an error that has occurred
        /// </summary>
        public Exception Exception { get; }
    }
}