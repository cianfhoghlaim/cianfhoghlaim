using System;

namespace Gaois.Localizer
{
    /// <summary>
    /// Specifies options for the <see cref="LocalizationCookies"/> middleware
    /// </summary>
    public class LocalizationCookiesOptions
    {
        /// <summary>
        /// Specifies whether the <see cref="LocalizationCookies"/> middleware should be applied
        /// </summary>
        /// <value>The default value is false</value>
        public bool UseLocalizationCookies { get; set; } = false;

        /// <summary>
        /// The expiration date and time for the cookie
        /// </summary>
        /// <value>The default value is one year</value>
        public DateTimeOffset? Expires { get; set; } = DateTimeOffset.UtcNow.AddYears(1);
        
        /// <summary>
        /// Specifies if this cookie is essential for the application to function correctly.
        /// </summary>
        /// <value>If true then consent policy checks may be bypassed. The default value is false.</value>
        public bool IsEssential { get; set; } = false;
    }
}