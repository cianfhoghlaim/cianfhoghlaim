namespace Gaois.QueryLogger
{
    /// <summary>
    /// Data obtained from the current HttpContext
    /// </summary>
    public interface IHttpContextData
    {
        /// <summary>
        /// The application host domain
        /// </summary>
        string Host { get; }

        /// <summary>
        /// The client IP address
        /// </summary>
        string IPAddress { get; }
    }
}