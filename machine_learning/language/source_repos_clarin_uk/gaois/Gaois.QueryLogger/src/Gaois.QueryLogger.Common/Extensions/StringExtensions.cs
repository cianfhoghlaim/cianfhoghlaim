using Ansa.Extensions;

namespace Gaois.QueryLogger
{
    /// <summary>
    /// Extension methods for strings
    /// </summary>
    public static class StringExtensions
    {
        /// <summary>
        /// Truncates a given string to a given length
        /// </summary>
        /// <param name="value">The string to be truncated</param>
        /// <param name="maxLength">The maximum length of the output string</param>
        public static string Truncate(this string value, int? maxLength)
        {
            if (!(maxLength is int maxStringLength))
                return value;

            if (value.IsNullOrWhiteSpace())
                return value;

            return value.Length <= maxLength ? value : value.Substring(0, maxStringLength);
        }
    }
}