namespace KoalaWiki.Dto;

public class OpenAIResponse
{
    public string model { get; set; }

    public string id { get; set; }

    public Choices[] choices { get; set; }

    public int created { get; set; }

    public bool input_sensitive { get; set; }

    public bool output_sensitive { get; set; }

    public int input_sensitive_type { get; set; }

    public int output_sensitive_type { get; set; }

    public int output_sensitive_int { get; set; }
}

public class Choices
{
    public Delta? delta { get; set; }

    public Delta? message { get; set; }

    public int index { get; set; }
}

public class Delta
{
    public string? role { get; set; }

    public string? content { get; set; }

    public string? name { get; set; }

    public string? audio_content { get; set; }

    public string? reasoning_content { get; set; }
}