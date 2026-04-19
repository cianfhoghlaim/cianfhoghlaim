using ImageAgent.Feishu;
using KoalaWiki.BackendService;
using KoalaWiki.Generate;
using KoalaWiki.KoalaWarehouse.Extensions;
using KoalaWiki.MCP;
using KoalaWiki.Mem0;
using KoalaWiki.Services.Feishu.Feishu;
using Microsoft.AspNetCore.StaticFiles;

AppContext.SetSwitch("Microsoft.SemanticKernel.Experimental.GenAI.EnableOTelDiagnosticsSensitive", true);

var builder = WebApplication.CreateBuilder(args);

builder.AddServiceDefaults();

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .WriteTo.Console()
    .CreateLogger();

#region Dynamic Configuration

// 注册动态配置服务
builder.Services.AddScoped<DynamicConfigService>();
builder.Services.AddScoped<DynamicOptionsManager>();

// 临时初始化JWT配置（保持向后兼容）
var jwtOptions = JwtOptions.InitConfig(builder.Configuration);
builder.Services.AddSingleton(jwtOptions);

// 为了向后兼容，仍然保留静态初始化作为回退
// 这些值会在应用启动后被动态配置覆盖
OpenAIOptions.InitConfig(builder.Configuration);
GithubOptions.InitConfig(builder.Configuration);
GiteeOptions.InitConfig(builder.Configuration);
DocumentOptions.InitConfig(builder.Configuration);
FeishuOptions.InitConfig(builder.Configuration);

#endregion

// 设置文件上传大小
builder.Services.Configure<FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 1024 * 1024 * OpenAIOptions.MaxFileLimit; // 10MB
});

builder.WebHost.UseKestrel((options =>
{
    options.Limits.MaxRequestBodySize = 1024 * 1024 * OpenAIOptions.MaxFileLimit; // 10MB
}));

builder.Services.AddResponseCompression();

builder.Services.AddHttpContextAccessor();
builder.Services.AddKoalaMcp();
builder.Services.AddSerilog(Log.Logger);

builder.Services.AddOpenApi();
builder.Services.AddFastApis();
builder.Services.AddSingleton<GitService>();
builder.Services.AddScoped<IWarehouseSyncService, WarehouseSyncService>();
builder.Services.AddScoped<IWarehouseSyncExecutor, WarehouseSyncExecutor>();

// 添加文档处理管道架构
builder.Services.AddDocumentProcessingPipeline();

builder.Services.AddTransient<GlobalMiddleware>();
builder.Services.AddScoped<IUserContext, UserContext>();
builder.Services.AddMemoryCache();

builder.Services.AddHostedService<StatisticsBackgroundService>();
builder.Services.AddHostedService<MiniMapBackgroundService>();

// 添加访问日志队列和后台处理服务
builder.Services.AddSingleton<AccessLogQueue>();
builder.Services.AddHostedService<AccessLogBackgroundService>();

builder.Services.AddScoped<TranslateService>();

builder.Services.AddTransient<FeiShuClient>();
builder.Services.AddHostedService<FeishuStore>();
builder.Services.AddTransient<FeishuHttpClientHandler>();

builder.Services.AddHttpClient("FeiShu")
    .ConfigureHttpClient((client) =>
    {
        client.Timeout = TimeSpan.FromSeconds(600);
        client.DefaultRequestHeaders.Add("User-Agent", "OpenDeepWiki");
        client.DefaultRequestVersion = new Version(2, 0);
        client.DefaultRequestHeaders.Add("Accept", "application/json");
    }).AddHttpMessageHandler<FeishuHttpClientHandler>();

// 添加JWT认证
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
}).AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtOptions.Issuer,
        ValidAudience = jwtOptions.Audience,
        IssuerSigningKey = jwtOptions.GetSymmetricSecurityKey(),
        ClockSkew = TimeSpan.Zero
    };

    // 添加事件处理器以支持从cookie中读取token
    options.Events = new JwtBearerEvents
    {
        OnMessageReceived = context =>
        {
            // 首先检查Authorization header
            var token = context.Request.Headers["Authorization"]
                .FirstOrDefault()?.Split(" ").Last();

            // 如果Authorization header中没有token，则检查cookie
            if (string.IsNullOrEmpty(token))
            {
                token = context.Request.Cookies["token"];
            }

            // 如果找到token，则设置到context中
            if (!string.IsNullOrEmpty(token))
            {
                context.Token = token;
            }

            return Task.CompletedTask;
        }
    };
});


// 添加授权策略
builder.Services.AddAuthorizationBuilder()
    // 添加授权策略
    .AddPolicy("RequireAdminRole", policy => policy.RequireRole("admin"))
    .AddPolicy("RequireUserRole", policy => policy.RequireRole("user", "admin"));

builder.Services
    .AddCors(options =>
    {
        options.AddPolicy("AllowAll", configurePolicy => configurePolicy
            .SetIsOriginAllowed(_ => true)
            .AllowAnyMethod()
            .AllowAnyHeader()
            .AllowCredentials());
    });

builder.Services.AddHostedService<WarehouseTask>();
builder.Services.AddSingleton<WarehouseProcessingTask>();
builder.Services.AddHostedService<WarehouseProcessingTask>(provider =>
    provider.GetRequiredService<WarehouseProcessingTask>());
builder.Services.AddHostedService<DataMigrationTask>();
builder.Services.AddHostedService<Mem0Rag>();

builder.Services.AddDbContext(builder.Configuration);

builder.Services.AddMapster();

builder.Services.AddHttpClient("KoalaWiki", client =>
{
    client.DefaultRequestHeaders.Add("Accept", "application/json");
    client.DefaultRequestHeaders.Add("User-Agent", "KoalaWiki");
});

var app = builder.Build();

app.MapDefaultEndpoints();
app.UseResponseCompression();
// 添加自动迁移代码
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<IKoalaWikiContext>();
    await dbContext.RunMigrateAsync();

    // 初始化动态配置系统
    try
    {
        var dynamicOptionsManager = scope.ServiceProvider.GetRequiredService<DynamicOptionsManager>();
        await dynamicOptionsManager.InitializeAsync();
        Log.Information("动态配置系统初始化成功");
    }
    catch (Exception ex)
    {
        Log.Error(ex, "动态配置系统初始化失败，使用静态配置作为回退");
        // 如果动态配置初始化失败，继续使用静态配置
    }
}

// 添加中间件
app.UseSerilogRequestLogging();

app.UseCors("AllowAll");

// 创建 ContentTypeProvider 实例
var contentTypeProvider = new FileExtensionContentTypeProvider();

// 配置静态文件选项以支持 Brotli 压缩
var staticFileOptions = new StaticFileOptions
{
    ContentTypeProvider = contentTypeProvider,
    OnPrepareResponse = ctx =>
    {
        // 设置缓存控制
        const int durationInSeconds = 60 * 60 * 24 * 7; // 7 days
        ctx.Context.Response.Headers["Cache-Control"] = $"public, max-age={durationInSeconds}";
    }
};

// 添加静态文件服务
app.UseStaticFiles(staticFileOptions);

// 自定义中间件：处理 Brotli 压缩文件优先和 SPA 回退
app.Use(async (context, next) =>
{
    var path = context.Request.Path.Value;

    // 检查是否是 API 路由，如果是则跳过
    if (path != null && (path.StartsWith("/api") || path.StartsWith("/mcp")))
    {
        await next();
        return;
    }

    // 如果请求支持 Brotli 编码
    if (context.Request.Headers.AcceptEncoding.ToString().Contains("br"))
    {
        var wwwrootPath = Path.Combine(app.Environment.ContentRootPath, "wwwroot");
        var requestPath = path?.TrimStart('/') ?? "";

        // 如果是根路径或目录，尝试 index.html
        if (string.IsNullOrEmpty(requestPath) || requestPath.EndsWith("/"))
        {
            requestPath = Path.Combine(requestPath, "index.html");
        }

        var brFilePath = Path.Combine(wwwrootPath, requestPath + ".br");
        var originalFilePath = Path.Combine(wwwrootPath, requestPath);

        // 检查 .br 文件是否存在
        if (File.Exists(brFilePath))
        {
            context.Response.Headers["Content-Encoding"] = "br";

            // 使用 ContentTypeProvider 获取内容类型
            if (!contentTypeProvider.TryGetContentType(requestPath, out var contentType))
            {
                contentType = "application/octet-stream";
            }

            context.Response.ContentType = contentType;

            await context.Response.SendFileAsync(brFilePath);
            return;
        }
        // 如果原始文件存在，继续正常处理
        else if (File.Exists(originalFilePath))
        {
            // 使用 ContentTypeProvider 获取内容类型
            if (!contentTypeProvider.TryGetContentType(originalFilePath, out var contentType))
            {
                contentType = "application/octet-stream";
            }

            context.Response.ContentType = contentType;

            await context.Response.SendFileAsync(originalFilePath);
            return;
        }
    }

    await next();

    // SPA 回退：如果是 404 且不是 API 调用，返回 index.html
    if (context.Response.StatusCode == 404 &&
        !Path.HasExtension(context.Request.Path.Value) &&
        path != null && !path.StartsWith("/api"))
    {
        context.Response.StatusCode = 200;
        context.Response.ContentType = "text/html";
        await context.Response.SendFileAsync(Path.Combine(app.Environment.ContentRootPath, "wwwroot", "index.html"));
    }
});

app.UseAuthentication();
app.UseAuthorization();

// 添加访问记录中间件（在认证授权之后，业务逻辑之前）
app.UseAccessRecord();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}

// Add SSE keep-alive middleware to prevent connection timeout after ~5 minutes of inactivity
// This is especially important for MCP SSE endpoints used by Claude Code
app.UseMiddleware<SseKeepAliveMiddleware>();

app.MapMcp("/api/mcp");


app.UseMiddleware<GlobalMiddleware>();

// 添加权限中间件
app.UseMiddleware<PermissionMiddleware>();

app.MapSitemap();

app.MapFastApis();

app.Run();