---
title: Gaois.Localizer
description: A toolkit for creating multilingual web applications on ASP.NET Core
keywords: localization, internationalization, software, open source, C#, .NET Core, dotnet, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.Localizer
nuget: https://www.nuget.org/packages/Gaois.Localizer/
public: true
---

**Note:** This is a **prerelease version** for testing purposes. Expect some breaking changes and renamed API methods before we reach a 1.0 release.

This is a toolkit for creating multilingual web applications on ASP.NET Core. It offers a suite of configurable localisation middleware, including request culture validators, cookie management, exception handlers and URL rewriting rules, that wrap and extend the framework's native [globalisation and localisation](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/localization?view=aspnetcore-2.1) functions to take the pain out of building localised websites.

The library was developed by [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU where we use it to build our own multilingual web applications.

## Features

The library provides out-of-the-box functionality that allows you to:

- Get the request culture from URL path parameters such as `www.mymultilingualapp.com/en-GB/about/` and `www.mymultilingualapp.com/ga/about/`.
- Use cookies and HTTP `Accept-Language` headers to infer the user's desired culture when they visit the website homepage, e.g. `www.mymultilingualapp.com`, where no path parameters are present.
- Handle requests to unsupported cultures, either by returning a 404 error page or redirecting the user to a page in the default language.
- Exclude certain routes from being affected by the localisation middleware.
- Manage and configure settings related to localisation cookies, so that the user's language preferences can be persisted across browsing sessions.
- Decide if users should be redirected to a localised URL when they first request the website homepage.
- Handle scenarios where you wish to internally map a two- or three-letter ISO language code in the URL to a region or an extended language subtag.

Most of these features are configurable: sensible defaults are supplied, but you get to specify which types of redirects to use, how long before cookies expire, etc. The library was also designed very much with SEO in mind and the default setup offers an optimal localisation solution when it comes to being indexed by major search engines. The localizer middleware plays nice, even when the application is run in a virtual directory.

## Install and setup

Add the NuGet package [Gaois.Localizer](https://www.nuget.org/packages/Gaois.Localizer/) to any ASP.NET Core 2.1+ project.

```cmd
dotnet add package Gaois.Localizer
```

Then in **Startup.cs**, add the `using Gaois.Localizer` directive to the top of the file. All configuration of the package is done in this file. The specific configuration for your application will depend on your own needs.

### Basic configuration

1. Add the `app.UseLocalizer()` middleware to the *Configure* method anywhere after `app.UseStaticFiles` (if present) and before `app.UseMvc()`, like so:

```csharp
public void Configure(IApplicationBuilder app, IHostingEnvironment env)
{
    if (env.IsDevelopment())
    {
        app.UseDeveloperExceptionPage();
    }
    else
    {
        app.UseExceptionHandler("/Error");
        app.UseStatusCodePagesWithReExecute("/Error/{0}");
    }

    app.UseStaticFiles();

    app.UseLocalizer();

    app.UseMvc(routes =>
    {
        routes.MapRoute(
            name: "default",
            template: "{controller=Home}/{action=Index}/{id?}");
    });
}
```

2. Modify the *ConfigureServices* method:

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddLocalization(options =>
    {
        options.ResourcesPath = "Resources";
    });

    services.AddMvc()
        .SetCompatibilityVersion(CompatibilityVersion.Version_2_1)
        .AddRazorPagesOptions(options =>
        {
            options.RootDirectory = "/Pages";
            options.Conventions.AddPageRoute("/Index", route: "{culture?}");
            options.Conventions.AddPageRoute("/About", route: "{culture}/about/{id?}");
            options.Conventions.AddPageRoute("/Error", route: "/Error/{0}");
        })
        .AddViewLocalization(LanguageViewLocationExpanderFormat.Suffix, options =>
        {
            options.ResourcesPath = "Resources";
        })
        .AddDataAnnotationsLocalization();

    services.AddLocalizer(options =>
    {
        var supportedCultures = new[]
        {
            new CultureInfo("en-GB"),
            new CultureInfo("ga-IE")
        };
        options.SupportedCultures = supportedCultures;
        options.SupportedUICultures = supportedCultures;
        options.DefaultRequestCulture = new RequestCulture(culture: "en-GB", uiCulture: "en-GB");
    });
}
```

The `SupportedCultures`, `SupportedUICultures` and `DefaultRequestCulture` options are required.

## Getting the request culture

The primary goal of this package is to make it easier to understand what language the user intends to use when accessing your website so that the application can set the correct culture and localise the contents for the user. The minimal configuration discussed previously contains all you need to interpret the request culture from a URL:

```csharp
public void ConfigureServices(IServiceCollection services)
{
    ...

    services.AddLocalizer(options =>
    {
        var supportedCultures = new[]
        {
            new CultureInfo("en-GB"),
            new CultureInfo("ga-IE")
        };
        options.SupportedCultures = supportedCultures;
        options.SupportedUICultures = supportedCultures;
        options.DefaultRequestCulture = new RequestCulture(culture: "en-GB", uiCulture: "en-GB");
    });
}
```

The `supportedCultures` variables lists the languages and culture types we wish to support in the application. The `DefaultRequestCulture` provides the ultimate fallback if the desired culture cannot be inferred from the HTTP request.

The localizer middleware parses the HTTP request and returns a target culture according to the following criteria:

1. The presence of a culture path parameter, i.e. an [IETF language tag](https://en.wikipedia.org/wiki/IETF_language_tag), in the request URL (e.g. the 'ga-IE' parameter in `www.mymultilingualapp.com/ga-IE/`).
2. The request contains a culture cookie previously obtained from the website (see [below](#localisation-cookies)).
3. The user has specified a desired language in their browser (obtained via the HTTP `Accept-Language` header) that matches one of the application's supported cultures.
4. The default language specified in the `RequestLocalizationOptions` service.

The first criterion to return a non-null result will be used. Thus, a user who accesses `www.mymultilingualapp.com/ru-RU/` will be shown a page in Russian, regardless of their browser settings. A user who has selected `en` as their preferred language in their browser and visits `www.mymultilingualapp.com` will be shown a page in English, etc.

These checks are performed once the `app.UseLocalizer()` method is reached in the request execution pipeline. All middleware and application logic called subsequent to this can access the request culture via the `CultureInfo.CurrentCulture` object.

### Configure the culture path parameter

By default, Gaois.Localizer assumes that the first request path parameter, i.e. the `ga-IE` parameter in the URL `www.mymultilingualapp.com/ga-IE/about/our-story/`, contains the target culture information, as is common practice. You can configure the application to use a different parameter index, however:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RouteCulture.CultureParameterIndex = 2;
});
```

Now, the application will attempt to use the second path parameter in the request when evaluating the request culture, meaning that a URL such as `www.mymultilingualapp.com/shop/fr-FR/products/` will work as expected.

### A word about SEO

In what is probably the most opinionated feature of this library, preference is always given to a culture obtained from a URL path parameter over client cookie or HTTP header settings. This means that if a user visits `www.mymultilingualapp.com/en-GB/` and their preferred browser language is US English (en-US) they will still receive the page in United Kingdom English (en-GB), provided this is a supported culture within the application. This means that (i) users get the page they expected to open when they clicked the URL, and (ii) search crawlers can reliably associate URLs with localised content. We believe this is optimal for SEO and for user experience. Having opened the page, users should be able to voluntarily switch languages via a dedicated language switcher in the UI.

## Unsupported cultures

What happens when a user inputs a URL that contains an unsupported culture? For instance, if your site supports Spanish and Portugese content, but the user supplies an `fr-FR` region subtag in the URL. Internally, the localization middleware will throw a `CultureNotFoundException` in this scenario. Gaois.Localizer offers two ways to handle this error.

### Return a '404 Not Found' status code

By default, a request to an unsupported culture will cause a '404 Not Found' HTTP status code to be returned in the response and the user will be shown an appropriate message, provided that an error page route has been configured. This may be the ideal approach in terms of SEO. Search engines will be in no doubt that content is not available at the requested URL.

### Redirect the user to a page in the default culture

This may, in some cases, be the preferred option for user experience. When a URL containing an unsupported culture is accessed the client will be redirected to an equivalent page in the default culture of the application. To implement this, configure the `RequestCultureRerouter` in the *ConfigureServices* method in **Startup.cs**. By default, the response will return a 302 redirect to the same path with an updated culture parameter.

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RequestCultureRerouter.RerouteRequestCultureExceptions = true;
});
```

#### Configure the rerouter

You can further configure the rerouter to send a different HTTP status code in the response or to have redirects routed to a particular path.

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RequestCultureRerouter.RerouteRequestCultureExceptions = true;
    options.RequestCultureRerouter.StatusCode = 301;
    options.RequestCultureRerouter.ResponsePath = "/en-GB/lost/";
});
```

## Excluding routes

While you might use the first parameter of your request path to represent the target culture most of the time, you may wish to exclude certain routes from the localisation pipeline, for example `www.mymultilingualapp.com/api/v1.2/`. Using the out-of-the-box configuration, a URL such as this will throw a `CultureNotFoundException`. However, you can prevent this by excluding certain routes within your service configuration:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RouteCulture.ExcludedRoutes.Add(@"^/api");
    options.RouteCulture.ExcludedRoutes.Add(@"^/content");
});
```

Paths are defined in the form of regex strings. Routes beginning with `/error`, e.g. `/Error` or `/error/{0}/`, are added by default to the exclusion list in order to prevent circular routing issues when a `CultureNotFoundException` is thrown.

## Localisation cookies

When a user visits your website, they may decide to select another language via a language switcher or similar UI facility. It can be useful to store the user's preference in a cookie so that the application will remember their choice and the user can pick up where they left off on their next visit. Fortunately, ASP.NET Core has a built-in [provider](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/localization?view=aspnetcore-2.1#set-the-culture-programmatically) to append culture cookies to the HTTP response. Gaois.Localizer wraps this provider in some useful logic that lives in the request execution pipeline, thus foregoing the need for POST requests or additional controllers to programatically set and update the user's language preferences. All you need to do is configure the *AddLocalizer* method in **Startup.cs**:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.LocalizationCookies.UseLocalizationCookies = true;
});
```

The localisation cookies middleware will ensure that your site is displayed in the user's preferred culture every time they visit the homepage. Don't forget, however, that the localisation tools [give precedence to the culture in the URL path parameters over any other settings](#a-word-about-seo), so, if the user follows a link to a page in a particular culture, localisation cookies will not be taken into account.

### Configure the localisation cookies

Optionally, you can further configure the localisation cookies settings, allowing you to specify both the cookie expiration date and whether the cookie is essential for the application to function. The default values are `1 year` and `false`, respectively. The `IsEssential` property should be configured with respect to your privacy and data protection policies. If true, then consent policy checks may be bypassed.

```csharp
services.AddLocalizer(options =>
{
    ...
    options.LocalizationCookies.UseLocalizationCookies = true;
    options.LocalizationCookies.Expires = DateTime.UtcNow.AddDays(5);
    options.LocalizationCookies.IsEssential = true;
});
```

## Landing page redirection

When a user visits a website's homepage, e.g. `www.mymultilingualapp.com`, it may sometimes be desirable to automatically redirect them to the URL for a localised version of that page, e.g. `www.mymultilingualapp.com/es`. This is not the default behaviour when using Gaois.Localizer for reasons of SEO (see below) but we recognise that it is a common use case. To turn on landing page redirection, again just configure the *AddLocalizer* method in **Startup.cs**:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RequireCulturePathParameter.RequireCulturePathParameter = true;
});
```

The redirect URL automatically respects settings configured in the [`Microsoft.AspNetCore.Routing.RouteOptions`](https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.routing.routeoptions?view=aspnetcore-2.1) service as regards whether a trailing slash should be appended to the generated URL.

### Another word about SEO

Numerous approaches can be taken when localising a website's homepage. Some websites will evaluate a user's preferred language and redirect them to a new URL, such as moving from `example.com` to `example.com/es`. This can be problematic, however, due to the nature of HTTP redirects and how they interact with the browser:

- Some websites (for example, [mozilla.org](https://www.mozilla.org/)) examine the browser's language preferences and implement a 301 (permanent) redirect. This is fine if you are reasonably certain that most users will access the application in one language only. However, many browsers indefinitely cache 301 redirects, meaning that even if the user later updates their browser settings — or they access the computer in a public location such as a school or a library — the browser will always take them to the first localised version of the site that was opened in that browser.
- Many other websites implement 302 redirects, likely for the reasons described above. However, it is unclear whether some major web crawlers pay attention to pages with 302 redirects and this may not be ideal for SEO.

That is why the default approach using the Gaois.Localizer library is not to redirect the user (i.e. the user stays on `example.com`), though the culture information will still be localised according to the criteria outlined [above](#getting-the-request-culture). We feel this gives optimal results both in terms of SEO and user experience.

## Language tag choice

The library is agnostic as to which type of [IETF language tag](https://en.wikipedia.org/wiki/IETF_language_tag) you use in your URL to signify the target culture. The examples in this documentation use region subtags such as `ga-IE`, `en-GB`, `pt-BR`, etc. Many applications prefer ISO two-letter language codes such as `ga`, `en`, `fr`. You can specify either type of tag in the supported cultures variable of your `RequestLocalizationOptions` in **Startup.cs**.

If you do opt for two-letter language codes it can often be helpful to store a set of region or extended language subtags that map to your language codes — for example, when supplying locale data in [Open Graph](http://ogp.me/) meta tags. Gaois.Localizer facilitates this by allowing you to configure the route culture options in the *Configure* method of **Startup.cs**:

```csharp
services.AddLocalizer(options =>
{
    ...
    options.RouteCulture.LanguageLocaleMap.Add("en", "en-GB");
    options.RouteCulture.LanguageLocaleMap.Add("ga", "ga-IE");
});
```

The mapped tags can then be accessed elsewhere in the application, and an `InferLocaleFromLanguage()` convenience function is provided to output the correct locale or region subtag when given a corresponding language code.

Example usage (Razor view):

```csharp
@using Gaois.Localizer
@inject IOptions<RequestLocalizationOptions> LocalizationOptions
@inject IOptions<RouteCultureOptions> CultureOptions

...

@foreach (var culture in LocalizationOptions.Value.SupportedUICultures)
{
    if (culture.Name != CultureInfo.CurrentCulture.Name)
    {
        string lang = @culture.TwoLetterISOLanguageName;
        string locale = CultureOptions.Value.InferLocaleFromLanguage(@lang);
        <link rel="alternate" hreflang="@lang" href="https://www.mymultilingualapp.com/(@lang)">
        <meta property="og:locale:alternate" content="@locale">
    }
}
```

## Migrating between language tags in a URL scheme

If you wish to migrate from a URL scheme that used two-letter language tags (such as `example.com/es`) to a scheme that uses regional locales (such as `example.com/es-ES`), Gaois.Localizer includes a helpful redirection protocol that leverages ASP.NET Core's native URL rewriting middleware to take care of the hard work for you.

First, configure the *AddLocalizer* method as described in the [previous section](#language-tag-choice):

```csharp
public void ConfigureServices(IServiceCollection services)
{
    ...

    services.AddLocalizer(options =>
    {
        ...
        options.RouteCulture.LanguageLocaleMap.Add("en", "en-GB");
        options.RouteCulture.LanguageLocaleMap.Add("ga", "ga-IE");
    });

    ...
}
```

You can then pass the `LanguageLocaleMap` to a `RedirectLanguageToLocale` object in the URL rewriting middleware:

```csharp
public void Configure(IApplicationBuilder app, IHostingEnvironment env)
{
    ...

    var routeCultureOptions = app.ApplicationServices
        .GetService<IOptions<RouteCultureOptions>>().Value;

    var rewriteOptions = new RewriteOptions()
        .Add(new RedirectLanguageToLocale(routeCultureOptions.LanguageLocaleMap));

    app.UseRewriter(rewriteOptions);

    ...

    app.UseMvc();
}
```

Now, all requests to `www.mymultilingualapp.com/ga/about/` will be automatically redirected to `www.mymultilingualapp.com/ga-IE/about/`. The `RedirectLanguageToLocale` object implements a 302 redirect by default, but you can specify a 301 or other redirect type in an optional argument.

## Helper methods

Gaois.Localizer also contains extension methods that aid common localisation-related tasks.

### GetDisplayUrl()

This method extends the [*GetDisplayUrl()*](https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.extensions.urihelper.getdisplayurl?view=aspnetcore-2.2) method, allowing you to replace a URL path parameter (if present) by index.

### GetEncodedUrl()

This is equivalent to the previous method, except that it returns a fully URL-encoded string. In the context of web application localisation, this method is particularly useful when it comes to generating alternate links with alternate culture parameters:

```c#
<link rel="alternate" hreflang="@lang" href="@Context.Request.GetEncodedUrl(1, "fr-FR")">
```
