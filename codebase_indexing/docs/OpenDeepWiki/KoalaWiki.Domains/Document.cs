using System;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Entities;

namespace KoalaWiki.Domains;

public class Document : Entity<string>
{
    /// <summary>
    /// 关联id
    /// </summary>
    public string WarehouseId { get; set; } = string.Empty;
    
    /// <summary>
    /// 最后更新时间
    /// </summary>
    public DateTime LastUpdate { get; set; } = DateTime.UtcNow;
    
    /// <summary>
    /// 文档介绍
    /// </summary>
    public string Description { get; set; } = string.Empty;
    
    /// <summary>
    /// 浏览量
    /// </summary>
    public long LikeCount { get; set; } = 0;
    
    /// <summary>
    /// 评论量
    /// </summary>
    public long CommentCount { get; set; } = 0;
    
    /// <summary>
    /// 本地git仓库地址
    /// </summary>
    /// <returns></returns>
    public string GitPath { get; set; } = string.Empty;
    
    /// <summary>
    /// 仓库状态
    /// </summary>
    public WarehouseStatus Status { get; set; }
}