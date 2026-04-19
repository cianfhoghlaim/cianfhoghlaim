using Ansa.Extensions;
using System.Net.Mail;
using System.Text;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Base methods for a derived EmailAlertService class
    /// </summary>
    public class EmailAlertServiceBase
    {
        /// <summary>
        /// Creates a <see cref="SmtpClient"/> using configuration file settings
        /// </summary>
        /// <param name="settings">An instance of the <see cref="EmailSettings"/> class</param>
        /// <returns>An instance of the <see cref="SmtpClient"/> class</returns>
        protected SmtpClient GetClient(EmailSettings settings)
        {
            // In NET461 creating a new SmtpClient instance gets mail settings from Web.config, if present
            var client = new SmtpClient();

            // If NET461 or netstandard these settings can be overridden by settings in a configured QueryLoggerSettings instance
            if (settings.SMTPCredentials != null)
                client.Credentials = settings.SMTPCredentials;

            if (settings.SMTPHost.HasValue())
                client.Host = settings.SMTPHost;

            if (settings.SMTPPort != null)
                client.Port = settings.SMTPPort.Value;

            if (settings.SMTPEnableSSL)
                client.EnableSsl = true;

            return client;
        }

        /// <summary>
        /// Sends an e-mail using the specified settings
        /// </summary>
        /// <param name="settings">An instance of the <see cref="EmailSettings"/> class</param>
        /// <param name="address">The address or addresses to which mail will be sent</param>
        /// <param name="subject">The e-mail subject line</param>
        /// <param name="body">The e-mail body</param>
        protected void SendEmail(EmailSettings settings, string address, string subject, string body)
        {
            if (address.IsNullOrWhiteSpace())
                return;

            using (var message = new MailMessage())
            {
                message.To.Add(address);

                if (settings.FromMailAddress != null)
                    message.From = settings.FromMailAddress;

                message.Subject = subject;
                message.Body = body;
                message.IsBodyHtml = true;

                using (var client = GetClient(settings))
                    client.Send(message);
            }
        }

        /// <summary>
        /// Generates the alert e-mail body
        /// </summary>
        /// <param name="title">The e-mail title</param>
        /// <param name="alert">The <see cref="Alert"/> instance</param>
        /// <returns>The HTML e-mail body</returns>
        protected string GetAlertBody(string title, Alert alert)
        {
            var sb = new StringBuilder();

            // HTML opening tags & head
            sb.Append("<!doctype html>");
            sb.AppendLine("<html>");
            sb.AppendLine("<head>");
            sb.AppendLine("<meta name=\"viewport\" content=\"width=device-width\" />");
            sb.AppendLine("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />");
            sb.AppendLine("<title>");
            sb.Append(title);
            sb.AppendLine("</title>");
            sb.AppendLine("</head>");
            sb.AppendLine("<body>");

            // Body inner HTML
            sb.AppendParagraph(alert.Type);

            // Add query data
            if (alert.Query != null)
            {
                sb.Append("<table>");
                sb.Append($"<tr>Query ID<td></td><td>{alert.Query.QueryID}</td></tr>");
                sb.Append($"<tr>Application Name<td></td><td>{alert.Query.ApplicationName}</td></tr>");
                sb.Append($"<tr>Query Category<td></td><td>{alert.Query.QueryCategory}</td></tr>");
                sb.Append($"<tr>Query Terms<td></td><td>{alert.Query.QueryTerms}</td></tr>");
                sb.Append($"<tr>Query Text<td></td><td>{alert.Query.QueryText}</td></tr>");
                sb.Append($"<tr>Host<td></td><td>{alert.Query.Host}</td></tr>");
                sb.Append($"<tr>Log Date<td></td><td>{alert.Query.LogDate}</td></tr>");
                sb.Append("</table>");
            }

            // Add exception data
            if (alert.Exception != null)
            {
                sb.AppendParagraph(alert.Exception.Message);
                sb.AppendLine(alert.Exception.StackTrace);
            }

            sb.AppendLineBreak();

            // HTML closing tags
            sb.AppendLine("</body>");
            sb.AppendLine("</html>");

            return sb.ToString();
        }
    }
}