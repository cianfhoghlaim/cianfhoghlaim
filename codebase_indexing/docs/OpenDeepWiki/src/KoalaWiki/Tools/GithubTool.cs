using System.ComponentModel;
using System.Text;
using Octokit;

namespace KoalaWiki.Tools;

public class GithubTool(
    string owner,
    string name,
    string branch
)
{
    /// <summary>
    /// 搜索相关issue内容
    /// </summary>
    /// <param name="query">搜索关键词</param>
    /// <param name="maxResults">最大返回数量</param>
    /// <returns>搜索结果字符串</returns>
    [Description("搜索相关 Issue 内容")]
    [KernelFunction("search_issues")]
    public async Task<string> SearchIssuesAsync(
        [Description("搜索关键词")] string query,
        int maxResults = 5)
    {
        // 使用 Octokit 进行 GitHub Issue 搜索
        var client = new GitHubClient(new ProductHeaderValue("KoalaWiki"));
        if (!string.IsNullOrEmpty(GithubOptions.Token))
        {
            var tokenAuth = new Credentials(GithubOptions.Token); // Password 作为 token
            client.Credentials = tokenAuth;
        }

        var request = new SearchIssuesRequest(query)
        {
            Repos = new RepositoryCollection()
            {
                { owner, name }
            },
            Type = IssueTypeQualifier.Issue
        };

        var result = await client.Search.SearchIssues(request);
        var issues = result.Items.Take(maxResults).ToList();
        if (!issues.Any()) return "未找到相关 Issue。";
        var sb = new System.Text.StringBuilder();
        foreach (var issue in issues)
        {
            sb.AppendLine($"[{issue.Title}]({issue.HtmlUrl}) # {issue.Number} - {issue.State.Value.ToString()}");
        }

        if (DocumentContext.DocumentStore != null)
        {
            DocumentContext.DocumentStore.GitIssus.AddRange(issues.Select(x => new GitIssusItem()
            {
                Author = x.User.Name,
                Title = x.Title,
                Url = x.Url,
                Content = x.Body,
                CreatedAt = x.CreatedAt.Date,
                UrlHtml = x.HtmlUrl,
                State = x.State.StringValue,
                Number = x.Number.ToString()
            }));
        }

        return sb.ToString();
    }

    /// <summary>
    /// 搜索指定的一个issue下评论内容
    /// </summary>
    /// <param name="issueNumber">Issue编号</param>
    /// <param name="maxResults">最大返回数量</param>
    /// <returns>搜索结果字符串</returns>
    [Description("搜索指定编号 Issue 评论内容")]
    [KernelFunction("search_issue_comments")]
    public async Task<string> SearchIssueCommentsAsync(
        [Description("Issue编号")] int issueNumber,
        int maxResults = 5)
    {
        // 使用 Octokit 进行 GitHub Issue 评论搜索
        var client = new GitHubClient(new ProductHeaderValue("KoalaWiki"));
        if (!string.IsNullOrEmpty(GithubOptions.Token))
        {
            var tokenAuth = new Credentials(GithubOptions.Token);
            client.Credentials = tokenAuth;
        }

        try
        {
            // 获取issue的评论
            var comments = await client.Issue.Comment.GetAllForIssue(owner, name, issueNumber);
            var issueComments = comments.Take(maxResults).ToList();

            var sb = new StringBuilder();

            if (issueComments.Any())
            {
                sb.AppendLine($"Issue #{issueNumber} 评论：\n");
                foreach (var comment in issueComments)
                {
                    sb.AppendLine($"  创建时间: {comment.CreatedAt}");
                    sb.AppendLine($"- [{comment.User.Login}]({comment.User.HtmlUrl}): {comment.Body}");
                }
            }
            else
            {
                sb.AppendLine("未找到相关评论。");
            }

            return sb.ToString();
        }
        catch (Exception ex)
        {
            return $"获取 Issue 评论失败: {ex.Message}";
        }
    }
}