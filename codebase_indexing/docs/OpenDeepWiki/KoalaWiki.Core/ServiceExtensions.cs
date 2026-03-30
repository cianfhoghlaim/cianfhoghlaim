using System;
using KoalaWiki.Core.DataAccess;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace KoalaWiki.Core;

public static class ServiceExtensions
{
    public static IServiceCollection AddDataAccess<TContext>(this IServiceCollection services,
        Action<IServiceProvider, DbContextOptionsBuilder> configureContext) where TContext : KoalaWikiContext<TContext>
    {
        services.AddDbContext<IKoalaWikiContext, TContext>(configureContext);
        return services;
    }
}