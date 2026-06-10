using System;
using Newtonsoft.Json;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Data describing the query to be logged
    /// </summary>
    public class Query
    {
        /// <summary>
        /// The persistent store ID for this query
        /// </summary>
        [JsonIgnore]
        public int ID { get; set; }

        /// <summary>
        /// A unique ID that represents a specific query or group of queries
        /// </summary>
        public Guid? QueryID { get; set; }

        /// <summary>
        /// The name of the application that executes the query
        /// </summary>
        public string ApplicationName { get; set; }

        /// <summary>
        /// Relates the query to a category specified by the application
        /// </summary>
        public string QueryCategory { get; set; }

        /// <summary>
        /// The query term(s) or text content
        /// </summary>
        public string QueryTerms { get; set; }

        /// <summary>
        /// The raw query text, such as a query string or POSTed form field
        /// </summary>
        public string QueryText { get; set; }

        /// <summary>
        /// The application host domain
        /// </summary>
        public string Host { get; set; }

        /// <summary>
        /// The client IP address
        /// </summary>
        public string IPAddress { get; set; }

        /// <summary>
        /// Records whether the query executed successfully. The default value is true.
        /// </summary>
        public bool ExecutedSuccessfully { get; set; } = true;

        /// <summary>
        /// The query execution time in milliseconds
        /// </summary>
        public int? ExecutionTime { get; set; }

        /// <summary>
        /// The count of results returned by the query.
        /// </summary>
        public int? ResultCount { get; set; }

        /// <summary>
        /// The date and time of query logging. Gaois.QueryLogger logs this information automatically.
        /// </summary>
        public DateTime? LogDate { get; set; }

        /// <summary>
        /// Record additional data in JSON format
        /// </summary>
        public string JsonData { get; set; }

        /// <summary>
        /// Get a JSON representation for this query
        /// </summary>
        public string ToJson() => JsonConvert.SerializeObject(this);

        /// <summary>
        /// Deserializes provided JSON into a Query object
        /// </summary>
        /// <param name="json">JSON representing a Query</param>
        /// <returns>The Query object</returns>
        public static Query FromJson(string json) => JsonConvert.DeserializeObject<Query>(json);
    }
}