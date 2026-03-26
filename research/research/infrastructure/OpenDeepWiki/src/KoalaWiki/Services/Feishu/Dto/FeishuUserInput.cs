namespace KoalaWiki.Services.Feishu.Dto;

public class FeishuUserInput
{
    public string text { get; set; }

    public string image_key { get; set; }

    public string tag { get; set; }

    public bool IsImage => tag.Equals("img", StringComparison.OrdinalIgnoreCase);

    public bool IsText => tag.Equals("text", StringComparison.OrdinalIgnoreCase);

    public bool IsAt => tag.Equals("at", StringComparison.OrdinalIgnoreCase);
}

public class UserInputs
{
    public string title { get; set; }

    public FeishuUserInput[][]? content { get; set; }

    public string? text { get; set; }

    public bool IsText => !string.IsNullOrWhiteSpace(text) && (content == null || content.Length == 0);
}