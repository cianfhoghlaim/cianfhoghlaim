using KoalaWiki.Core.Extensions;
using KoalaWiki.Extensions;
using Newtonsoft.Json;

namespace KoalaWiki.Options;

public class OpenAIOptions
{
    /// <summary>
    /// ChatGPT模型
    /// </summary>
    public static string ChatModel { get; set; } = string.Empty;

    /// <summary>
    /// 分析模型
    /// </summary>
    public static string AnalysisModel { get; set; } = string.Empty;

    /// <summary>
    /// ChatGPT API密钥
    /// </summary>
    public static string ChatApiKey { get; set; } = string.Empty;

    /// <summary>
    /// API地址
    /// </summary>
    public static string Endpoint { get; set; } = string.Empty;

    /// <summary>
    /// 模型提供商
    /// </summary>
    public static string ModelProvider { get; set; } = string.Empty;

    /// <summary>
    /// 最大文件限制
    /// </summary>
    public static int MaxFileLimit { get; set; } = 10;

    /// <summary>
    /// 深度研究模型
    /// </summary>
    public static string DeepResearchModel { get; set; } = string.Empty;

    /// <summary>
    /// 启用Mem0
    /// </summary>
    public static bool EnableMem0 { get; set; } = false;

    public static string Mem0ApiKey { get; set; } = string.Empty;

    public static string Mem0Endpoint { get; set; } = string.Empty;

    public static void InitConfig(IConfiguration configuration)
    {
        ChatModel = (configuration.GetValue<string>("CHAT_MODEL") ??
                     configuration.GetValue<string>("ChatModel") ?? string.Empty).GetTrimmedValueOrEmpty();
        AnalysisModel = (configuration.GetValue<string>("ANALYSIS_MODEL") ??
                         configuration.GetValue<string>("AnalysisModel") ?? string.Empty).GetTrimmedValueOrEmpty();
        ChatApiKey = (configuration.GetValue<string>("CHAT_API_KEY") ??
                      configuration.GetValue<string>("ChatApiKey") ?? string.Empty).GetTrimmedValueOrEmpty();
        Endpoint = (configuration.GetValue<string>("ENDPOINT") ??
                    configuration.GetValue<string>("Endpoint") ?? string.Empty).GetTrimmedValueOrEmpty();
        ModelProvider = (configuration.GetValue<string>("MODEL_PROVIDER") ??
                         configuration.GetValue<string>("ModelProvider")).GetTrimmedValueOrEmpty();

        DeepResearchModel = (configuration.GetValue<string>("DEEP_RESEARCH_MODEL") ??
                             configuration.GetValue<string>("DeepResearchModel")).GetTrimmedValueOrEmpty();

        MaxFileLimit = configuration.GetValue<int>("MAX_FILE_LIMIT") > 0
            ? configuration.GetValue<int>("MAX_FILE_LIMIT")
            : 10;

        EnableMem0 = configuration.GetValue<bool?>("ENABLE_MEM0") ?? false;

        if (EnableMem0)
        {
            Mem0ApiKey = (configuration.GetValue<string>("MEM0_API_KEY") ??
                          configuration.GetValue<string>("Mem0ApiKey") ?? string.Empty).GetTrimmedValueOrEmpty();

            Mem0Endpoint = (configuration.GetValue<string>("MEM0_ENDPOINT") ??
                            configuration.GetValue<string>("Mem0Endpoint") ?? string.Empty).GetTrimmedValueOrEmpty();

            if (string.IsNullOrEmpty(Mem0Endpoint))
            {
                throw new Exception("Mem0Endpoint is empty or not set");
            }
        }

        if (string.IsNullOrEmpty(ModelProvider))
        {
            ModelProvider = "OpenAI";
        }

        // 检查参数
        if (string.IsNullOrEmpty(ChatModel))
        {
            throw new Exception("ChatModel is empty");
        }

        if (string.IsNullOrEmpty(ChatApiKey))
        {
            throw new Exception("ChatApiKey is empty");
        }

        if (string.IsNullOrEmpty(Endpoint))
        {
            throw new Exception("Endpoint is empty");
        }

        if (string.IsNullOrEmpty(DeepResearchModel))
        {
            DeepResearchModel = ChatModel;
        }

        // 如果没设置分析模型则使用默认的
        if (string.IsNullOrEmpty(AnalysisModel))
        {
            AnalysisModel = ChatModel;
        }
    }
}