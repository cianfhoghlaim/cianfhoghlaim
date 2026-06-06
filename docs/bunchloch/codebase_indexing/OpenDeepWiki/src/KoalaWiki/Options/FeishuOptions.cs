namespace KoalaWiki.Options;

public class FeishuOptions
{
    public static string AppId { get; set; }

    public static string AppSecret { get; set; }

    public static string FeishuBotName { get; set; }


    public static void InitConfig(IConfiguration configuration)
    {
        AppId = configuration["FeishuAppId"];
        AppSecret = configuration["FeishuAppSecret"];
        FeishuBotName = configuration["FeishuBotName"];
    }
}