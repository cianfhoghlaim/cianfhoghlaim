---
title: Gaois.QueryLogger (ASP.NET Core)
shortTitle: .NET Core
description: A simple, configurable query logger for ASP.NET and ASP.NET Core applications
keywords: query logger, search, search statistics, open source, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.QueryLogger
nuget: https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/
order: 3
public: true
---

A simple, configurable query logger for ASP.NET Core 2.1+ applications. Find a general introduction to the library [here](../intro).

## Installation and setup

### Database

1. Give the application permissions to a database.
2. Run the [SQL script to create the `QueryLogs` table](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) in the same database.

### Application

Add the NuGet package [Gaois.QueryLogger.AspNetCore](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) to any ASP.NET Core 2.1+ project.

```cmd
dotnet add package Gaois.QueryLogger.AspNetCore
```

Then, in **Startup.cs**, modify the *ConfigureServices* method by adding a call to `services.AddQueryLogger()`. You will need to add an application name and a connection string for your chosen SQL Server data store also:

```csharp
services.AddQueryLogger(settings =>
{
    settings.ApplicationName = "RecordsApp"
    settings.Store.ConnectionString = configuration.GetConnectionString("query_logger");
});
```
Alternatively, load the configuration from your `appsettings.json` file:

```csharp
services.AddQueryLogger(configuration.GetSection("QueryLogger"));
```

Or you can mix the two approaches:

```csharp
services.AddQueryLogger(configuration.GetSection("QueryLogger"), settings =>
{
    settings.IsEnabled = !environment.IsDevelopment();
});
```

Now you can add the `using Gaois.QueryLogger` directive to any C# file to access the library's methods and services.

## Usage

Gaois.QueryLogger is implemented in ASP.NET Core using the framework's recommended conventions for [dependency injection](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection). Pass the query logger dependency to a class constructor via the `IQueryLogger` interface:

```csharp
private readonly IQueryLogger _queryLogger;

public RecordsController(IQueryLogger queryLogger)
{
    _queryLogger = queryLogger;
}

var query = new Query { QueryCategory = "birth_records", QueryTerms = "test", QueryText = Request.Url.Query };
_queryLogger.Log(query);
```

### Log a query

The `Log()` method accepts any number of `Query` objects as parameters.

Example usage:

```csharp
var query = new Query()
{
    QueryCategory = "birth_records",
    QueryTerms = "John Doe Jr.",
    QueryText = Request.Url.Query,
    ResultCount = 27
};

_queryLogger.Log(query);
```

The library automatically obtains the website `Host` and client `IPAddress` properties from the HTTP context. Likewise, if you do not specify a `QueryID` property (in the form of a GUID), one will be created for you. You can, however, overwrite any of these auto-populated values by specifying the relevant property in the `Query` object. See the full list of query data than can be specified [here](../data).

The `Log()` method is fire-and-forget, queries are added synchronously to a thread-safe log queue which is in turn processed asynchronously in a separate thread in an implementation of the Producer-Consumer pattern. This means that logging adds effectively zero overhead to server response time. At the same time, Gaois.QueryLogger is built with fault tolerance and error handling in mind. Learn more [here](../faulttolerance).

### Associate related queries

If you wish to group related queries together — for example different search queries executed on a single page — assign the same `QueryID` property to each of the associated queries:

```csharp
var queryID = Guid.NewGuid();
var searchText = "John Doe Jr.";

var births = new Query()
{
    QueryID = queryID,
    QueryCategory = "birth_records",
    QueryTerms = searchText
};

var deaths = new Query()
{
    QueryID = queryID,
    QueryCategory = "death_records",
    QueryTerms = searchText
};

_queryLogger.Log(births, deaths);
```

## Configuration

As described above, you can use the `services.AddQueryLogger()` method in **Startup.cs** to configure the query logger settings:

```csharp
services.AddQueryLogger(settings =>
{
    settings.IsEnabled = !environment.IsDevelopment();
    settings.StoreClientIPAddress = false;
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
});
```

You can also load the configuration from your JSON configuration file:

```json
{
  "QueryLogger": {
    "ApplicationName": "RecordsApp",
    "IsEnabled": true,
    "Store": {
      "ConnectionString": "Server=localhost;Database=recordsappdb;Trusted_Connection=True;"
    },
    "Email": {
      "ToAddress": "me@test.ie",
      "FromAddress": "test@test.ie",
      "FromDisplayName": "RecordsApp — QueryLogger",
      "SMTPHost": "smtp.myhost.net",
      "SMTPPort": 587,
      "SMTPUserName": "MY_USERNAME",
      "SMTPPassword": "MY_PASSWORD",
      "SMTPEnableSSL": true
    },
    "ExcludedIPAddresses": [
      { "name": "Bingbot", "ipAddress": "40.77.167.0" },
      { "name": "Bingbot", "ipAddress": "207.46.13.0" }
    ]
}
```

See the full list of configurable settings [here](../configuration). The rest of this section describes some useful ways you can make use of the configuration settings.

### Globally enable/disable the query logger

The query logger is enabled by default. However, there may be occasions or particular environments where, for testing or other purposes, you would prefer to disable the query logger without having to wrap each query command in its own conditional logic. To accomodate this, disable the query logger globally within your application by setting `IsEnabled` to `false`.

```csharp
services.AddQueryLogger(settings =>
{
    settings.IsEnabled = false;
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
});
```

### Configure application name

Configure your application name globally and avoid having to specify it for each individual `Query` object you create.

```csharp
services.AddQueryLogger(settings =>
{
    settings.ApplicationName = "My Application";
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
});
```

### Configure IP anonymisation

Use the settings object to configure user IP address anonymisation.

```csharp
services.AddQueryLogger(settings =>
{
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
    settings.AnonymizeIPAddress = IPAddressAnonymizationLevel.None;
});
```

At present the available anonymisation levels are `None` (no anonymisation is applied) and `Partial` (the last octet of an IPv4 client IP address or the last 80 bits of an IPv6 address are removed).

You can also prevent the logger from collecting IP addresses in the first place by configuring the `StoreClientIPAddress` setting:

```csharp
services.AddQueryLogger(settings =>
{
    settings.Store.ConnectionString = Configuration.GetConnectionString("query_logger");
    settings.StoreClientIPAddress = false;
});
```

When `StoreClientIPAddress` is set to `false`, the value `PRIVATE` will be recorded in the `IPAddress` column of your database's query log table. If `StoreClientIPAddress` is set to `true`, but a client IP address cannot be obtained from the HTTP context for any reason, a value of `UNKNOWN` will be recorded.

## Aggregated query logs and log analysis

In [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU we aggregate summary data from our query log table on a monthly basis and store it in a separate database table. We have made the table structure and stored procedures that manage this process available in the [scripts](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) folder in the Gaois.QueryLogger repository in case they are of use to anyone else. Gaois.QueryLogger also has an `AggregratedQueryLog` entity that corresponds to entries in the aggregated log table. The scripts folder also contains some of the more general SQL queries we use to summarise and analyse log data.
