using Ansa.Extensions;
using System;
using System.Web;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Logs query data to a data store
    /// </summary>
    public static class QueryLogger
    {
        private static QueryLoggerSettings _settings = ConfigurationSettings.Settings;

        /// <summary>
        /// Logs query data to a data store
        /// </summary>
        /// <param name="queries">The <see cref="Query"/> object or objects to be logged</param>
        public static void Log(params Query[] queries)
        {
            if (!_settings.IsEnabled)
                return;

            foreach (var query in queries)
            {
                var host = default(string);
                var ipAddress = default(string);
                var request = HttpContext.Current.Request;

                host = request.Url.Host;
                ipAddress = (query.IPAddress.IsNullOrWhiteSpace())
                    ? request.UserHostAddress : query.IPAddress;

                query.QueryID = (query.QueryID is null) ? Guid.NewGuid() : query.QueryID;
                query.ApplicationName = (query.ApplicationName.IsNullOrWhiteSpace())
                    ? _settings.ApplicationName : query.ApplicationName;
                query.QueryTerms = query.QueryTerms.Truncate(_settings.MaxQueryTermsLength);
                query.QueryText = query.QueryText.Truncate(_settings.MaxQueryTextLength);
                query.Host = (query.Host.IsNullOrWhiteSpace()) ? host : query.Host;
                query.IPAddress = IPAddressProcessor.Process(ipAddress, _settings);
                query.LogDate = (query.LogDate is null) ? DateTime.UtcNow : query.LogDate;
            }

            SqlLogStore.Instance.Enqueue(queries);
        }
    }
}