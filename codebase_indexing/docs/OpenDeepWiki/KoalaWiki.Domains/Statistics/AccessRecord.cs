namespace KoalaWiki.Domains.Statistics;

/// <summary>
/// 访问记录实体
/// </summary>
public class AccessRecord : Entity<string>
{

    /// <summary>
    /// 访问的资源类型（Repository、Document、User等）
    /// </summary>
    public string ResourceType { get; set; } = string.Empty;

    /// <summary>
    /// 访问的资源ID
    /// </summary>
    public string ResourceId { get; set; } = string.Empty;

    /// <summary>
    /// 访问用户ID（可选，匿名访问时为空）
    /// </summary>
    public string? UserId { get; set; }

    /// <summary>
    /// 访问者IP地址
    /// </summary>
    public string IpAddress { get; set; } = string.Empty;

    /// <summary>
    /// 用户代理信息
    /// </summary>
    public string UserAgent { get; set; } = string.Empty;

    /// <summary>
    /// 访问路径
    /// </summary>
    public string Path { get; set; } = string.Empty;

    /// <summary>
    /// 访问方法（GET、POST等）
    /// </summary>
    public string Method { get; set; } = string.Empty;

    /// <summary>
    /// 响应状态码
    /// </summary>
    public int StatusCode { get; set; }

    /// <summary>
    /// 响应时间（毫秒）
    /// </summary>
    public long ResponseTime { get; set; }
} 