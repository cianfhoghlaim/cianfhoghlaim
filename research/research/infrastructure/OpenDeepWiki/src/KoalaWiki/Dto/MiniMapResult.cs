namespace KoalaWiki.Dto;

public class MiniMapResult
{
    public string Title { get; set; }

    public string Url { get; set; }

    public List<MiniMapResult> Nodes { get; set; } = new();
}
