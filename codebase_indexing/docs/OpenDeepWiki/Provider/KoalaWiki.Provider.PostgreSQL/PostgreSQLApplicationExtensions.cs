using KoalaWiki.Core;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace KoalaWiki.Provider.PostgreSQL;


public static class PostgreSQLApplicationExtensions
{
    public static IServiceCollection AddPostgreSQLDbContext(this IServiceCollection services,
        IConfiguration configuration)
    {
        
        services.AddDataAccess<PostgreSQLContext>((_, builder) =>
        {
            builder.UseNpgsql(configuration.GetConnectionString("Default"));
            
            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        });
        

        return services;
    }
    
    public static IServiceCollection AddPostgreSQLDbContext(this IServiceCollection services,
        string connectionString)
    {
        
        services.AddDataAccess<PostgreSQLContext>(((provider, builder) =>
        {
            builder.UseNpgsql(connectionString);
            
            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        }));
        

        return services;
    }
}