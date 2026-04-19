namespace KoalaWiki.Options;

public class GiteeOptions
{
    public static string ClientId { get; set; }

    public static string ClientSecret { get; set; }

    public static string Token { get; set; }


    public static void InitConfig(IConfiguration configuration)
    {
        ClientId = configuration["Gitee:ClientId"] ?? configuration["GITEE_CLIENT_ID"];
        ClientSecret = configuration["Gitee:ClientSecret"] ?? configuration["GITEE_CLIENT_SECRET"];
        Token = configuration["Gitee:Token"] ?? configuration["GITEE_TOKEN"];
    }
}