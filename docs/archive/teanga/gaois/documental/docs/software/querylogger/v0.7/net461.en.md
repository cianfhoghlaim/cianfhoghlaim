---
title: Gaois.QueryLogger (ASP.NET Framework)
shortTitle: .NET Framework
description: A simple, configurable query logger for ASP.NET and ASP.NET Core applications
keywords: query logger, search, search statistics, open source, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.QueryLogger
nuget: https://www.nuget.org/packages/Gaois.QueryLogger/
order: 2
public: true
---

A simple, configurable query logger for ASP.NET Framework 4.6.1+ applications. Find a general introduction to the library [here](../intro).

## Installation and setup

### Database

1. Give the application permissions to a database.
2. Run the [SQL script to create the `QueryLogs` table](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) in the same database.

### Application

Add the NuGet package [Gaois.QueryLogger](https://www.nuget.org/packages/Gaois.QueryLogger/) to any ASP.NET Framework 4.6.1+ project.

```cmd
Install-Package Gaois.QueryLogger
```

Then, configure the query logger in your **Web.config** file. You will need to add a configuration section as well as specifying an application name and a connection string for your chosen SQL Server data store:

```xml
<configSections>
  <section name="QueryLogger" type="Gaois.QueryLogger.ConfigurationSettings, Gaois.QueryLogger" />
</configSections>
```

```xml
<QueryLogger applicationName="RecordsApp" isEnabled="true">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

Now you can add the `using Gaois.QueryLogger` directive to any C# file to access the library's methods and services.

## Usage

### Log a query

The `QueryLogger.Log()` method accepts any number of `Query` objects as parameters.

Example usage:

```csharp
var query = new Query()
{
    QueryCategory = "birth_records",
    QueryTerms = "John Doe Jr.",
    QueryText = Request.Url.Query,
    ResultCount = 27
};

QueryLogger.Log(query);
```

The library automatically obtains the website `Host` and client `IPAddress` properties from the HTTP context. Likewise, if you do not specify a `QueryID` (in the form of a GUID) in the `Query` object, one will be created for you. You can, however, overwrite any of these automatically-created values by specifying the relevant property in the `Query` object. See the full list of query data that can be specified [here](../data).

The `Log()` method is fire-and-forget, queries are added synchronously to a thread-safe log queue which is in turn processed asynchronously in a separate thread in an implementation of the Producer-Consumer pattern. This means that logging adds effectively zero overhead to server response time. At the same time, Gaois.QueryLogger is built with fault tolerance and error handling in mind. Learn more [here](../faulttolerance).

### Associate related queries

If you wish to group related queries together — for example different search queries executed on a single page — pass the associated queries the same `QueryID` parameter:

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

QueryLogger.Log(births, deaths);
```

## Configuration

As described above, you can configure the query logger settings in your **Web.config** file:

```xml
<QueryLogger applicationName="RecordsApp" isEnabled="true">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie"
         fromAddress="test@test.ie"
         fromDisplayName="RecordsApp — QueryLogger"
         smtpHost="smtp.myhost.net"
         smtpPort="587"
         smtpUserName="MY_USERNAME"
         smtpPassword="MY_PASSWORD"
         smtpEnableSSL="true" />
  <ExcludedIPAddresses>
    <add name="Bingbot" ipAddress="40.77.167.0" />
    <add name="Bingbot" ipAddress="207.46.13.0" />
  </ExcludedIPAddresses>
</QueryLogger>
```

See the full list of configurable settings [here](../configuration). The rest of this section describes some useful ways you can make use of the configuration settings.

### Globally enable/disable the query logger

The query logger is enabled by default. However, there may be occasions or particular environments where, for testing or other purposes, you would prefer to disable the query logger without having to wrap each query command in its own conditional logic. To accomodate this, disable the query logger globally within your application by setting `IsEnabled` to `false`.

```xml
<QueryLogger applicationName="RecordsApp" isEnabled="false">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

### Configure application name

Configure your application name globally and avoid having to specify it for each individual `Query` object you create.

```xml
<QueryLogger applicationName="RecordsApp">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

### Configure IP anonymisation

Configure settings regarding user IP address anonymisation.

```xml
<QueryLogger applicationName="RecordsApp" anonymizeIPAddress="None">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

At present the available anonymisation levels are `None` (no anonymisation is applied) and `Partial` (the last octet of an IPv4 client IP address or the last 80 bits of an IPv6 address are removed).

You can also prevent the logger from collecting IP addresses in the first place by configuring the `StoreClientIPAddress` setting:

```xml
<QueryLogger applicationName="RecordsApp" storeClientIPAddress="false">
  <Store connectionString="Server=localhost;Database=recordsappdb;Trusted_Connection=True;" />
  <Email toAddress="me@test.ie" />
</QueryLogger>
```

When `StoreClientIPAddress` is set to `false`, the value `PRIVATE` will be recorded in the `IPAddress` column of your database's query log table. If `StoreClientIPAddress` is set to `true`, but a client IP address cannot be obtained from the HTTP context for any reason, a value of `UNKNOWN` will be recorded.

## Aggregated query logs and log analysis

In [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU we aggregate summary data from our query log table on a monthly basis and store it in a separate database table. We have made the table structure and stored procedures that manage this process available in the [scripts](https://github.com/gaois/Gaois.QueryLogger/tree/master/scripts) folder in the Gaois.QueryLogger GitHub repository in case they are of use to anyone else. Gaois.QueryLogger also has an `AggregratedQueryLog` entity that corresponds to entries in the aggregated log table. The scripts folder also contains some of the more general SQL queries we use to summarise and analyse log data.
