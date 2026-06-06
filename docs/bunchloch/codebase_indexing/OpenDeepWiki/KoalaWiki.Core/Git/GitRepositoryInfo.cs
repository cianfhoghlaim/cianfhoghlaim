namespace KoalaWiki.Git;

public record GitRepositoryInfo(
    string LocalPath,
    string RepositoryName,
    string Organization,
    string BranchName,
    string CommitTime,
    string CommitAuthor,
    string CommitMessage,
    string Version);