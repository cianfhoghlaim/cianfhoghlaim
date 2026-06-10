using System.Net;

namespace Gaois.Localizer
{
    /// <summary>
    /// Specifies options for the <see cref="RequestCultureExceptionRerouter"/> middleware
    /// </summary>
    public class RequestCultureRerouterOptions
    {
        /// <summary>
        /// Specifies whether the request should be redirected to a page in the default culture whenever a <see cref="System.Globalization.CultureNotFoundException"/> is thrown
        /// </summary>
        /// <value>The defaul value is false</value>
        public bool RerouteRequestCultureExceptions { get; set; } = false;

        /// <summary>
        /// The HTTP status code to return in the response. The default is a 302 <see cref="HttpStatusCode.Redirect"/> code
        /// </summary>
        public int StatusCode = (int)HttpStatusCode.Redirect;
        
        /// <summary>
        /// Specifies a relative path for the redirect URL
        /// </summary>
        public string ResponsePath { get; set; }
    }
}