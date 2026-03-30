using System.Net;

namespace Gaois.Localizer
{
    /// <summary>
    /// Specifies options for the <see cref="RequireCulturePathParameter"/> middleware
    /// </summary>
    public class RequireCulturePathParameterOptions
    {
        /// <summary>
        /// Specifies whether the request should be redirected to a localized path when no culture parameter is provided
        /// </summary>
        /// <value>The default value is false</value>
        public bool RequireCulturePathParameter { get; set; } = false;

        /// <summary>
        /// The HTTP status code to return in the response. The default is a 302 <see cref="HttpStatusCode.Redirect"/> code
        /// </summary>
        public int StatusCode = (int)HttpStatusCode.Redirect;
    }
}