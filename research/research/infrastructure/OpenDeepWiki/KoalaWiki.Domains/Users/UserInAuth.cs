namespace KoalaWiki.Domains.Users;

public class UserInAuth : Entity<string>
{
    public string UserId { get; set; } = string.Empty;
    
    public string Provider { get; set; } = string.Empty;
    
    public string AuthId { get; set; } = string.Empty;
}