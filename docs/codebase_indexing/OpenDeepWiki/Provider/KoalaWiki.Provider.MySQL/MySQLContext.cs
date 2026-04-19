using KoalaWiki.Core.DataAccess;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace KoalaWiki.Provider.MySQL;

public class MySQLContext(DbContextOptions<MySQLContext> options)
    : KoalaWikiContext<MySQLContext>(options)
{
}