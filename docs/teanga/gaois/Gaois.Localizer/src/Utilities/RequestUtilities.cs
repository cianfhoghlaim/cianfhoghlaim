using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Http.Extensions;

namespace Gaois.Localizer
{
    // TODO: Consider adding other alternate methods consistent with https://github.com/aspnet/AspNetCore/blob/425c196cba530b161b120a57af8f1dd513b96f67/src/Http/Http.Extensions/src/UriHelper.cs
    /// <summary>
    /// Helper methods that extend the <see cref="HttpRequest"/> class
    /// </summary>
    public static class RequestUtilities
    {
        /// <summary>
        /// Similar to the GetDisplayUrl() method that extends <see cref="HttpRequest"/>, 
        /// but allows you to specify a new parameter that will replace an existing parameter
        /// </summary>
        /// <remarks>Useful for obtaining URLs with alternate culture parameter</remarks>
        /// <param name="request">A <see cref="HttpRequest"/> object</param>
        /// <param name="parameterIndex">The index of the URL parameter to be replaced</param>
        /// <param name="replacementParameter">The new replacement parameter</param>
        /// <returns>The new display URL</returns>
        public static string GetDisplayUrl(this HttpRequest request, int parameterIndex, string replacementParameter)
        {
            var parameters = request.Path.Value.Split('/');

            if (parameters is null || parameters.Length <= 1)
                return request.GetDisplayUrl();

            parameters[parameterIndex] = replacementParameter;

            var newPath = string.Join("/", parameters);
            return UrlUtilities.ReplacePath(request, newPath);
        }

        /// <summary>
        /// Similar to the GetEncodedUrl() method that extends <see cref="HttpRequest"/>, 
        /// but allows you to specify a new parameter that will replace an existing parameter
        /// </summary>
        /// <remarks>Useful for obtaining URLs with alternate culture parameter</remarks>
        /// <param name="request">A <see cref="HttpRequest"/> object</param>
        /// <param name="parameterIndex">The index of the URL parameter to be replaced</param>
        /// <param name="replacementParameter">The new replacement parameter</param>
        /// <returns>The new encoded URL</returns>
        public static string GetEncodedUrl(this HttpRequest request, int parameterIndex, string replacementParameter)
        {
            var parameters = request.Path.Value.Split('/');

            if (parameters is null || parameters.Length <= 1)
                return request.GetDisplayUrl();

            parameters[parameterIndex] = replacementParameter;
            var newPath = string.Join("/", parameters);

            return UriHelper.BuildAbsolute(request.Scheme, request.Host, request.PathBase, newPath, request.QueryString);
        }
    }
}