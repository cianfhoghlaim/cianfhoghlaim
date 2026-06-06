# Gaois.QueryLogger

A simple, configurable query logger for ASP.NET and ASP.NET Core applications. It is the query logger used by [Fiontar & Scoil na Gaeilge](https://www.gaois.ie), Dublin City University, Ireland to log search statistics to SQL Server. Gaois.QueryLogger is a [.NET Standard 2.0](https://docs.microsoft.com/en-us/dotnet/standard/net-standard) library and it supports applications built with ASP.NET Framework 4.6.1 and ASP.NET Core 2.1 or higher.

[![Build Status](https://dev.azure.com/gaois/Gaois.QueryLogger/_apis/build/status/gaois.Gaois.QueryLogger?branchName=master)](https://dev.azure.com/gaois/Gaois.QueryLogger/_build/latest?definitionId=1&branchName=master)

**Note:** This is a **prerelease version** for testing purposes. The API surface is now relatively stable and we are focusing on adding additonal features, unit tests and documentation.

## Documentation

Learn how to install and configure the query logger on our documentation site at [docs.gaois.ie](https://docs.gaois.ie/en/software/querylogger/v0.7/intro).

## Package status

| Package | NuGet Stable | NuGet Prerelease | Downloads |
| ------- | ------------ | ----------------- | --------- |
| Gaois.QueryLogger | N/A | [![NuGet Pre Release](https://img.shields.io/nuget/vpre/Gaois.QueryLogger.svg)](https://www.nuget.org/packages/Gaois.QueryLogger/) | [![NuGet](https://img.shields.io/nuget/dt/Gaois.QueryLogger.svg)](https://www.nuget.org/packages/Gaois.QueryLogger/) |
| Gaois.QueryLogger.AspNetCore | N/A | [![NuGet Pre Release](https://img.shields.io/nuget/vpre/Gaois.QueryLogger.AspNetCore.svg)](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) | [![NuGet](https://img.shields.io/nuget/dt/Gaois.QueryLogger.AspNetCore.svg)](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) |

## Features

- Log query terms and associated metadata to SQL Server.
- Metadata include a unique query ID, application name, query category, host server, client IP address, query execution success, query execution duration, result count, and datetime information.
- Queries can share a GUID, meaning you can group multiple associated queries.
- Add custom metadata to your logs. We use this to store application-specific data in a multi-application log.
- By default, the library partially anonymises user IP addresses by removing the last octet of IPv4 client IP addresses or the last 80 bits of an IPv6 address. This setting can be turned off.
- Performance: logging adds no additional overhead to server response times. We log over 100,000 queries per day in production with ease.
- Includes its own e-mail notification service that will alert you in the event of any logging errors.
