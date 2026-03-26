namespace KoalaWiki.Options;

public class GithubOptions
{
    public static string ClientId { get; set; }

    public static string ClientSecret { get; set; }

    public static string Token { get; set; }


    public static void InitConfig(IConfiguration configuration)
    {
        ClientId = string.IsNullOrEmpty(configuration["Github:ClientId"])
            ? configuration["GITHUB_CLIENT_ID"]
            : configuration["Github:ClientId"];
        ClientSecret = string.IsNullOrEmpty(configuration["Github:ClientSecret"])
            ? configuration["GITHUB_CLIENT_SECRET"]
            : configuration["Github:ClientSecret"];
        Token = string.IsNullOrEmpty(configuration["Github:Token"])
            ? configuration["GITHUB_TOKEN"]
            : configuration["Github:Token"];
    }
}