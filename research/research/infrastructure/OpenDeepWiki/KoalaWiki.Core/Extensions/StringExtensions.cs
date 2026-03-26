using System.Runtime.CompilerServices;

namespace KoalaWiki.Core.Extensions
{
    public static class StringExtensions
    {
        /// <summary>
        /// 对字符串进行安全的 Trim 处理。如果字符串为 null 或空白，则返回空字符串；
        /// 否则返回去除首尾空白后的字符串。
        /// </summary>
        /// <param name="value">要处理的字符串（可为空）</param>
        /// <returns>Trim 后的字符串，或空字符串</returns>
        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public static string GetTrimmedValueOrEmpty(this string? value)
        {
            return !string.IsNullOrWhiteSpace(value) ? value.Trim() : value ?? string.Empty;
        }

        public static string Trim(this string value)
        {
            return !string.IsNullOrWhiteSpace(value) ? value.Trim() : string.Empty;
        }

        public static string TrimStart(this string value, string trimChar)
        {
            if (value.StartsWith(trimChar))
            {
                return value.Substring(trimChar.Length);
            }
            else
            {
                return value;
            }
        }

        public static string TrimEnd(this string value, string trimChar)
        {
            if (value.EndsWith(trimChar))
            {
                return value.Substring(0, value.Length - trimChar.Length);
            }
            else
            {
                return value;
            }
        }
    }
}