using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace KoalaWiki.Options;

/// <summary>
/// JWT配置选项
/// </summary>
public class JwtOptions
{
    /// <summary>
    /// 配置名称
    /// </summary>
    public const string Name = "Jwt";
    
    /// <summary>
    /// 密钥
    /// </summary>
    public string Secret { get; set; } = string.Empty;
    
    /// <summary>
    /// 颁发者
    /// </summary>
    public string Issuer { get; set; } = string.Empty;
    
    /// <summary>
    /// 接收者
    /// </summary>
    public string Audience { get; set; } = string.Empty;
    
    /// <summary>
    /// 过期时间（分钟）
    /// </summary>
    public int ExpireMinutes { get; set; } = 60 * 24; // 默认1天
    
    /// <summary>
    /// 刷新令牌过期时间（分钟）
    /// </summary>
    public int RefreshExpireMinutes { get; set; } = 60 * 24 * 7; // 默认7天
    
    /// <summary>
    /// 获取签名凭证
    /// </summary>
    public SymmetricSecurityKey GetSymmetricSecurityKey()
    {
        return new SymmetricSecurityKey(Encoding.UTF8.GetBytes(Secret));
    }
    
    /// <summary>
    /// 初始化配置
    /// </summary>
    public static JwtOptions InitConfig(IConfiguration configuration)
    {
        var options = configuration.GetSection(Name).Get<JwtOptions>() ?? new JwtOptions();
        
        // 如果配置中没有设置密钥，则生成一个随机密钥
        if (string.IsNullOrEmpty(options.Secret))
        {
            options.Secret = Guid.NewGuid().ToString("N") + Guid.NewGuid().ToString("N");
        }
        
        // 如果没有设置颁发者和接收者，则使用默认值
        if (string.IsNullOrEmpty(options.Issuer))
        {
            options.Issuer = "KoalaWiki";
        }
        
        if (string.IsNullOrEmpty(options.Audience))
        {
            options.Audience = "KoalaWiki";
        }
        
        return options;
    }
} 