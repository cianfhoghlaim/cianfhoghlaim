using Xunit;

namespace Gaois.QueryLogger.Tests
{
    public class IPAddressProcessorTests
    {
        [Fact]
        public void IPAddressProcessorStorageDisabled()
        {
            var settings = new QueryLoggerSettings()
            {
                StoreClientIPAddress = false
            };

            var result = IPAddressProcessor.Process("40.77.167.0", settings);

            Assert.Equal("PRIVATE", result);
        }

        [Fact]
        public void IPAddressProcessorIPUnknown()
        {
            var settings = new QueryLoggerSettings()
            {
                StoreClientIPAddress = true
            };

            var result = IPAddressProcessor.Process("", settings);

            Assert.Equal("UNKNOWN", result);
        }

        [Fact]
        public void IPAddressProcessorNoAnonymization()
        {
            var settings = new QueryLoggerSettings()
            {
                StoreClientIPAddress = true,
                AnonymizeIPAddress = IPAddressAnonymizationLevel.None
            };

            var result = IPAddressProcessor.Process("40.77.167.0", settings);

            Assert.Equal("40.77.167.0", result);
        }

        [Fact]
        public void IPAddressProcessorPartialAnonymizationIPv4()
        {
            var settings = new QueryLoggerSettings()
            {
                StoreClientIPAddress = true,
                AnonymizeIPAddress = IPAddressAnonymizationLevel.Partial
            };

            var result = IPAddressProcessor.Process("40.77.167.23", settings);

            Assert.Equal("40.77.167.0", result);
        }

        [Fact]
        public void IPAddressProcessorPartialAnonymizationIPv6()
        {
            var settings = new QueryLoggerSettings()
            {
                StoreClientIPAddress = true,
                AnonymizeIPAddress = IPAddressAnonymizationLevel.Partial
            };

            var result = IPAddressProcessor.Process("2001:0db8:85a3:0000:0000:8a2e:0370:7334", settings);

            Assert.Equal("2001:0db8:85a3:0000:0000:0000:0000:0000", result);
        }
    }
}