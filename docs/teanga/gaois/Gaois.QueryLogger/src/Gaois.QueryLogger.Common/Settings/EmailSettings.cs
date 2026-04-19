using Ansa.Extensions;
using System.Net;
using System.Net.Mail;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Email settings configuration
    /// </summary>
    public class EmailSettings
    {
        /// <summary>
        /// Represents the address of the e-mail sender
        /// </summary>
        public MailAddress FromMailAddress { get; private set; }

        /// <summary>
        /// Provides credentials for SMTP authentication
        /// </summary>
        public NetworkCredential SMTPCredentials { get; private set; }

        /// <summary>
        /// The address to which e-mail messages will be sent
        /// </summary>
        public string ToAddress { get; set; }

        private string _fromAddress;
        /// <summary>
        /// The address from which e-mail messages will be sent
        /// </summary>
        public string FromAddress
        {
            get => _fromAddress;
            set
            {
                _fromAddress = value;
                SetMailAddress();
            }
        }

        private string _fromDisplayName;
        /// <summary>
        /// The display name with which e-mail messages will be sent
        /// </summary>
        public string FromDisplayName
        {
            get => _fromDisplayName;
            set
            {
                _fromDisplayName = value;
                SetMailAddress();
            }
        }

        /// <summary>
        /// The SMTP server through which mail will be sent
        /// </summary>
        public string SMTPHost { get; set; }

        /// <summary>
        /// The port via which mail will be sent (if SMTP server is specified via <see cref="SMTPHost"/>).
        /// </summary>
        public int? SMTPPort { get; set; }

        private string _smtpUserName;
        /// <summary>
        /// The SMTP user name to use, if authentication is required
        /// </summary>
        public string SMTPUserName
        {
            get => _smtpUserName;
            set
            {
                _smtpUserName = value;
                SetCredentials();
            }
        }

        private string _smtpPassword;
        /// <summary>
        /// The SMTP password to use, if authentication is required
        /// </summary>
        public string SMTPPassword
        {
            get => _smtpPassword;
            set
            {
                _smtpPassword = value;
                SetCredentials();
            }
        }

        /// <summary>
        /// Whether to use SSL when sending via SMTP
        /// </summary>
        public bool SMTPEnableSSL { get; set; }

        private void SetMailAddress()
        {
            try
            {
                FromMailAddress = _fromDisplayName.HasValue()
                    ? new MailAddress(_fromAddress, _fromDisplayName)
                    : new MailAddress(_fromAddress);
            }
            catch
            {
                FromMailAddress = null;
            }
        }

        private void SetCredentials() =>
            SMTPCredentials = _smtpUserName.HasValue() && _smtpPassword.HasValue()
                ? new NetworkCredential(_smtpUserName, _smtpPassword)
                : null;
    }
}