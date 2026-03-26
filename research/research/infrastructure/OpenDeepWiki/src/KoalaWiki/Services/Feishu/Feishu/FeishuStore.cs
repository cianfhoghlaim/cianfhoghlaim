using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace KoalaWiki.Services.Feishu.Feishu;

public class FeishuStore : IHostedService, IDisposable
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<FeishuStore> _logger;
    private DateTime? _lastTime;
    private static string _token;
    private Timer _timer;
    private readonly SemaphoreSlim _semaphore = new(1, 1);

    public FeishuStore(IHttpClientFactory httpClientFactory, ILogger<FeishuStore> logger)
    {
        _httpClientFactory = httpClientFactory;
        _logger = logger;
    }

    public static string GetToken()
    {
        if (string.IsNullOrEmpty(_token))
        {
            throw new InvalidOperationException("飞书token未初始化，请确保 FeishuStore 服务已启动");
        }

        return _token;
    }

    /// <summary>
    /// 刷新飞书token
    /// </summary>
    private async ValueTask<string> RefreshTokenAsync()
    {
        await _semaphore.WaitAsync();
        try
        {
            if (!string.IsNullOrEmpty(_token))
            {
                // 如果LastTime大于1.5小时，刷新token
                if (_lastTime != null && DateTime.Now - _lastTime < TimeSpan.FromHours(1.5))
                {
                    return _token;
                }
            }

            await RefreshTokenInternalAsync();
            return _token;
        }
        finally
        {
            _semaphore.Release();
        }
    }

    private async Task RefreshTokenInternalAsync()
    {
        try
        {
            var client = _httpClientFactory.CreateClient(nameof(RefreshTokenAsync));
            var request = new HttpRequestMessage(HttpMethod.Post,
                "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal");

            request.Content = new StringContent(JsonSerializer.Serialize(new
            {
                app_id = FeishuOptions.AppId,
                app_secret = FeishuOptions.AppSecret,
            }), Encoding.UTF8, "application/json");

            var response = await client.SendAsync(request);
            var result = await response.Content.ReadAsStringAsync();
            var token = JsonSerializer.Deserialize<FeiShuToken>(result);

            _token = token.TenantAccessToken;
            _lastTime = DateTime.Now;

            _logger.LogInformation("飞书token已刷新，时间: {RefreshTime}", _lastTime);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "刷新飞书token失败");
        }
    }

    private async void OnTimerElapsed(object state)
    {
        _logger.LogDebug("定时刷新飞书token开始");
        await RefreshTokenInternalAsync();
    }

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("飞书token定时刷新服务启动");

        if (string.IsNullOrEmpty(FeishuOptions.AppId))
        {
            return;
        }

        // 立即刷新一次token
        await RefreshTokenInternalAsync();

        // 设置定时器，每1小时刷新一次token
        _timer = new Timer(OnTimerElapsed, null, TimeSpan.FromHours(1), TimeSpan.FromHours(1));
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("飞书token定时刷新服务停止");
        _timer?.Change(Timeout.Infinite, 0);
        return Task.CompletedTask;
    }

    public void Dispose()
    {
        _timer?.Dispose();
        _semaphore?.Dispose();
    }

    public class FeiShuToken
    {
        [JsonPropertyName("tenant_access_token")]
        public string TenantAccessToken { get; set; }

        [JsonPropertyName("user_access_token")]
        public string UserAccessToken { get; set; }

        [JsonPropertyName("expire")] public int Expire { get; set; }
    }
}