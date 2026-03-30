namespace KoalaWiki.Dto;

public class ResponsesInput
{
    public List<ResponsesMessageInput> Messages { get; set; } = new();

    /// <summary>
    /// 组织名
    /// </summary>
    /// <returns></returns>
    public string OrganizationName { get; set; } = string.Empty;

    /// <summary>
    /// 仓库名称
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// 应用ID
    /// </summary>
    public string? AppId { get; set; }

    /// <summary>
    /// 是否开启深度研究
    /// </summary>
    public bool DeepResearch { get; set; } = false;
}

public class ResponsesMessageInput
{
    /// <summary>
    /// 消息角色：user, assistant, system
    /// </summary>
    public string Role { get; set; } = string.Empty;

    public List<ResponsesMessageContentInput>? Content { get; set; }
}

/// <summary>
/// 消息内容输入
/// </summary>
public class ResponsesMessageContentInput
{
    public string Type { get; set; } = ResponsesMessageContentType.Text;

    /// <summary>
    /// 文本内容
    /// </summary>
    public string Content { get; set; } = string.Empty;

    /// <summary>
    /// 图片内容
    /// </summary>
    public List<ResponsesMessageContentBase64Input>? ImageContents { get; set; }

    public string? ToolId { get; set; }

    public string? TooResult { get; set; }

    public string? TooArgs { get; set; }
}

public static class ResponsesMessageContentType
{
    public const string Text = "text";

    public const string Tool = "tool";

    public const string Image = "image";

    public const string Code = "code";

    public const string Table = "table";

    public const string Link = "link";

    public const string File = "file";

    public const string Audio = "audio";

    public const string Video = "video";

    public const string Reasoning = "reasoning";

    // Text = 'text',
    // Tool = 'tool',
    // Image = 'image',
    // Code = 'code',
    // Table = 'table',
    // Link = 'link',
    // File = 'file',
    // Audio = 'audio',
    // Video = 'video',
    // Reasoning = 'reasoning',
}

public class ResponsesMessageContentBase64Input
{
    public string Data { get; set; }

    public string MimeType { get; set; }
}