namespace KoalaWiki.Dto;

public class ChatShareMessageInput
{
    public bool IsDeep { get; set; } = false;

    public string Owner { get; set; }

    public string Name { get; set; }
    
    public string Message { get; set; } 
}