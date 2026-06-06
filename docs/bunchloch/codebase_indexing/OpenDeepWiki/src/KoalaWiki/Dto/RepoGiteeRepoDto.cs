using System.Text.Json.Serialization;

namespace KoalaWiki.Dto;

public class RepoGiteeRepoDto
{
    [JsonPropertyName("id")] public long Id { get; set; }

    [JsonPropertyName("full_name")] public string FullName { get; set; }

    [JsonPropertyName("human_name")] public string human_name { get; set; }

    [JsonPropertyName("url")] public string url { get; set; }

    [JsonPropertyName("namespace")] public RepoGiteeRepoNamespace Namespace { get; set; }
    public string path { get; set; }
    public string name { get; set; }
    public RepoGiteeRepoOwner owner { get; set; }
    public RepoGiteeRepoAssigner assigner { get; set; }
    public string? description { get; set; }

    [JsonPropertyName("private")] public bool Private { get; set; }

    [JsonPropertyName("public")] public bool Public { get; set; }

    [JsonPropertyName("internal")] public bool Internal { get; set; }

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
    public string homepage { get; set; }
    public string? language { get; set; }
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
    public string license { get; set; }
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
    public RepoGiteeRepoAssignee[] assignee { get; set; }
    public RepoGiteeRepoTesters[] testers { get; set; }
    public string status { get; set; }
    public object[] programs { get; set; }
    public object enterprise { get; set; }
    public object[] project_labels { get; set; }
    public string issue_template_source { get; set; }
}

public class RepoGiteeRepoNamespace
{
    public int id { get; set; }
    public string type { get; set; }
    public string name { get; set; }
    public string path { get; set; }
    public string html_url { get; set; }
}

public class RepoGiteeRepoOwner
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

public class RepoGiteeRepoAssigner
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

public class RepoGiteeRepoAssignee
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

public class RepoGiteeRepoTesters
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