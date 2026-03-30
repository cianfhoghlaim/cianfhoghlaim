using KoalaWiki.Core;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace KoalaWiki.Provider.SqlServer;

public static class SqlServerApplicationExtensions
{
    public static IServiceCollection AddSqlServerDbContext(this IServiceCollection services,
        IConfiguration configuration)
    {
        services.AddDataAccess<SqlServerContext>((_, builder) =>
        {
            builder.UseSqlServer(configuration.GetConnectionString("Default"));

            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        });

        return services;
    }

    public static IServiceCollection AddSqlServerDbContext(this IServiceCollection services,
        string connectionString)
    {
        services.AddDataAccess<SqlServerContext>(((provider, builder) =>
        {
            builder.UseSqlServer(connectionString);

            // sql日志不输出控制台
            builder.UseLoggerFactory(LoggerFactory.Create(_ => { }));
        }));

        return services;
    }
}
