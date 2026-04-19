namespace Gaois.QueryLogger
{
    /// <summary>
    /// Service for sending e-mail alerts
    /// </summary>
    public interface IEmailAlertService
    {
        /// <summary>
        /// Sends an e-mail alert
        /// </summary>
        /// <param name="alert">The alert to be sent</param>
        void SendEmail(Alert alert);
    }
}