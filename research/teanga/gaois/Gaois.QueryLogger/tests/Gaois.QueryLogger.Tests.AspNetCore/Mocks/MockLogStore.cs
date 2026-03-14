using Microsoft.Extensions.Options;
using System;
using System.Threading.Channels;
using System.Threading.Tasks;

namespace Gaois.QueryLogger.Tests.AspNetCore
{
    internal class MockLogStore : ILogStore
    {
        private readonly IOptionsMonitor<QueryLoggerSettings> _settings;
        private readonly IAlertService _alertService;
        private Channel<Query> _logQueue;

        public MockLogStore(
            IOptionsMonitor<QueryLoggerSettings> settings,
            IAlertService alertService)
        {
            _settings = settings;
            _alertService = alertService;
        }

        public Channel<Query> LogQueue => _logQueue ??
            (_logQueue = Channel.CreateBounded<Query>(new BoundedChannelOptions(_settings.CurrentValue.Store.MaxQueueSize)
            {
                FullMode = BoundedChannelFullMode.DropOldest,
                SingleWriter = false,
                SingleReader = true
            }));

        public void Alert(Alert alert) => throw new NotImplementedException();

        public void Enqueue(Query query) => Enqueue(query);

        public void Enqueue(Query[] queries)
        {
            foreach (var query in queries)
            {
                if (_settings.CurrentValue.ExcludedIPAddresses != null
                    && _settings.CurrentValue.ExcludedIPAddresses.Find(x => x.IPAddress == query.IPAddress) != null)
                    continue;

                async Task<bool> RetryWriteAsync(Query q)
                {
                    while (await LogQueue.Writer.WaitToWriteAsync())
                    {
                        if (LogQueue.Writer.TryWrite(q))
                            return true;
                    }

                    return false;
                }

                if (!LogQueue.Writer.TryWrite(query))
                    _ = new ValueTask<bool>(RetryWriteAsync(query));
            }
        }

        public void WriteLog(params Query[] queries) => throw new NotImplementedException();

        public Task WriteLogAsync(params Query[] queries) => throw new NotImplementedException();
    }
}