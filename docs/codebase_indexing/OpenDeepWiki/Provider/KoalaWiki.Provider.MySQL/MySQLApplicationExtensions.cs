using KoalaWiki.Core;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace KoalaWiki.Provider.MySQL;

public static class MySQLApplicationExtensions
{
    public static IServiceCollection AddMySQLDbContext(this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddDataAccess<MySQLContext>((_, builder) =>
        {
            builder.UseMySQL(configuration.GetConnectionString("Default"));

            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        });

        return services;
    }

    public static IServiceCollection AddMySQLDbContext(this IServiceCollection services,
        string connectionString)
    {
        services.AddDataAccess<MySQLContext>((_, builder) =>
        {
            builder.UseMySQL(connectionString);

            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        });

        return services;
    }
}