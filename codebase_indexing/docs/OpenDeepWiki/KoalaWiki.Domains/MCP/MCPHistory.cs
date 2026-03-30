namespace KoalaWiki.Domains.MCP;

public class MCPHistory : Entity<string>
{
    /// <summary>
    /// 提问内容
    /// </summary>
    public string Question { get; set; } = null!;

    /// <summary>
    /// AI回复
    /// </summary>
    public string Answer { get; set; } = null!;

    /// <summary>
    /// 用户id
    /// </summary>
    public string? UserId { get; set; }

    /// <summary>
    /// 仓库id
    /// </summary>
    public string? WarehouseId { get; set; }

    /// <summary>
    /// 耗时
    /// </summary>
    /// <returns></returns>
    public int CostTime { get; set; }

    /// <summary>
    /// 请求id
    /// </summary>
    public string Ip { get; set; }

    /// <summary>
    /// 来源客户端
    /// </summary>
    public string UserAgent { get; set; } = null!;
}