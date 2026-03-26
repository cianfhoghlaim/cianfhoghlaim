using KoalaWiki.Core.Extensions;
using KoalaWiki.Provider.PostgreSQL;
using KoalaWiki.Provider.Sqlite;
using KoalaWiki.Provider.SqlServer;
using KoalaWiki.Provider.MySQL;

namespace KoalaWiki.Extensions;

public static class DbContextExtensions
{
    public static IServiceCollection AddDbContext(this IServiceCollection services,
        IConfiguration configuration)
    {
        var dbType = Environment.GetEnvironmentVariable("DB_TYPE").GetTrimmedValueOrEmpty();
        var dbConnectionString = Environment.GetEnvironmentVariable("DB_CONNECTION_STRING").GetTrimmedValueOrEmpty();

        if (string.IsNullOrEmpty(dbType) || string.IsNullOrEmpty(dbConnectionString))
        {
            var dbTypeFromConfig = configuration.GetConnectionString("type")?.ToLower();
            if (dbTypeFromConfig == "postgres")
            {
                AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);
                AppContext.SetSwitch("Npgsql.DisableDateTimeInfinityConversions", true);
                services.AddPostgreSQLDbContext(configuration);
            }
            else if (dbTypeFromConfig == "sqlserver")
            {
                services.AddSqlServerDbContext(configuration);
            }
            else if (dbTypeFromConfig == "mysql")
            {
                services.AddMySQLDbContext(configuration);
            }
            else
            {
                services.AddSqliteDbContext(configuration);
            }

            return services;
        }

        if (dbType.Equals("postgres", StringComparison.OrdinalIgnoreCase))
        {
            AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);
            AppContext.SetSwitch("Npgsql.DisableDateTimeInfinityConversions", true);
            services.AddPostgreSQLDbContext(dbConnectionString);
        }
        else if (dbType.Equals("sqlserver", StringComparison.OrdinalIgnoreCase))
        {
            services.AddSqlServerDbContext(dbConnectionString);
        }
        else if (dbType.Equals("mysql", StringComparison.OrdinalIgnoreCase))
        {
            services.AddMySQLDbContext(dbConnectionString);
        }
        else
        {
            services.AddSqliteDbContext(dbConnectionString);
        }

        return services;
    }
}