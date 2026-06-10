namespace Gaois.QueryLogger
{
    /// <summary>
    /// Alerts designated users in case of possible issues with the query logger service
    /// </summary>
    public interface IAlertService
    {
        /// <summary>
        /// Sends an alert
        /// </summary>
        /// <param name="alert">The <see cref="Alert"/> to send</param>
        void Alert(Alert alert);
    }
}