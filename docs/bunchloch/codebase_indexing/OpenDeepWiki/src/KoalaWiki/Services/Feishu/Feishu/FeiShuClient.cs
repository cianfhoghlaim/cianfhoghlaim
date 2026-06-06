using System.Net.Http.Headers;
using System.Text.Json;
using ImageAgent.Feishu;

namespace KoalaWiki.Services.Feishu.Feishu;

public class FeiShuClient(IHttpClientFactory httpClientFactory, ILogger<FeiShuClient> logger)
{
    private HttpClient GetFeishuClient()
    {
        var client = httpClientFactory.CreateClient("FeiShu");
        return client;
    }


    public async ValueTask SendMessages(SendMessageInput input, string receiveIdType = "open_id")
    {
        var client = GetFeishuClient();
        var result =
            await client.PostAsJsonAsync(
                "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=" + receiveIdType,
                input,JsonSerializerOptions.Web);

        var response = await result.Content.ReadFromJsonAsync<FeiShuResult>();
        
        if (response.code == 0)
        {
            return;
        }

        logger.LogError("发送错误：" + response.msg);
    }


    public async Task SendImageAsync(byte[] bytes, string receive_id, string receiveIdType = "open_id")
    {
        var client = GetFeishuClient();

        using var form = new MultipartFormDataContent();

        // 添加image_type参数
        form.Add(new StringContent("message"), "image_type");

        // 添加图片文件
        var imageContent = new ByteArrayContent(bytes);
        imageContent.Headers.ContentType = MediaTypeHeaderValue.Parse("image/jpeg");
        form.Add(imageContent, "image", "image.jpg");

        var result = await client.PostAsync("https://open.feishu.cn/open-apis/im/v1/images", form);

        var response = await result.Content.ReadFromJsonAsync<FeiShuResult<ImageUploadData>>();

        if (response.code == 0)
        {
            // 构建图片消息内容
            var imageMessage =
                new SendMessageInput(JsonSerializer.Serialize(new { image_key = response.data.image_key }), "image",
                    receive_id);

            // 发送图片消息
            await SendMessages(imageMessage, receiveIdType);

            return;
        }

        logger.LogError("图片上传错误：" + response.msg);
        throw new Exception($"图片上传失败: {response.msg}");
    }

    public async Task<byte[]> DownloadImageAsync(string messageId, string imageKey)
    {
        var client = GetFeishuClient();
        var response =
            await client.GetAsync(
                $"https://open.feishu.cn/open-apis/im/v1/messages/{messageId}/resources/{imageKey}?type=image");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsByteArrayAsync();
    }
}