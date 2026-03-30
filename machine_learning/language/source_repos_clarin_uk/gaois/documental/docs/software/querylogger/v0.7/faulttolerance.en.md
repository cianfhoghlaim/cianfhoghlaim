---
title: Fault tolerance and error handling
shortTitle: Error handling
description: A simple, configurable query logger for ASP.NET and ASP.NET Core applications
keywords: query logger, search, search statistics, open source, C#, .NET Core, dotnet, SQL Server, Fiontar & Scoil na Gaeilge, DCU
order: 6
toc: false
public: true
---

Gaois.QueryLogger is built with fault tolerance and high-volume/high-concurrency environments in mind. As part of the logging process queries are placed in a concurrent queue in a separate background thread prior to data persistence. This is part of the reason why the `Log()` method adds little to no overhead to your server response time. Enqueuing is a synchronous, near-instant process, while the process of writing the logs to the database happens asynchronously in another thread (a particular flavour of the Producer-Consumer pattern). Gaois.QueryLogger utilises data structures provided by the [System.Threading.Channels](https://docs.microsoft.com/en-us/dotnet/api/system.threading.channels) library for high-performance asynchronous logging.

Queuing the logs also means that, in the event of a passing database I/O issue (maybe you are experiencing high traffic or a particularly expensive query is running on the database), the logs are preserved in memory until the write process can be successfully retried. You can specify the maximum queue size and retry interval in the [configuration settings](../configuration). In the event that the maximum queue size is reached, logs are discarded from the queue on a First-In First-Out basis.

## Alert service

Because the log queue is consumed in a background thread, database errors and any other write-related exceptions will not be returned to the calling thread. It's important, however, that you know if the logging service is experiencing issues for any reason. To this end, Gaois.QueryLogger comes with an e-mail alert service out of the box. Specify your mail details in the [configuration settings](../configuration) and you will be notified of any problems. Setting the `AlertInterval` ensures that you do not receive many duplicate e-mails if the log queue gets backed up.
