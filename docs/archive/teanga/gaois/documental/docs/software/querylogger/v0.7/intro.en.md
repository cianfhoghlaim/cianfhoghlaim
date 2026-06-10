---
title: Gaois.QueryLogger
description: A simple, configurable query logger for ASP.NET and ASP.NET Core applications
keywords: query logger, search, search statistics, open source, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
github: https://github.com/gaois/Gaois.QueryLogger
order: 1
public: true
---

A simple, configurable query logger for ASP.NET and ASP.NET Core applications. It is the query logger used by [Gaois](https://www.gaois.ie), Fiontar & Scoil na Gaeilge, DCU to log search statistics to SQL Server. Gaois.QueryLogger is a [.NET Standard 2.0](https://docs.microsoft.com/en-us/dotnet/standard/net-standard) library and it supports applications built with ASP.NET Framework 4.6.1 and ASP.NET Core 2.1 or higher.

## Package status

| Package | NuGet Stable | NuGet Prerelease | Downloads |
| ------- | ------------ | ----------------- | --------- |
| Gaois.QueryLogger | N/A | [![NuGet Pre Release](https://img.shields.io/nuget/vpre/Gaois.QueryLogger.svg)](https://www.nuget.org/packages/Gaois.QueryLogger/) | [![NuGet](https://img.shields.io/nuget/dt/Gaois.QueryLogger.svg)](https://www.nuget.org/packages/Gaois.QueryLogger/) |
| Gaois.QueryLogger.AspNetCore | N/A | [![NuGet Pre Release](https://img.shields.io/nuget/vpre/Gaois.QueryLogger.AspNetCore.svg)](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) | [![NuGet](https://img.shields.io/nuget/dt/Gaois.QueryLogger.AspNetCore.svg)](https://www.nuget.org/packages/Gaois.QueryLogger.AspNetCore/) |

## Features

- Log query terms and associated metadata to SQL Server.
- Metadata includes a unique query ID, application name, query category, host server, client IP address, query execution success, query execution duration, result count and datetime information.
- Queries can share a GUID, meaning you can group multiple associated queries.
- Add custom metadata to your logs. We use this to store application-specific data in a multi-application log.
- By default, the library partially anonymises user IP addresses by removing the last octet of IPv4 client IP addresses or the last 80 bits of an IPv6 address. This setting can be turned off.
- Performance: logging adds no additional overhead to server response times.
- Includes its own e-mail notification service that will alert you in the event of any logging errors.

## Documentation

Installation and usage vary slightly according to the target framework. Follow the links below to see the relevant documentation.

- Read the documentation for ASP.NET Framework 4.6.1+ [here](../net461).
- Read the documentation for ASP.NET Core 2.1+ [here](../netcore).

Further documentation regarding [configuration options](../configuration) and [custom log data](../data) is also available.

## Who is using this?

Gaois.QueryLogger is in production use at [www.tearma.ie](https://www.tearma.ie), [www.duchas.ie](https://www.duchas.ie), [www.gaois.ie](https://www.gaois.ie), [www.ainm.ie](https://www.ainm.ie), [www.logainm.ie](https://www.logainm.ie) and [meitheal.logainm.ie](https://meitheal.logainm.ie).

## Additional credits

The architecture of Gaois.QueryLogger is heavily inspired by the [StackExchange.Exceptional](https://github.com/NickCraver/StackExchange.Exceptional) library. Gaois.QueryLogger makes use of two other third-party open-source libraries: [Dapper](https://github.com/StackExchange/Dapper/) and [AutoMapper](https://automapper.org/).
