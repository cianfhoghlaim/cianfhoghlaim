using KoalaWiki.Core;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace KoalaWiki.Provider.Sqlite;


public static class SqliteApplicationExtensions
{
    public static IServiceCollection AddSqliteDbContext(this IServiceCollection services,
        IConfiguration configuration)
    {
        
        services.AddDataAccess<SqliteContext>(((provider, builder) =>
        {
            builder.UseSqlite(configuration.GetConnectionString("Default"));
            
            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        }));
        

        return services;
    }
    public static IServiceCollection AddSqliteDbContext(this IServiceCollection services,
        string connectionString)
    {
        
        services.AddDataAccess<SqliteContext>(((provider, builder) =>
        {
            builder.UseSqlite(connectionString);
            
            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        }));
        

        return services;
    }
}