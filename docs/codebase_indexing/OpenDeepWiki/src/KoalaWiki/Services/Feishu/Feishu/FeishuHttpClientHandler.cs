using System.Net.Http.Headers;
using KoalaWiki.Services.Feishu.Feishu;

namespace ImageAgent.Feishu;

/// <summary>
/// 飞书 HTTP 客户端处理器，自动添加授权头
/// </summary>
public class FeishuHttpClientHandler : DelegatingHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", FeishuStore.GetToken());

        return base.SendAsync(request, cancellationToken);
    }
}