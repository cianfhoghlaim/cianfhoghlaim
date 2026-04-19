namespace Gaois.QueryLogger.Tests.AspNetCore
{
    public class MockHttpContextData : IHttpContextData
    {
        public string Host => "www.recordsapp.com";

        public string IPAddress => "123.45.67.1";
    }
}