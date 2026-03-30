namespace Gaois.QueryLogger
{
    /// <summary>
    /// Queries associated with this IP address will not be logged
    /// </summary>
    public class ExcludedIPAddress
    {
        /// <summary>
        /// Optional label describing the IP address source
        /// </summary>
        public string Name { get; set; }

        /// <summary>
        /// The IP address
        /// </summary>
        public string IPAddress { get; set; }
    }
}