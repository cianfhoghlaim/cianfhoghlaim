using System;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Threading.Tasks;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Log data to persistent storage
    /// </summary>
    public abstract class LogStore : ILogStore
    {
        /// <summary>
        /// Gets the queue of logs waiting to be written
        /// </summary>
        public abstract Channel<Query> LogQueue { get; }
        
        /// <summary>
        /// Queues query data for logging to a data store
        /// </summary>
        /// <param name="query">The <see cref="Query"/> object to be logged</param>
        public void Enqueue(Query query) => Enqueue(query);

        /// <summary>
        /// Queues query data for logging to a data store
        /// </summary>
        /// <param name="queries">An array of <see cref="Query"/> objects to be logged</param>
        public abstract void Enqueue(Query[] queries);

        /// <summary>
        /// Writes query log to a data store
        /// </summary>
        /// <param name="queries">The <see cref="Query"/> object or objects to be logged</param>
        public abstract void WriteLog(params Query[] queries);

        /// <summary>
        /// Writes query log to a data store asynchronously
        /// </summary>
        /// <param name="queries">The <see cref="Query"/> object or objects to be logged</param>
        public abstract Task WriteLogAsync(params Query[] queries);

        /// <summary>
        /// Alerts designated users in case of possible issues with the query logger service
        /// </summary>
        /// <param name="alert"></param>
        public abstract void Alert(Alert alert);

        /// <summary>
        /// Sends an alert to designated users using the configured alert services
        /// </summary>
        /// <param name="alert"></param>
        protected abstract void SendAlert(Alert alert);

        /// <summary>
        /// Determines whether an alert should be sent
        /// </summary>
        /// <param name="lastAlertTime">Time the last alert was sent</param>
        /// <param name="alertInterval">Interval to wait between sending alerts</param>
        /// <returns>An <see cref="AlertStatus"/></returns>
        protected AlertStatus ShouldAlert(DateTime? lastAlertTime, int alertInterval)
        {
            if (lastAlertTime is null)
                return AlertStatus.NotSet;

            if (lastAlertTime > (DateTime.UtcNow - TimeSpan.FromMilliseconds(alertInterval)))
                return AlertStatus.Wait;

            return AlertStatus.DoSend;
        }
    }
}