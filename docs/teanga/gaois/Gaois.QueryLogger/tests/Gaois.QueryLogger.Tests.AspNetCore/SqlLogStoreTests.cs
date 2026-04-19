using Microsoft.Extensions.DependencyInjection;
using System.Collections.Generic;
using Xunit;

namespace Gaois.QueryLogger.Tests.AspNetCore
{
    public class SqlLogStoreTests
    {
        private readonly ILogStore _store;

        public SqlLogStoreTests()
        {
            var configuration = TestHelper.GetQueryLoggerConfiguration("typicalsettings.json");
            var serviceProvider = new ServiceCollection()
                .Configure<QueryLoggerSettings>(configuration)
                .AddTransient<IAlertService, EmailAlertService>()
                .AddSingleton<ILogStore, MockLogStore>()
                .BuildServiceProvider();
            _store = serviceProvider.GetService<ILogStore>();
        }

        [Fact]
        public void Enqueue()
        {
            var queue = new List<Query>();

            // Add single query
            var query = new Query()
            {
                QueryTerms = "test"
            };
            
            _store.Enqueue(new[] { query });

            if (_store.LogQueue.Reader.TryRead(out Query singleQuery))
                queue.Add(singleQuery);

            Assert.Single(queue);
            Assert.Equal("test", queue[0].QueryTerms);

            // Add multiple queries
            queue = new List<Query>();

            var query1 = new Query()
            {
                QueryTerms = "test1"
            };

            var query2 = new Query()
            {
                QueryTerms = "test2"
            };

            var query3 = new Query()
            {
                QueryTerms = "test3",
            };

            // Test queue size
            _store.Enqueue(new[] { query1, query2, query3 });

            if (_store.LogQueue.Reader.TryRead(out Query q1))
                queue.Add(q1);

            if (_store.LogQueue.Reader.TryRead(out Query q2))
                queue.Add(q2);

            if (_store.LogQueue.Reader.TryRead(out Query q3))
                queue.Add(q3);

            Assert.Equal(3, queue.Count);
            Assert.Equal("test1", queue[0].QueryTerms);
            Assert.Equal("test2", queue[1].QueryTerms);
            Assert.Equal("test3", queue[2].QueryTerms);
        }

        [Fact]
        public async void EnqueueWithExcludedIPAddresses()
        {
            var query1 = new Query()
            {
                QueryTerms = "test1"
            };

            var query2 = new Query()
            {
                QueryTerms = "test2"
            };

            var query3 = new Query()
            {
                QueryTerms = "test3",
                IPAddress = "207.46.13.0"
            };

            // Test queue size: query3 contains an excluded IP address
            _store.Enqueue(new[] { query1, query2, query3 });
            _store.LogQueue.Writer.Complete();

            var queue = new List<Query>();

            while (await _store.LogQueue.Reader.WaitToReadAsync())
            {
                if (_store.LogQueue.Reader.TryRead(out Query query))
                    queue.Add(query);
            }

            Assert.Equal(2, queue.Count);
        }
    }
}