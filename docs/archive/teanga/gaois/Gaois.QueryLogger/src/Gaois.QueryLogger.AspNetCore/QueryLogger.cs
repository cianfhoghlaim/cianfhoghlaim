using Ansa.Extensions;
using Microsoft.Extensions.Options;
using System;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Logs query data to a data store
    /// </summary>
    public class QueryLogger : IQueryLogger
    {
        private readonly IOptionsSnapshot<QueryLoggerSettings> _settings;
        private readonly IHttpContextData _context;
        private readonly ILogStore _store;

        /// <summary>
        /// Logs query data to a data store
        /// </summary>
        public QueryLogger(
            IOptionsSnapshot<QueryLoggerSettings> settings,
            IHttpContextData context,
            ILogStore store)
        {
            _settings = settings;
            _context = context;
            _store = store;
        }

        /// <summary>
        /// Logs query data to a data store
        /// </summary>
        /// <param name="queries">The <see cref="Query"/> object or objects to be logged</param>
        public void Log(params Query[] queries)
        {
            if (!_settings.Value.IsEnabled)
                return;

            foreach (var query in queries)
            {
                var host = _context.Host;
                var ipAddress = (query.IPAddress.IsNullOrWhiteSpace())
                    ? _context.IPAddress : query.IPAddress;

                query.QueryID = (query.QueryID is null) ? Guid.NewGuid() : query.QueryID;
                query.ApplicationName = (query.ApplicationName.IsNullOrWhiteSpace())
                    ? _settings.Value.ApplicationName : query.ApplicationName;
                query.QueryTerms = query.QueryTerms.Truncate(_settings.Value.MaxQueryTermsLength);
                query.QueryText = query.QueryText.Truncate(_settings.Value.MaxQueryTextLength);
                query.Host = (query.Host.IsNullOrWhiteSpace()) ? host : query.Host;
                query.IPAddress = IPAddressProcessor.Process(ipAddress, _settings.Value);
                query.LogDate = (query.LogDate is null) ? DateTime.UtcNow : query.LogDate;
            }

            _store.Enqueue(queries);
        }
    }
}