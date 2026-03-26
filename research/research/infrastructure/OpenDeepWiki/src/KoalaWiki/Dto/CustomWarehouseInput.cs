namespace KoalaWiki.Dto;

public class CustomWarehouseInput
{
    /// <summary>
    /// 组织名称
    /// </summary>
    public string Organization { get; set; }

    /// <summary>
    /// 项目名称
    /// </summary>
    /// <returns></returns>
    public string RepositoryName { get; set; }

    /// <summary>
    /// 仓库地址
    /// </summary>
    /// <returns></returns>
    public string Address { get; set; }

    /// <summary>
    /// 分支
    /// </summary>
    /// <returns></returns>
    public string Branch { get; set; }

    /// <summary>
    /// 私有化git账号
    /// </summary>
    public string? GitUserName { get; set; }

    /// <summary>
    /// 私有化git密码
    /// </summary>
    public string? GitPassword { get; set; }

    /// <summary>
    ///  私有化git邮箱
    /// </summary>
    public string? Email { get; set; }
}