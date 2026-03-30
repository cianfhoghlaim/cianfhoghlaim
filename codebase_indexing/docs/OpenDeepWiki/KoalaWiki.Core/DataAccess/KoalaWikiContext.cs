using System.Text.Json;
using KoalaWiki.Domains;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Domains.FineTuning;
using KoalaWiki.Domains.MCP;
using KoalaWiki.Domains.Statistics;
using KoalaWiki.Domains.Users;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Entities;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Core.DataAccess;

public class KoalaWikiContext<TContext>(DbContextOptions<TContext> options)
    : DbContext(options), IKoalaWikiContext where TContext : DbContext
{
    public DbSet<Warehouse> Warehouses { get; set; }

    public DbSet<DocumentCatalog> DocumentCatalogs { get; set; }

    public DbSet<Document> Documents { get; set; }

    public DbSet<DocumentFileItem> DocumentFileItems { get; set; }

    public DbSet<DocumentFileItemSource> DocumentFileItemSources { get; set; }
    
    public DbSet<DocumentCatalogI18n> DocumentCatalogI18ns { get; set; }
    
    public DbSet<DocumentFileItemI18n> DocumentFileItemI18ns { get; set; }

    public DbSet<TranslationTask> TranslationTasks { get; set; }

    public DbSet<DocumentOverview> DocumentOverviews { get; set; }

    public DbSet<DocumentCommitRecord> DocumentCommitRecords { get; set; }

    public DbSet<TrainingDataset> TrainingDatasets { get; set; }

    public DbSet<FineTuningTask> FineTuningTasks { get; set; }

    public DbSet<User> Users { get; set; }

    public DbSet<MCPHistory> MCPHistories { get; set; }

    public DbSet<UserInAuth> UserInAuths { get; set; }

    public DbSet<UserInRole> UserInRoles { get; set; }

    public DbSet<Role> Roles { get; set; }

    public DbSet<WarehouseInRole> WarehouseInRoles { get; set; }

    public DbSet<WarehouseSyncRecord> WarehouseSyncRecords { get; set; }

    public DbSet<AccessRecord> AccessRecords { get; set; }

    public DbSet<DailyStatistics> DailyStatistics { get; set; }

    public DbSet<AppConfig> AppConfigs { get; set; }

    public DbSet<SystemSetting> SystemSettings { get; set; }

    public DbSet<MiniMap> MiniMaps { get; set; }

    public async Task<int> SaveChangesAsync(CancellationToken cancellationToken = new CancellationToken())
    {
        BeforeSaveChanges();
        return await base.SaveChangesAsync(cancellationToken);
    }

    public override int SaveChanges()
    {
        BeforeSaveChanges();
        return base.SaveChanges();
    }

    private void BeforeSaveChanges()
    {
        foreach (var entry in ChangeTracker.Entries())
        {
            if (entry is { State: EntityState.Added, Entity: ICreateEntity creationAudited })
            {
                creationAudited.CreatedAt = DateTime.UtcNow;
            }
        }
    }

    public async Task RunMigrateAsync()
    {
        await Database.MigrateAsync();
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<Warehouse>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.Name).IsRequired().HasComment("仓库名称");
            builder.Property(x => x.Description).IsRequired().HasComment("仓库描述");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.Status).HasComment("仓库状态");
            builder.Property(x => x.Address).HasComment("仓库地址");
            builder.Property(x => x.Type).HasComment("仓库类型");
            builder.Property(x => x.Branch).HasComment("分支");
            builder.Property(x => x.OrganizationName).HasComment("组织名称");
            builder.HasIndex(x => x.Name);
            builder.HasIndex(x => x.Status);
            builder.HasIndex(x => x.CreatedAt);
            builder.HasIndex(x => x.Address);
            builder.HasIndex(x => x.Type);
            builder.HasIndex(x => x.Branch);
            builder.HasIndex(x => x.OrganizationName);
            builder.HasComment("知识仓库表");
        }));

        modelBuilder.Entity<DocumentCatalog>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.Name).IsRequired().HasComment("目录名称");
            builder.Property(x => x.Description).IsRequired().HasComment("目录描述");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.ParentId).HasComment("父级目录Id");
            builder.Property(x => x.WarehouseId).HasComment("所属仓库Id");
            builder.Property(x => x.DucumentId).HasComment("文档Id");
            builder.Property(x => x.IsDeleted).HasComment("是否已删除");
            builder.HasIndex(x => x.Name);
            builder.HasIndex(x => x.CreatedAt);
            builder.HasIndex(x => x.ParentId);
            builder.HasIndex(x => x.WarehouseId);
            builder.HasIndex(x => x.DucumentId);
            builder.HasIndex(x => x.IsDeleted);
            builder.HasComment("文档目录表");
        }));

        modelBuilder.Entity<Document>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.Description).IsRequired().HasComment("文档描述");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.WarehouseId).HasComment("所属仓库Id");
            builder.HasIndex(x => x.CreatedAt);
            builder.HasIndex(x => x.WarehouseId);
            builder.HasComment("文档表");
        }));

        modelBuilder.Entity<DocumentFileItem>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.Title).IsRequired().HasComment("文件标题");
            builder.Property(x => x.Description).IsRequired().HasComment("文件描述");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.DocumentCatalogId).HasComment("目录Id");
            builder.Property(x => x.Metadata)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null),
                    v => JsonSerializer.Deserialize<Dictionary<string, string>>(v, (JsonSerializerOptions)null))
                .HasComment("元数据");
            builder.Property(x => x.Extra)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null),
                    v => JsonSerializer.Deserialize<Dictionary<string, string>>(v, (JsonSerializerOptions)null))
                .HasComment("扩展信息");
            builder.HasIndex(x => x.Title);
            builder.HasIndex(x => x.CreatedAt);
            builder.HasIndex(x => x.DocumentCatalogId);
            builder.HasComment("文档文件项表");
        }));

        modelBuilder.Entity<DocumentFileItemSource>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.Name).IsRequired().HasComment("来源名称");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.DocumentFileItemId).HasComment("文件项Id");
            builder.HasIndex(x => x.Name);
            builder.HasIndex(x => x.CreatedAt);
            builder.HasIndex(x => x.DocumentFileItemId);
            builder.HasComment("文档文件项来源表");
        }));
        
        modelBuilder.Entity<DocumentCatalogI18n>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.DocumentCatalogId).IsRequired().HasComment("文档目录Id");
            builder.Property(x => x.LanguageCode).IsRequired().HasMaxLength(10).HasComment("语言代码");
            builder.Property(x => x.Name).IsRequired().HasComment("多语言目录名称");
            builder.Property(x => x.Description).IsRequired().HasComment("多语言目录描述");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.UpdatedAt).IsRequired().HasComment("更新时间");
            builder.HasIndex(x => x.DocumentCatalogId);
            builder.HasIndex(x => x.LanguageCode);
            builder.HasIndex(x => new { x.DocumentCatalogId, x.LanguageCode }).IsUnique();
            builder.HasOne(x => x.DocumentCatalog)
                .WithMany(x => x.I18nTranslations)
                .HasForeignKey(x => x.DocumentCatalogId)
                .OnDelete(DeleteBehavior.Cascade);
            builder.HasComment("文档目录多语言表");
        }));
        
        modelBuilder.Entity<DocumentFileItemI18n>((builder =>
        {
            builder.HasKey(x => x.Id);
            builder.Property(x => x.Id).HasComment("主键Id");
            builder.Property(x => x.DocumentFileItemId).IsRequired().HasComment("文档文件Id");
            builder.Property(x => x.LanguageCode).IsRequired().HasMaxLength(10).HasComment("语言代码");
            builder.Property(x => x.Title).IsRequired().HasComment("多语言标题");
            builder.Property(x => x.Description).IsRequired().HasComment("多语言描述");
            builder.Property(x => x.Content).IsRequired().HasComment("多语言内容");
            builder.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            builder.Property(x => x.UpdatedAt).IsRequired().HasComment("更新时间");
            builder.HasIndex(x => x.DocumentFileItemId);
            builder.HasIndex(x => x.LanguageCode);
            builder.HasIndex(x => new { x.DocumentFileItemId, x.LanguageCode }).IsUnique();
            builder.HasOne(x => x.DocumentFileItem)
                .WithMany(x => x.I18nTranslations)
                .HasForeignKey(x => x.DocumentFileItemId)
                .OnDelete(DeleteBehavior.Cascade);
            builder.HasComment("文档文件多语言表");
        }));

        modelBuilder.Entity<DocumentOverview>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Title).IsRequired().HasComment("文档标题");
            options.Property(x => x.DocumentId).HasComment("文档Id");
            options.HasIndex(x => x.DocumentId);
            options.HasIndex(x => x.Title);
            options.HasComment("文档概览表");
        });

        modelBuilder.Entity<DocumentCommitRecord>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.CommitMessage).IsRequired().HasComment("提交信息");
            options.Property(x => x.Author).IsRequired().HasComment("作者");
            options.Property(x => x.WarehouseId).HasComment("仓库Id");
            options.Property(x => x.CommitId).HasComment("提交Id");
            options.HasIndex(x => x.WarehouseId);
            options.HasIndex(x => x.CommitId);
            options.HasComment("文档提交记录表");
        });

        modelBuilder.Entity<User>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Name).IsRequired().HasComment("用户名");
            options.Property(x => x.Email).IsRequired().HasComment("邮箱");
            options.Property(x => x.Password).IsRequired().HasComment("密码");
            options.Property(x => x.CreatedAt).HasComment("创建时间");
            options.Property(x => x.LastLoginAt).HasComment("最后登录时间");
            options.HasIndex(x => x.Name);
            options.HasIndex(x => x.Email);
            options.HasIndex(x => x.CreatedAt);
            options.HasIndex(x => x.LastLoginAt);
            options.HasComment("用户表");
        });

        modelBuilder.Entity<TrainingDataset>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Name).IsRequired().HasComment("数据集名称");
            options.Property(x => x.CreatedAt).HasComment("创建时间");
            options.Property(x => x.WarehouseId).HasComment("仓库Id");
            options.HasIndex(x => x.Name);
            options.HasIndex(x => x.CreatedAt);
            options.HasIndex(x => x.WarehouseId);
            options.HasComment("训练数据集表");
        });

        modelBuilder.Entity<FineTuningTask>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Name).IsRequired().HasComment("微调任务名称");
            options.Property(x => x.CreatedAt).HasComment("创建时间");
            options.Property(x => x.TrainingDatasetId).HasComment("训练数据集Id");
            options.Property(x => x.UserId).HasComment("用户Id");
            options.Property(x => x.Status).HasComment("任务状态");
            options.Property(x => x.WarehouseId).HasComment("仓库Id");
            options.Property(x => x.DocumentCatalogId).HasComment("目录Id");
            options.HasIndex(x => x.Name);
            options.HasIndex(x => x.CreatedAt);
            options.HasIndex(x => x.TrainingDatasetId);
            options.HasIndex(x => x.UserId);
            options.HasIndex(x => x.Status);
            options.HasIndex(x => x.WarehouseId);
            options.HasIndex(x => x.DocumentCatalogId);
            options.HasOne(x => x.DocumentCatalog)
                .WithMany()
                .HasForeignKey(x => x.DocumentCatalogId)
                .OnDelete(DeleteBehavior.Cascade);
            options.HasComment("微调任务表");
        });

        modelBuilder.Entity<MCPHistory>(options =>
        {
            options.HasComment("MCP历史记录");
            options.Property(x => x.Id).HasComment("主键Id");
            options.HasKey(x => x.Id);
            options.Property(x => x.CreatedAt).HasComment("创建时间");
            options.Property(x => x.WarehouseId).HasComment("仓库Id");
            options.Property(x => x.UserId).HasComment("用户Id");
            options.HasIndex(x => x.CreatedAt);
            options.HasIndex(x => x.WarehouseId);
            options.HasIndex(x => x.UserId);
        });

        modelBuilder.Entity<UserInAuth>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.UserId).IsRequired().HasComment("用户Id");
            options.Property(x => x.Provider).IsRequired().HasComment("认证提供方");
            options.Property(x => x.AuthId).IsRequired().HasComment("认证Id");
            options.HasIndex(x => x.UserId);
            options.HasIndex(x => x.Provider);
            options.HasIndex(x => x.AuthId);
            options.HasComment("用户认证表");
        });

        modelBuilder.Entity<UserInRole>(options =>
        {
            options.HasKey(x => new { x.UserId, x.RoleId });
            options.Property(x => x.UserId).HasComment("用户Id");
            options.Property(x => x.RoleId).HasComment("角色Id");
            options.HasComment("用户角色关联表");
        });

        modelBuilder.Entity<Role>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Name).IsRequired().HasComment("角色名称");
            options.Property(x => x.Description).IsRequired().HasComment("角色描述");
            options.Property(x => x.CreatedAt).HasComment("创建时间");
            options.HasIndex(x => x.Name);
            options.HasIndex(x => x.CreatedAt);
            options.HasComment("角色表");
        });

        modelBuilder.Entity<WarehouseInRole>(options =>
        {
            options.HasKey(x => new { x.WarehouseId, x.RoleId });
            options.Property(x => x.WarehouseId).HasComment("仓库Id");
            options.Property(x => x.RoleId).HasComment("角色Id");
            options.HasIndex(x => x.WarehouseId);
            options.HasIndex(x => x.RoleId);
            options.HasComment("仓库角色关联表");
        });

        modelBuilder.Entity<AccessRecord>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.ResourceType).IsRequired().HasComment("资源类型");
            options.Property(x => x.ResourceId).IsRequired().HasComment("资源Id");
            options.Property(x => x.UserId).HasComment("用户Id");
            options.Property(x => x.IpAddress).IsRequired().HasComment("IP地址");
            options.Property(x => x.UserAgent).IsRequired().HasComment("用户代理");
            options.Property(x => x.Path).IsRequired().HasComment("访问路径");
            options.Property(x => x.Method).IsRequired().HasComment("请求方法");
            options.Property(x => x.StatusCode).HasComment("状态码");
            options.Property(x => x.ResponseTime).HasComment("响应时间");
            options.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            options.HasIndex(x => x.ResourceType);
            options.HasIndex(x => x.ResourceId);
            options.HasIndex(x => x.UserId);
            options.HasIndex(x => x.IpAddress);
            options.HasIndex(x => x.CreatedAt);
            options.HasIndex(x => new { x.ResourceType, x.ResourceId });
            options.HasComment("访问记录表");
        });

        modelBuilder.Entity<DailyStatistics>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Date).IsRequired().HasComment("统计日期");
            options.Property(x => x.NewUsersCount).HasComment("新增用户数");
            options.Property(x => x.NewRepositoriesCount).HasComment("新增仓库数");
            options.Property(x => x.NewDocumentsCount).HasComment("新增文档数");
            options.Property(x => x.PageViews).HasComment("页面访问量");
            options.Property(x => x.UniqueVisitors).HasComment("独立访问用户数");
            options.Property(x => x.ActiveUsers).HasComment("活跃用户数");
            options.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            options.Property(x => x.UpdatedAt).IsRequired().HasComment("更新时间");
            options.HasIndex(x => x.Date).IsUnique();
            options.HasIndex(x => x.CreatedAt);
            options.HasComment("每日统计表");
        });

        modelBuilder.Entity<AppConfig>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.AppId).IsRequired().HasComment("应用ID");
            options.Property(x => x.Name).IsRequired().HasComment("应用名称");
            options.Property(x => x.OrganizationName).IsRequired().HasComment("组织名称");
            options.Property(x => x.RepositoryName).IsRequired().HasComment("仓库名称");
            options.Property(x => x.AllowedDomainsJson).IsRequired().HasComment("允许的域名列表JSON");
            options.Property(x => x.EnableDomainValidation).HasComment("是否启用域名验证");
            options.Property(x => x.Description).HasComment("应用描述");
            options.Property(x => x.Prompt).HasComment("默认提示词");
            options.Property(x => x.Introduction).HasComment("开场白");
            options.Property(x => x.Model).HasComment("选择模型");
            options.Property(x => x.UserId).IsRequired().HasComment("创建用户ID");
            options.Property(x => x.IsEnabled).HasComment("是否启用");
            options.Property(x => x.LastUsedAt).HasComment("最后使用时间");
            options.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            options.HasIndex(x => x.AppId).IsUnique();
            options.HasIndex(x => x.Name);
            options.HasIndex(x => x.OrganizationName);
            options.HasIndex(x => x.RepositoryName);
            options.HasIndex(x => x.UserId);
            options.HasIndex(x => x.IsEnabled);
            options.HasIndex(x => x.CreatedAt);
            options.HasIndex(x => new { x.OrganizationName, x.RepositoryName });

            options.Property(x => x.Mcps)
                .HasConversion((mcps => JsonSerializer.Serialize(mcps, JsonSerializerOptions.Web)),
                    (s => string.IsNullOrEmpty(s)
                        ? (new List<AppConfigMcp>())
                        : (JsonSerializer.Deserialize<List<AppConfigMcp>>(s, JsonSerializerOptions.Web) ??
                           new List<AppConfigMcp>())));

            options.Property(x => x.RecommendedQuestions)
                .HasConversion(x => JsonSerializer.Serialize(x, JsonSerializerOptions.Web),
                    (s => string.IsNullOrEmpty(s)
                        ? new List<string>()
                        : (JsonSerializer.Deserialize<List<string>>(s, JsonSerializerOptions.Web) ??
                           new List<string>())));

            options.HasComment("应用配置表");
        });

        modelBuilder.Entity<SystemSetting>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.Key).IsRequired().HasComment("设置键名");
            options.Property(x => x.Value).HasComment("设置值");
            options.Property(x => x.Group).IsRequired().HasComment("设置分组");
            options.Property(x => x.ValueType).IsRequired().HasComment("设置类型");
            options.Property(x => x.Description).HasComment("设置描述");
            options.Property(x => x.IsSensitive).HasComment("是否敏感信息");
            options.Property(x => x.RequiresRestart).HasComment("是否需要重启生效");
            options.Property(x => x.DefaultValue).HasComment("默认值");
            options.Property(x => x.Order).HasComment("排序顺序");
            options.Property(x => x.IsEnabled).HasComment("是否启用");
            options.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            options.Property(x => x.UpdatedAt).IsRequired().HasComment("更新时间");
            options.HasIndex(x => x.Key).IsUnique();
            options.HasIndex(x => x.Group);
            options.HasIndex(x => x.Order);
            options.HasIndex(x => x.IsEnabled);
            options.HasComment("系统设置表");
        });

        modelBuilder.Entity<MiniMap>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.WarehouseId).IsRequired().HasComment("仓库Id");
            options.Property(x => x.Value).IsRequired().HasComment("小地图数据");
            options.HasIndex(x => x.WarehouseId);
            options.HasComment("小地图表");
        });

        modelBuilder.Entity<WarehouseSyncRecord>(options =>
        {
            options.HasKey(x => x.Id);
            options.Property(x => x.Id).HasComment("主键Id");
            options.Property(x => x.WarehouseId).IsRequired().HasComment("仓库Id");
            options.Property(x => x.Status).IsRequired().HasComment("同步状态");
            options.Property(x => x.StartTime).IsRequired().HasComment("同步开始时间");
            options.Property(x => x.EndTime).HasComment("同步结束时间");
            options.Property(x => x.FromVersion).HasComment("同步前的版本");
            options.Property(x => x.ToVersion).HasComment("同步后的版本");
            options.Property(x => x.ErrorMessage).HasComment("错误信息");
            options.Property(x => x.FileCount).HasComment("同步的文件数量");
            options.Property(x => x.UpdatedFileCount).HasComment("更新的文件数量");
            options.Property(x => x.AddedFileCount).HasComment("新增的文件数量");
            options.Property(x => x.DeletedFileCount).HasComment("删除的文件数量");
            options.Property(x => x.Trigger).IsRequired().HasComment("同步触发方式");
            options.Property(x => x.CreatedAt).IsRequired().HasComment("创建时间");
            options.HasIndex(x => x.WarehouseId);
            options.HasIndex(x => x.Status);
            options.HasIndex(x => x.StartTime);
            options.HasIndex(x => x.Trigger);
            options.HasIndex(x => x.CreatedAt);
            options.HasOne(x => x.Warehouse)
                .WithMany()
                .HasForeignKey(x => x.WarehouseId)
                .OnDelete(DeleteBehavior.Cascade);
            options.HasComment("仓库同步记录表");
        });
    }
}