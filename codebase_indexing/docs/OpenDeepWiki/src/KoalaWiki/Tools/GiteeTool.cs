using System.ComponentModel;
using System.Text;
using System.Text.Json;

namespace KoalaWiki.Tools;

[Description("Gitee相关功能")]
public class GiteeTool(
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
    [KernelFunction("search_issues")]
    [Description("搜索 Issue 内容")]
    public async Task<string> SearchIssuesAsync(
        [Description("搜索关键词")] string query,
        int maxResults = 5)
    {
        // Gitee 暂无官方 .NET SDK，需直接调用 Gitee Open API
        if (string.IsNullOrWhiteSpace(GiteeOptions.Token))
            return "未配置 Gitee Token，无法搜索 Issue。";


        using var httpClient = new HttpClient();
        var url =
            $"https://gitee.com/api/v5/repos/{owner}/{name}/issues?page=1&per_page={maxResults}&access_token={GiteeOptions.Token}&q={Uri.EscapeDataString(query)}";
        var response = await httpClient.GetAsync(url);
        if (!response.IsSuccessStatusCode)
            return $"Gitee API 请求失败: {response.StatusCode}";
        var json = await response.Content.ReadAsStringAsync();
        var issues = JsonSerializer.Deserialize<List<GiteeIssueListDto>>(json, JsonSerializerOptions.Web);
        if (issues == null || issues.Count == 0) return "未找到相关 Issue。";
        var sb = new StringBuilder();
        foreach (var issue in issues)
        {
            sb.AppendLine($"[{issue.title}]({issue.html_url}) # {issue.number} - {issue.state}");
        }

        if (DocumentContext.DocumentStore != null)
        {
            DocumentContext.DocumentStore.GitIssus.AddRange(issues.Select(x => new GitIssusItem()
            {
                Author = x.user.name,
                Title = x.title,
                Url = x.url,
                Content = x.body,
                CreatedAt = DateTime.TryParse(x.created_at, out var createdAt) ? createdAt : null,
                UrlHtml = x.html_url,
                State = x.state,
                Number = x.number
            }));
        }

        return sb.ToString();
    }

    /// <summary>
    /// 搜索指定的一个issue下评论内容
    /// </summary>
    /// <returns></returns>
    [Description("搜索指定编号 Issue 评论内容")]
    public async Task<string> SearchIssueCommentsAsync(
        [Description("Issue编号")] int issueNumber,
        int maxResults = 5)
    {
        // Gitee 暂无官方 .NET SDK，需直接调用 Gitee Open API
        if (string.IsNullOrWhiteSpace(GiteeOptions.Token))
            return "未配置 Gitee Token，无法搜索 Issue 评论。";

        var httpClient = new HttpClient();
        // 获取issue具体内容
        var issueUrl =
            $"https://gitee.com/api/v5/repos/{owner}/{name}/issues/{issueNumber}/comments?access_token={GiteeOptions.Token}&page=1&per_page=" +
            maxResults;

        var result = await httpClient.GetFromJsonAsync<GiteeIssusItem[]>(issueUrl);

        var sb = new StringBuilder();

        if (result != null && result.Length > 0)
        {
            sb.AppendLine($"Issue #{issueNumber} 评论：\n");
            foreach (var comment in result)
            {
                sb.AppendLine($"  创建时间: {comment.created_at}");
                sb.AppendLine($"- [{comment.user.name}]({comment.user.html_url}): {comment.body}");
            }
        }
        else
        {
            sb.AppendLine("未找到相关评论。");
        }

        return sb.ToString();
    }
}

public class GiteeIssusItem
{
    public int id { get; set; }
    public string body { get; set; }
    public User user { get; set; }
    public object source { get; set; }
    public Target target { get; set; }
    public string created_at { get; set; }
    public string updated_at { get; set; }
}

public class Target
{
    public Issue issue { get; set; }
    public object pull_request { get; set; }
}

public class Issue
{
    public int id { get; set; }
    public string title { get; set; }
    public string number { get; set; }
}

public class GiteeIssueListDto
{
    public int id { get; set; }
    public string url { get; set; }
    public string repository_url { get; set; }
    public string labels_url { get; set; }
    public string comments_url { get; set; }
    public string html_url { get; set; }
    public object parent_url { get; set; }
    public string number { get; set; }
    public int parent_id { get; set; }
    public int depth { get; set; }
    public string state { get; set; }
    public string title { get; set; }
    public string body { get; set; }
    public User user { get; set; }
    public Repository repository { get; set; }
    public object milestone { get; set; }
    public string created_at { get; set; }
    public string updated_at { get; set; }
    public object plan_started_at { get; set; }
    public object deadline { get; set; }
    public object finished_at { get; set; }
    public int scheduled_time { get; set; }
    public int comments { get; set; }
    public int priority { get; set; }
    public string issue_type { get; set; }
    public object program { get; set; }
    public bool security_hole { get; set; }
    public string issue_state { get; set; }
    public object branch { get; set; }
    public Issue_type_detail issue_type_detail { get; set; }
    public Issue_state_detail issue_state_detail { get; set; }
}

public class User
{
    public int id { get; set; }
    public string login { get; set; }
    public string name { get; set; }
    public string avatar_url { get; set; }
    public string url { get; set; }
    public string html_url { get; set; }
    public string remark { get; set; }
    public string followers_url { get; set; }
    public string following_url { get; set; }
    public string gists_url { get; set; }
    public string starred_url { get; set; }
    public string subscriptions_url { get; set; }
    public string organizations_url { get; set; }
    public string repos_url { get; set; }
    public string events_url { get; set; }
    public string received_events_url { get; set; }
    public string type { get; set; }
}

public class Repository
{
    public int id { get; set; }
    public string full_name { get; set; }
    public string human_name { get; set; }
    public string url { get; set; }

    public string path { get; set; }
    public string name { get; set; }

    public Owner owner { get; set; }
    public Assigner assigner { get; set; }
    public string description { get; set; }

    public bool fork { get; set; }
    public string html_url { get; set; }
    public string ssh_url { get; set; }
    public string forks_url { get; set; }
    public string keys_url { get; set; }
    public string collaborators_url { get; set; }
    public string hooks_url { get; set; }
    public string branches_url { get; set; }
    public string tags_url { get; set; }
    public string blobs_url { get; set; }
    public string stargazers_url { get; set; }
    public string contributors_url { get; set; }
    public string commits_url { get; set; }
    public string comments_url { get; set; }
    public string issue_comment_url { get; set; }
    public string issues_url { get; set; }
    public string pulls_url { get; set; }
    public string milestones_url { get; set; }
    public string notifications_url { get; set; }
    public string labels_url { get; set; }
    public string releases_url { get; set; }
    public bool recommend { get; set; }
    public bool gvp { get; set; }
    public object homepage { get; set; }
    public object language { get; set; }
    public int forks_count { get; set; }
    public int stargazers_count { get; set; }
    public int watchers_count { get; set; }
    public string default_branch { get; set; }
    public int open_issues_count { get; set; }
    public bool has_issues { get; set; }
    public bool has_wiki { get; set; }
    public bool issue_comment { get; set; }
    public bool can_comment { get; set; }
    public bool pull_requests_enabled { get; set; }
    public bool has_page { get; set; }
    public object license { get; set; }
    public bool outsourced { get; set; }
    public string project_creator { get; set; }
    public string[] members { get; set; }
    public string pushed_at { get; set; }
    public string created_at { get; set; }
    public string updated_at { get; set; }
    public object parent { get; set; }
    public object paas { get; set; }
    public int assignees_number { get; set; }
    public int testers_number { get; set; }
    public Assignee[] assignee { get; set; }
    public Testers[] testers { get; set; }
    public string status { get; set; }
    public object[] programs { get; set; }
    public object enterprise { get; set; }
    public object[] project_labels { get; set; }
    public string issue_template_source { get; set; }
}

public class Namespace
{
    public int id { get; set; }
    public string type { get; set; }
    public string name { get; set; }
    public string path { get; set; }
    public string html_url { get; set; }
}

public class Owner
{
    public int id { get; set; }
    public string login { get; set; }
    public string name { get; set; }
    public string avatar_url { get; set; }
    public string url { get; set; }
    public string html_url { get; set; }
    public string remark { get; set; }
    public string followers_url { get; set; }
    public string following_url { get; set; }
    public string gists_url { get; set; }
    public string starred_url { get; set; }
    public string subscriptions_url { get; set; }
    public string organizations_url { get; set; }
    public string repos_url { get; set; }
    public string events_url { get; set; }
    public string received_events_url { get; set; }
    public string type { get; set; }
}

public class Assigner
{
    public int id { get; set; }
    public string login { get; set; }
    public string name { get; set; }
    public string avatar_url { get; set; }
    public string url { get; set; }
    public string html_url { get; set; }
    public string remark { get; set; }
    public string followers_url { get; set; }
    public string following_url { get; set; }
    public string gists_url { get; set; }
    public string starred_url { get; set; }
    public string subscriptions_url { get; set; }
    public string organizations_url { get; set; }
    public string repos_url { get; set; }
    public string events_url { get; set; }
    public string received_events_url { get; set; }
    public string type { get; set; }
}

public class Assignee
{
    public int id { get; set; }
    public string login { get; set; }
    public string name { get; set; }
    public string avatar_url { get; set; }
    public string url { get; set; }
    public string html_url { get; set; }
    public string remark { get; set; }
    public string followers_url { get; set; }
    public string following_url { get; set; }
    public string gists_url { get; set; }
    public string starred_url { get; set; }
    public string subscriptions_url { get; set; }
    public string organizations_url { get; set; }
    public string repos_url { get; set; }
    public string events_url { get; set; }
    public string received_events_url { get; set; }
    public string type { get; set; }
}

public class Testers
{
    public int id { get; set; }
    public string login { get; set; }
    public string name { get; set; }
    public string avatar_url { get; set; }
    public string url { get; set; }
    public string html_url { get; set; }
    public string remark { get; set; }
    public string followers_url { get; set; }
    public string following_url { get; set; }
    public string gists_url { get; set; }
    public string starred_url { get; set; }
    public string subscriptions_url { get; set; }
    public string organizations_url { get; set; }
    public string repos_url { get; set; }
    public string events_url { get; set; }
    public string received_events_url { get; set; }
    public string type { get; set; }
}

public class Issue_type_detail
{
    public int id { get; set; }
    public string title { get; set; }
    public object template { get; set; }
    public string ident { get; set; }
    public string color { get; set; }
    public bool is_system { get; set; }
    public string created_at { get; set; }
    public string updated_at { get; set; }
}

public class Issue_state_detail
{
    public int id { get; set; }
    public string title { get; set; }
    public string color { get; set; }
    public string icon { get; set; }
    public object command { get; set; }
    public int serial { get; set; }
    public string created_at { get; set; }
    public string updated_at { get; set; }
}