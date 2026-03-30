using Microsoft.AspNetCore.Builder;

namespace Gaois.Localizer
{
    /// <summary>
    /// Extension methods that handle a <see cref="System.Globalization.CultureNotFoundException"/> in the request pipeline by returning a page in the default culture
    /// </summary>
    public static class RequestCultureExceptionRerouterExtensions
    {
        /// <summary>
        /// Adds middleware that will redirect the user to a page in the default culture whenever a <see cref="System.Globalization.CultureNotFoundException"/> is thrown
        /// </summary>
        /// <remarks>
        /// Use with <see cref="RequestCultureValidation"/> to test for unsupported cultures in the request and handle the exception. Must be placed before UseRequestCultureValidation() in the request execution pipeline.
        /// </remarks>
        public static IApplicationBuilder UseRequestCultureExceptionRerouter(this IApplicationBuilder builder) =>
            builder.UseMiddleware<RequestCultureExceptionRerouter>();

        /// <summary>
        /// Adds middleware that will redirect the user to a page in the default culture whenever a <see cref="System.Globalization.CultureNotFoundException"/> is thrown
        /// </summary>
        /// <remarks>
        /// Use with <see cref="RequestCultureValidation"/> to test for unsupported cultures in the request and handle the exception. Must be placed before UseRequestCultureValidation() in the request execution pipeline.
        /// </remarks>
        /// <param name="builder">The <see cref="IApplicationBuilder"/></param>
        /// <param name="options">The <see cref="RequestCultureRerouterOptions"/> to configure the middleware with</param>
        public static IApplicationBuilder UseRequestCultureExceptionRerouter(
            this IApplicationBuilder builder,
            RequestCultureRerouterOptions options) =>
            builder.UseMiddleware<RequestCultureExceptionRerouter>(options);
    }
}