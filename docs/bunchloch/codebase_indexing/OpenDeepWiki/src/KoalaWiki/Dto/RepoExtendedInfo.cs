namespace KoalaWiki.Dto;


public class RepoExtendedInfo
{
    public bool Success { get; set; }
    public int Stars { get; set; }
    public int Forks { get; set; }
    public string AvatarUrl { get; set; } = string.Empty;
    public string OwnerUrl { get; set; } = string.Empty;
    public string RepoUrl { get; set; } = string.Empty;
    public string? Language { get; set; }
    public string? License { get; set; }
    public string? Description { get; set; }
    public string? Error { get; set; }
}
