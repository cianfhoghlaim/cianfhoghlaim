using Microsoft.AspNetCore.Http;

namespace Gaois.QueryLogger.AspNetCore
{
    /// <summary>
    /// Data obtained from the current HttpContext
    /// </summary>
    public class HttpContextData : IHttpContextData
    {
        private readonly HttpContext _context;

        /// <summary>
        /// Data obtained from the current HttpContext
        /// </summary>
        public HttpContextData(IHttpContextAccessor contextAccessor)
        {
            _context = contextAccessor.HttpContext;
        }

        /// <summary>
        /// The application host domain
        /// </summary>
        public string Host => _context.Request.Host.ToString();

        /// <summary>
        /// The client IP address
        /// </summary>
        public string IPAddress => _context.Connection.RemoteIpAddress.ToString();
    }
}