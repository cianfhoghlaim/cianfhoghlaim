using System.ClientModel.Primitives;
using System.Text;
using System.Text.RegularExpressions;
using KoalaWiki.Agents;
using KoalaWiki.Domains;
using KoalaWiki.Dto;
using KoalaWiki.Prompts;
using Microsoft.SemanticKernel.Connectors.OpenAI;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace KoalaWiki.KoalaWarehouse;

public class WarehouseClassify
{
    /// <summary>
    /// 根据仓库信息分析得出仓库分类
    /// </summary>
    public static async Task<ClassifyType?> ClassifyAsync(string catalog, string readme)
    {
        var prompt = await PromptContext.Warehouse(nameof(PromptConstant.Warehouse.RepositoryClassification),
            new KernelArguments(new OpenAIPromptExecutionSettings()
            {
                Temperature = 0.1,
                MaxTokens = DocumentsHelper.GetMaxTokens(OpenAIOptions.ChatModel)
            })
            {
                ["category"] = catalog,
                ["readme"] = readme
            }, OpenAIOptions.ChatModel);

        var result = new StringBuilder();

        var agent = AgentFactory.CreateChatClientAgentAsync(OpenAIOptions.ChatModel, (options =>
        {
            options.Name = "WarehouseClassifyAgent";
        }));

        await foreach (var i in agent.RunStreamingAsync(prompt))
        {
            if (!string.IsNullOrEmpty(i.Text))
            {
                result.Append(i.Text);
            }
        }

        // 提取分类结果正则表达式<classify>(.*?)</classify>
        var regex = new Regex(@"<classify>(.*?)</classify>", RegexOptions.Singleline);

        var match = regex.Match(result.ToString());
        if (match.Success)
        {
            // 提取到的内容
            var extractedContent = match.Groups[1].Value.Replace("classifyName:", "").Trim();

            // 将提取的内容转换为枚举类型
            if (Enum.TryParse<ClassifyType>(extractedContent, true, out var classifyType))
            {
                return classifyType;
            }
            else
            {
                return null;
            }
        }

        else
        {
            return null;
        }
    }
}