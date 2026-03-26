using System.Text.Json.Serialization;

namespace KoalaWiki.Services.Feishu.Dto;


public class FeishuInput
{
    public string schema { get; set; }
    public Header header { get; set; }

    [JsonPropertyName("event")]
    public Event Event { get; set; }

    public string? challenge { get; set; }
    public string? encrypt { get; set; }

    public string? type { get; set; }
}

public class Header
{
    public string event_id { get; set; }
    public string event_type { get; set; }
    public string create_time { get; set; }
    public string token { get; set; }
    public string app_id { get; set; }
    public string tenant_key { get; set; }
}

public class Event
{
    public Sender sender { get; set; }
    public Message message { get; set; }
}

public class Sender
{
    public Sender_Id sender_id { get; set; }
    public string sender_type { get; set; }
    public string tenant_key { get; set; }
}

public class Sender_Id
{
    public string union_id { get; set; }
    public string user_id { get; set; }
    public string open_id { get; set; }
}

public class Message
{
    public string message_id { get; set; }
    public string root_id { get; set; }
    public string parent_id { get; set; }
    public string create_time { get; set; }
    public string update_time { get; set; }
    public string chat_id { get; set; }
    public string chat_type { get; set; }
    public string message_type { get; set; }
    public string content { get; set; }
    public Mention[]? mentions { get; set; }
    public string user_agent { get; set; }
}

public class Mention
{
    public string key { get; set; }
    public Id id { get; set; }
    public string name { get; set; }
    public string tenant_key { get; set; }
}

public class Id
{
    public string union_id { get; set; }
    public string user_id { get; set; }
    public string open_id { get; set; }
}