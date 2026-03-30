using System.ComponentModel;
using KoalaWiki.Core;
using KoalaWiki.Options;
using LibGit2Sharp;

namespace KoalaWiki.Git;

public class GitService
{
    public static (string localPath, string organization) GetRepositoryPath(string repositoryUrl)
    {
        var uri = new Uri(repositoryUrl);
        var segments = uri.Segments;

        if (segments.Length < 2)
        {
            throw new ArgumentException("仓库URL格式不正确，至少需要包含组织名和仓库名");
        }

        string organization;
        string repositoryName;


        // 对于 GitLab，最后一个段是仓库名，前面的都是组织/子组织  
        repositoryName = segments[^1].Trim('/').Replace(".git", "");

        // 组织名包含所有中间路径，用下划线连接以避免路径冲突  
        var orgParts = new List<string>();
        for (int i = 1; i < segments.Length - 1; i++)
        {
            orgParts.Add(segments[i].Trim('/'));
        }

        organization = string.Join("/", orgParts);


        // 拼接本地路径  
        var repositoryPath = Path.Combine(Constant.GitPath, organization, repositoryName);
        return (repositoryPath, organization);
    }

    public static (List<Commit> commits, string Sha) PullRepository(
        [Description("仓库地址")] string repositoryUrl,
        string commitId,
        string branch,
        string userName = "",
        string password = "")
    {
        var fetchOptions = new FetchOptions()
        {
            CertificateCheck = (_, _, _) => true,
            CredentialsProvider = (_url, _user, _cred) =>
                new UsernamePasswordCredentials
                {
                    Username = userName,
                    Password = password
                }
        };

        // 设置代理
        if (!string.IsNullOrEmpty(DocumentOptions.Proxy))
        {
            fetchOptions.ProxyOptions.Url = DocumentOptions.Proxy;
        }

        var pullOptions = new PullOptions
        {
            FetchOptions = fetchOptions
        };

        // 先克隆
        if (!Directory.Exists(repositoryUrl))
        {
            // 克隆
            CloneRepository(repositoryUrl, userName, password, branch);
        }

        if (!Directory.Exists(repositoryUrl))
        {
            throw new Exception("克隆失败");
        }

        // pull仓库
        using var repo = new Repository(repositoryUrl);

        var result = Commands.Pull(repo, new Signature("KoalaWiki", "239573049@qq.com", DateTimeOffset.Now),
            pullOptions);

        // commitId是上次提交id，根据commitId获取到到现在的所有提交记录
        if (!string.IsNullOrEmpty(commitId))
        {
            var commit = repo.Lookup<Commit>(commitId);
            if (commit != null)
            {
                // 获取从指定commitId到HEAD的所有提交记录
                var filter = new CommitFilter
                {
                    IncludeReachableFrom = repo.Head.Tip,
                    ExcludeReachableFrom = commit,
                    SortBy = CommitSortStrategies.Time
                };
                var commits = repo.Commits.QueryBy(filter).ToList();
                return (commits, repo.Head.Tip.Sha);
            }
        }

        return (repo.Commits.ToList(), repo.Head.Tip.Sha);
    }

    /// <summary>
    /// 拉取指定仓库
    /// </summary>
    /// <returns></returns>
    public static GitRepositoryInfo CloneRepository(
        [Description("仓库地址")] string repositoryUrl,
        string userName = "",
        string password = "",
        [Description("分支")] string branch = "master")
    {
        var (localPath, organization) = GetRepositoryPath(repositoryUrl);

        var fetchOptions = new FetchOptions
        {
            CertificateCheck = (_, _, _) => true,
            Depth = 0,
        };

        // 设置代理
        if (!string.IsNullOrEmpty(DocumentOptions.Proxy))
        {
            fetchOptions.ProxyOptions.Url = DocumentOptions.Proxy;
        }

        var cloneOptions = new CloneOptions(fetchOptions)
        {
            BranchName = branch
        };

        var names = repositoryUrl.Split('/');

        var repositoryName = names[^1].Replace(".git", "");

        localPath = Path.Combine(localPath, branch);

        // 判断仓库是否已经存在
        if (Directory.Exists(localPath))
        {
            try
            {
                // 获取当前仓库的git分支
                using var repo = new Repository(localPath);

                var branchName = repo.Head.FriendlyName;
                // 获取当前仓库的git版本
                var version = repo.Head.Tip.Sha;
                // 获取当前仓库的git提交时间
                var commitTime = repo.Head.Tip.Committer.When;
                // 获取当前仓库的git提交人
                var commitAuthor = repo.Head.Tip.Committer.Name;
                // 获取当前仓库的git提交信息
                var commitMessage = repo.Head.Tip.Message;

                return new GitRepositoryInfo(localPath, repositoryName, organization, branchName, commitTime.ToString(),
                    commitAuthor, commitMessage, version);
            }
            catch (Exception e)
            {
                // 删除目录以后在尝试一次
                Directory.Delete(localPath, true);

                var retryFetchOptions = new FetchOptions
                {
                    Depth = 0,
                    CertificateCheck = (_, _, _) => true,
                    CredentialsProvider = (_url, _user, _cred) =>
                    {
                        return new UsernamePasswordCredentials
                        {
                            Username = userName, // 对于Token认证，Username可以随便填
                            Password = password
                        };
                    }
                };

                // 设置代理
                if (!string.IsNullOrEmpty(DocumentOptions.Proxy))
                {
                    retryFetchOptions.ProxyOptions.Url = DocumentOptions.Proxy;
                }

                cloneOptions = new CloneOptions(retryFetchOptions)
                {
                    BranchName = branch,
                };

                Repository.Clone(repositoryUrl, localPath, cloneOptions);
                // 获取当前仓库的git分支
                using var repo = new Repository(localPath);

                var branchName = repo.Head.FriendlyName;
                // 获取当前仓库的git版本
                var version = repo.Head.Tip.Sha;
                // 获取当前仓库的git提交时间
                var commitTime = repo.Head.Tip.Committer.When;
                // 获取当前仓库的git提交人
                var commitAuthor = repo.Head.Tip.Committer.Name;
                // 获取当前仓库的git提交信息
                var commitMessage = repo.Head.Tip.Message;

                return new GitRepositoryInfo(localPath, repositoryName, organization, branchName, commitTime.ToString(),
                    commitAuthor, commitMessage, version);
            }
        }
        else
        {
            if (string.IsNullOrEmpty(userName))
            {
                var str = Repository.Clone(repositoryUrl, localPath, cloneOptions);
            }
            else
            {
                var info = Directory.CreateDirectory(localPath);

                var authFetchOptions = new FetchOptions
                {
                    Depth = 0,
                    CertificateCheck = (_, _, _) => true,
                    CredentialsProvider = (_url, _user, _cred) =>
                    {
                        return new UsernamePasswordCredentials
                        {
                            Username = userName, // 对于Token认证，Username可以随便填
                            Password = password
                        };
                    }
                };

                // 设置代理
                if (!string.IsNullOrEmpty(DocumentOptions.Proxy))
                {
                    authFetchOptions.ProxyOptions.Url = DocumentOptions.Proxy;
                }

                cloneOptions = new CloneOptions(authFetchOptions)
                {
                    BranchName = branch,
                };

                Repository.Clone(repositoryUrl, localPath, cloneOptions);
            }

            // 获取当前仓库的git分支
            using var repo = new Repository(localPath);
            var branchName = repo.Head.FriendlyName;
            // 获取当前仓库的git版本
            var version = repo.Head.Tip.Sha;
            // 获取当前仓库的git提交时间
            var commitTime = repo.Head.Tip.Committer.When;
            // 获取当前仓库的git提交人
            var commitAuthor = repo.Head.Tip.Committer.Name;
            // 获取当前仓库的git提交信息
            var commitMessage = repo.Head.Tip.Message;

            return new GitRepositoryInfo(localPath, repositoryName, organization, branchName, commitTime.ToString(),
                commitAuthor, commitMessage, version);
        }
    }
}