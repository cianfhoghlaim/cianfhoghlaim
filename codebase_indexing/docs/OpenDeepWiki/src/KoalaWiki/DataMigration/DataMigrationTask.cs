using KoalaWiki.Core.DataAccess;
using KoalaWiki.Domains.Users;
using Microsoft.EntityFrameworkCore;

namespace KoalaWiki.DataMigration;

public class DataMigrationTask(IServiceProvider service) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await Task.Delay(1000, stoppingToken);

        await using var scope = service.CreateAsyncScope();

        var dbContext = scope.ServiceProvider.GetService<IKoalaWikiContext>();


        await InitializeUsersAsync(dbContext, stoppingToken);
    }

    /// <summary>
    /// 用户初始化任务
    /// </summary>
    private async Task InitializeUsersAsync(IKoalaWikiContext dbContext, CancellationToken stoppingToken)
    {
        // 判断是否存在账号
        if (await dbContext.UserInRoles.AnyAsync(cancellationToken: stoppingToken))
        {
            // 如果存在账号则不进行初始化
            return;
        }

        // 迁移数据库
        var adminRole = new Role
        {
            Id = Guid.NewGuid().ToString("N"),
            Name = "admin",
            Description = "管理员角色",
            CreatedAt = DateTime.UtcNow,
            IsSystemRole = true,
            UpdatedAt = DateTime.UtcNow,
        };

        var userRole = new Role
        {
            Id = Guid.NewGuid().ToString("N"),
            Name = "user",
            Description = "普通用户角色",
            IsSystemRole = false,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow,
        };

        // 创建管理员角色
        await dbContext.Roles.AddRangeAsync(adminRole, userRole);

        if (await dbContext.Users.AnyAsync(cancellationToken: stoppingToken))
        {
            // 给所有用户初始化角色
            var users = await dbContext.Users.ToListAsync(cancellationToken: stoppingToken);
            foreach (var user in users)
            {
                if (user.Name == "admin")
                {
                    await dbContext.UserInRoles.AddAsync(new UserInRole
                    {
                        UserId = user.Id,
                        RoleId = adminRole.Id
                    }, stoppingToken);
                }
                else
                {
                    await dbContext.UserInRoles.AddAsync(new UserInRole
                    {
                        UserId = user.Id,
                        RoleId = userRole.Id
                    }, stoppingToken);
                }
            }

            await dbContext.SaveChangesAsync(cancellationToken: stoppingToken);

            return;
        }

        // 迁移数据库
        var admin = new User
        {
            Id = Guid.NewGuid().ToString("N"),
            Name = "admin",
            Password = "admin",
            Email = "239573049@qq.com",
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow,
            Avatar = "/avatar.png",
        };

        // 创建管理员账号
        await dbContext.Users.AddAsync(admin, stoppingToken);

        await dbContext.UserInRoles.AddAsync(new UserInRole()
        {
            UserId = admin.Id,
            RoleId = adminRole.Id
        }, stoppingToken);

        await dbContext.SaveChangesAsync(stoppingToken);
    }
}