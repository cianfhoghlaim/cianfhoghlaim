using System.Text.RegularExpressions;
using KoalaWiki.Domains.Warehouse;
using LibGit2Sharp;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;

namespace KoalaWiki.BackendService;

public partial class WarehouseProcessingTask
{
    /// <summary>
    /// 生成更新日志
    /// </summary>
    public async Task<List<CommitResultDto>> GenerateUpdateLogAsync(string gitPath,
        Warehouse warehouse,
        string readme, string gitRepositoryUrl, string branch, IKoalaWikiContext koalaWikiContext)
    {
        // 获取仓库上次最近更新时间
        var records = await koalaWikiContext.DocumentCommitRecords
            .Where(x => x.WarehouseId == warehouse.Id)
            // 获取最近的记录LastUpdate
            .OrderByDescending(x => x.LastUpdate).FirstOrDefaultAsync();

        // 读取git log
        using var repo = new Repository(gitPath, new RepositoryOptions());

        // 大于records的提交时间内容
        var log = repo.Commits
            .Where(x => records == null || x.Committer.When > records?.LastUpdate)
            .OrderByDescending(x => x.Committer.When)
            .ThenBy(x => x.Committer.When)
            .ToList();

        var kernel = await KernelFactory.GetKernel(OpenAIOptions.Endpoint, OpenAIOptions.ChatApiKey, gitPath,
            OpenAIOptions.ChatModel);

        string commitMessage = string.Empty;
        foreach (var commit in log)
        {
            commitMessage += "提交人：" + commit.Committer.Name + "\n提交内容\n<message>\n" + commit.Message +
                             "<message>";

            commitMessage += "\n提交时间：" + commit.Committer.When.ToString("yyyy-MM-dd HH:mm:ss") + "\n";
        }

        var plugin = kernel.Plugins["CodeAnalysis"]["CommitAnalyze"];

        var str = string.Empty;
        await foreach (var item in kernel.InvokeStreamingAsync(plugin, new KernelArguments()
                       {
                           ["readme"] = readme,
                           ["git_repository"] = gitRepositoryUrl,
                           ["commit_message"] = commitMessage,
                           ["git_branch"] = branch
                       }))
        {
            str += item;
        }

        var regex = new Regex(@"<changelog>(.*?)</changelog>",
            RegexOptions.Singleline);

        var match = regex.Match(str);

        if (match.Success)
        {
            // 提取到的内容
            str = match.Groups[1].Value;
        }

        var result = JsonConvert.DeserializeObject<List<CommitResultDto>>(str);

        return result;
    }

    public class CommitResultDto
    {
        public DateTime date { get; set; }

        public string title { get; set; }

        public string description { get; set; }
    }
}