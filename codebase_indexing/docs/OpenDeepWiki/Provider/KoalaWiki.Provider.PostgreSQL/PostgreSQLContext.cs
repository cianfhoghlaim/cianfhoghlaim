using KoalaWiki.Core.DataAccess;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace KoalaWiki.Provider.PostgreSQL;

public class PostgreSQLContext(DbContextOptions<PostgreSQLContext> options)
    : KoalaWikiContext<PostgreSQLContext>(options)
{
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.ConfigureWarnings(warnings =>
            warnings.Ignore(RelationalEventId.PendingModelChangesWarning));
    }
}