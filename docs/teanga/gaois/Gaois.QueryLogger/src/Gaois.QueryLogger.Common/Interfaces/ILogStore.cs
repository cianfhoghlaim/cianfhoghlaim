using System.Threading.Channels;
using System.Threading.Tasks;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Log data to persistent storage
    /// </summary>
    public interface ILogStore
    {
        /// <summary>
        /// Gets the queue of logs waiting to be written
        /// </summary>
        Channel<Query> LogQueue { get; }

        /// <summary>
        /// Queues query data for logging to a data store
        /// </summary>
        /// <param name="query">The <see cref="Query"/> object to be logged</param>
        void Enqueue(Query query);

        /// <summary>
        /// Queues query data for logging to a data store
        /// </summary>
        /// <param name="queries">An array of <see cref="Query"/> objects to be logged</param>
        void Enqueue(Query[] queries);

        /// <summary>
        /// Writes query log to a data store
        /// </summary>
        /// <param name="queries">The <see cref="Query"/> object or objects to be logged</param>
        void WriteLog(params Query[] queries);

        /// <summary>
        /// Writes query log to a data store asynchronously
        /// </summary>
        /// <param name="queries">The <see cref="Query"/> object or objects to be logged</param>
        Task WriteLogAsync(params Query[] queries);

        /// <summary>
        /// Alerts designated users in case of possible issues with the query logger service
        /// </summary>
        /// <param name="alert"></param>
        void Alert(Alert alert);
    }
}