using Ansa.Extensions;
using Microsoft.Extensions.Options;
using System;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Alerts designated users via e-mail in case of possible issues with the query logger service
    /// </summary>
    public class EmailAlertService : EmailAlertServiceBase, IAlertService
    {
        private readonly IOptionsMonitor<QueryLoggerSettings> _settings;

        /// <summary>
        /// Alerts designated users via e-mail in case of possible issues with the query logger service
        /// </summary>
        public EmailAlertService(IOptionsMonitor<QueryLoggerSettings> settings)
        {
            _settings = settings;
        }

        /// <summary>
        /// Sends an e-mail alert
        /// </summary>
        /// <param name="alert">The alert to be sent</param>
        public void Alert(Alert alert)
        {
            _ = alert ?? throw new ArgumentNullException(nameof(alert));

            var address = _settings.CurrentValue.Email.ToAddress;
            if (address.IsNullOrWhiteSpace())
                return;

            var subject = "QueryLogger Alert";

            if (_settings.CurrentValue.ApplicationName.HasValue())
                subject += $": {_settings.CurrentValue.ApplicationName}";

            var body = GetAlertBody(subject, alert);

            SendEmail(_settings.CurrentValue.Email, address, subject, body);
        }
    }
}