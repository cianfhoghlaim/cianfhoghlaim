using System.Threading;
using System.Threading.Tasks;
using KoalaWiki.Domains;
using KoalaWiki.Domains.DocumentFile;
using KoalaWiki.Domains.FineTuning;
using KoalaWiki.Domains.MCP;
using KoalaWiki.Domains.Users;
using KoalaWiki.Domains.Warehouse;
using KoalaWiki.Domains.Statistics;
using KoalaWiki.Entities;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.Core.DataAccess;

public interface IKoalaWikiContext
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
    /// <summary>
    /// 训练数据集
    /// </summary>
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
    
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = new());

    Task RunMigrateAsync();
}