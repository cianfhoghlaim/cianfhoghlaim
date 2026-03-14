using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using Xunit;

namespace Gaois.QueryLogger.Tests.AspNetCore
{
    public class ConfigurationTests
    {
        [Fact]
        public void TypicalConfiguration()
        {
            var configuration = TestHelper.GetQueryLoggerConfiguration("typicalsettings.json");
            var serviceProvider = GetServiceProvider(configuration);
            var settings = serviceProvider.GetService<IOptionsMonitor<QueryLoggerSettings>>();

            // Top level
            Assert.Equal("RecordsApp", settings.CurrentValue.ApplicationName);
            Assert.True(settings.CurrentValue.IsEnabled);
            Assert.Equal(500, settings.CurrentValue.MaxQueryTermsLength);
            Assert.Equal(1000, settings.CurrentValue.MaxQueryTextLength);
            Assert.True(settings.CurrentValue.StoreClientIPAddress);
            Assert.Equal(IPAddressAnonymizationLevel.Partial, settings.CurrentValue.AnonymizeIPAddress);
            Assert.Equal(300000, settings.CurrentValue.AlertInterval);

            // Store
            var storeSettings = settings.CurrentValue.Store;
            Assert.False(string.IsNullOrWhiteSpace(storeSettings.ConnectionString));
            Assert.Equal(30000, storeSettings.MaxQueueRetryInterval);
            Assert.Equal(1000, storeSettings.MaxQueueSize);
            Assert.Equal("QueryLogs", storeSettings.TableName);

            // E-mail
            var emailSettings = settings.CurrentValue.Email;
            Assert.Equal("me@test.ie", emailSettings.ToAddress);
            Assert.Equal("test@test.ie", emailSettings.FromAddress);
            Assert.Equal("RecordsApp — QueryLogger", emailSettings.FromDisplayName);
            Assert.Equal("smtp.myhost.net", emailSettings.SMTPHost);
            Assert.Equal(587, emailSettings.SMTPPort);
            Assert.Equal("MY_USERNAME", emailSettings.SMTPUserName);
            Assert.Equal("MY_PASSWORD", emailSettings.SMTPPassword);
            Assert.True(emailSettings.SMTPEnableSSL);

            // Excluded IP addresses
            var excludedIPSettings = settings.CurrentValue.ExcludedIPAddresses;
            Assert.Equal(2, excludedIPSettings.Count);
            Assert.Equal("Bingbot", excludedIPSettings[0].Name);
            Assert.Equal("207.46.13.0", excludedIPSettings[1].IPAddress);
        }

        [Fact]
        public void AtypicalConfiguration()
        {
            var configuration = TestHelper.GetQueryLoggerConfiguration("atypicalsettings.json");
            var serviceProvider = GetServiceProvider(configuration);
            var settings = serviceProvider.GetService<IOptionsMonitor<QueryLoggerSettings>>();

            // Top level
            Assert.False(settings.CurrentValue.IsEnabled);
            Assert.True(settings.CurrentValue.StoreClientIPAddress);
            Assert.Equal(IPAddressAnonymizationLevel.None, settings.CurrentValue.AnonymizeIPAddress);
            Assert.Equal(60000, settings.CurrentValue.AlertInterval);

            // Store
            var storeSettings = settings.CurrentValue.Store;
            Assert.Equal(30000, storeSettings.MaxQueueRetryInterval);
            Assert.Equal(1000, storeSettings.MaxQueueSize);
            Assert.Equal("SearchStats", storeSettings.TableName);
        }

        private ServiceProvider GetServiceProvider(IConfigurationSection configuration) =>
            new ServiceCollection()
                .Configure<QueryLoggerSettings>(configuration)
                .BuildServiceProvider();
    }
}