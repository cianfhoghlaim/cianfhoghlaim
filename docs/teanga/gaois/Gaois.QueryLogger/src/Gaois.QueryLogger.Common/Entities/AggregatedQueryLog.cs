using Newtonsoft.Json;
using System;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Data describing an aggregated set of query logs
    /// </summary>
    public class AggregatedQueryLog
    {
        /// <summary>
        /// The persistent store ID for this aggregated log
        /// </summary>
        [JsonIgnore]
        public int ID { get; set; }

        /// <summary>
        /// The name of the application
        /// </summary>
        public string ApplicationName { get; set; }

        /// <summary>
        /// The application host domain
        /// </summary>
        public string Host { get; set; }

        /// <summary>
        /// The date and time to which the aggregated log relates
        /// </summary>
        public DateTime? LogDate { get; set; }

        /// <summary>
        /// The total number of aggregated queries
        /// </summary>
        public int TotalQueries { get; set; }

        /// <summary>
        /// The total number of aggregated unique queries. Useful in cases where you want to count groups of related queries.
        /// </summary>
        public int TotalUniqueQueries { get; set; }

        /// <summary>
        /// The total number of queries executed successfully
        /// </summary>
        public int? ExecutedSuccessfully { get; set; }

        /// <summary>
        /// The average query execution time in milliseconds
        /// </summary>
        public int? AverageExecutionTime { get; set; }

        /// <summary>
        /// Record additional data in JSON format
        /// </summary>
        public string JsonData { get; set; }

        /// <summary>
        /// Get a JSON representation for this aggregated query log
        /// </summary>
        public string ToJson() => JsonConvert.SerializeObject(this);

        /// <summary>
        /// Deserializes provided JSON into an AggregatedQueryLog object
        /// </summary>
        /// <param name="json">JSON representing an AggregatedQueryLog</param>
        /// <returns>The AggregatedQueryLog object</returns>
        public static AggregatedQueryLog FromJson(string json) =>
            JsonConvert.DeserializeObject<AggregatedQueryLog>(json);
    }
}