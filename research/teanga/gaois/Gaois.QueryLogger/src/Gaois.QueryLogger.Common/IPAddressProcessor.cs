using Ansa.Extensions;
using System.Net;
using System.Net.Sockets;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Provides methods to process and anonymize IP addresses
    /// </summary>
    public static class IPAddressProcessor
    {
        /// <summary>
        /// Assesses whether the IP address is to be anonymized and excutes anonymization if necessary
        /// </summary>
        /// <param name="ip">An IP address</param>
        /// <param name="settings">The <see cref="QueryLoggerSettings"/> to configure the processor with</param>
        public static string Process(string ip, QueryLoggerSettings settings)
        {
            if (!settings.StoreClientIPAddress)
                return "PRIVATE";

            if (ip.IsNullOrWhiteSpace())
                return "UNKNOWN";

            string result = default(string);

            switch (settings.AnonymizeIPAddress)
            {
                case IPAddressAnonymizationLevel.None:
                    result = ip;
                    break;
                case IPAddressAnonymizationLevel.Partial:
                    result = PartiallyAnonymizeIP(ip);
                    break;
                default:
                    result = string.Empty;
                    break;
            }

            return result;
        }

        private static string PartiallyAnonymizeIP(string ip)
        {
            if (IPAddress.TryParse(ip, out IPAddress address))
            {
                if (address.AddressFamily == AddressFamily.InterNetwork)
                {
                    var lastPosition = ip.LastIndexOf(".");
                    return (lastPosition > 0) ? ip.Substring(0, lastPosition) + ".0" : string.Empty;
                }

                if (address.AddressFamily == AddressFamily.InterNetworkV6)
                {
                    var bytes = address.GetAddressBytes();
                    return string.Format("{0:x2}{1:x2}:{2:x2}{3:x2}:{4:x2}{5:x2}:{6:x2}{7:x2}:0000:0000:0000:0000",
                        bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7]);
                }
            }

            return string.Empty;
        }
    }
}