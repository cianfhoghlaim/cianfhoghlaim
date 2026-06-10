---
title: Adding query data
description: A simple, configurable query logger for ASP.NET and ASP.NET Core applications
keywords: query logger, search, search statistics, open source, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
order: 5
public: true
---

The `Query` object is at the heart of Gaois.QueryLogger. `Query` objects carry the query data that will be logged to your data store. Gaois.QueryLogger will auto-populate certain query data, such as the application host or client IP, prior to logging while other data needs to be specified by your application. All default behaviours can be overridden. The rest of this document describes the various properties available for storing your query data as well as methods that can be called on the `Query` object.

## Data

**QueryID** (`Guid`): A unique ID that represents a specific query or group of queries. A query ID will be created automatically if not specified by your application.

**ApplicationName** (`string`): The name of the application that executes the query. The application name will be retrieved from your configuration settings if not specified in code.

**QueryCategory** (`string`): Relates the query to a category specified by the application. Useful if, for example, you have multiple search types within one application (optional).

**QueryTerms** (`string`): The query term(s) or text content of the query (optional).

**QueryText** (`string`): The raw query text, such as a query string or POST-ed form field (optional).

**Host** (`string`): The application host domain, e.g. www.example.com. Will be automatically obtained from the current HTTP context if not otherwise specified.

**IPAddress** (`string`): The client IP address. Will be automatically obtained from the current HTTP context if not otherwise specified.

**ExecutedSuccessfully** (`bool`, default: `true`): Records whether the query executed successfully.

**ExecutionTime** (`int?`): The query execution time in milliseconds (optional).

**ResultCount** (`int?`): The count of results returned by the query (optional).

**LogDate** (`DateTime`): The date and time of query logging. A value will be automatically generated for this property at time of logging if not otherwise specified.

**JsonData** (`string`): Record additional data in JSON format. Useful for storing application- or query-specific data in a multi-application environment, for example.

## Methods

**ToJson()** (`string`): Returns a JSON representation of a `Query` object.

**FromJson()** (`Query`): Deserialises the provided JSON into a `Query` object.
