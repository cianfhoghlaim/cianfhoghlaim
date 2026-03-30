using System.Text.Json.Serialization;

namespace KoalaWiki.Services.Feishu.Feishu;

public class SendMessageInput(string content, string msgType, string receiveId)
{
    [JsonPropertyName("content")] public string content { get; set; } = content;

    [JsonPropertyName("msg_type")] public string msg_type { get; set; } = msgType;

    [JsonPropertyName("receive_id")] public string receive_id { get; set; } = receiveId;
}