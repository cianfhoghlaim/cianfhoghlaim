using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.MySQL.Migrations
{
    /// <inheritdoc />
    public partial class Initial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "AccessRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    ResourceType = table.Column<string>(type: "varchar(255)", nullable: false, comment: "资源类型"),
                    ResourceId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "资源Id"),
                    UserId = table.Column<string>(type: "varchar(255)", nullable: true, comment: "用户Id"),
                    IpAddress = table.Column<string>(type: "varchar(255)", nullable: false, comment: "IP地址"),
                    UserAgent = table.Column<string>(type: "longtext", nullable: false, comment: "用户代理"),
                    Path = table.Column<string>(type: "longtext", nullable: false, comment: "访问路径"),
                    Method = table.Column<string>(type: "longtext", nullable: false, comment: "请求方法"),
                    StatusCode = table.Column<int>(type: "int", nullable: false, comment: "状态码"),
                    ResponseTime = table.Column<long>(type: "bigint", nullable: false, comment: "响应时间"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AccessRecords", x => x.Id);
                },
                comment: "访问记录表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "AppConfigs",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    AppId = table.Column<string>(type: "varchar(64)", maxLength: 64, nullable: false, comment: "应用ID"),
                    Name = table.Column<string>(type: "varchar(100)", maxLength: 100, nullable: false, comment: "应用名称"),
                    OrganizationName = table.Column<string>(type: "varchar(100)", maxLength: 100, nullable: false, comment: "组织名称"),
                    RepositoryName = table.Column<string>(type: "varchar(100)", maxLength: 100, nullable: false, comment: "仓库名称"),
                    AllowedDomainsJson = table.Column<string>(type: "longtext", nullable: false, comment: "允许的域名列表JSON"),
                    EnableDomainValidation = table.Column<bool>(type: "tinyint(1)", nullable: false, comment: "是否启用域名验证"),
                    Description = table.Column<string>(type: "varchar(500)", maxLength: 500, nullable: false, comment: "应用描述"),
                    UserId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "创建用户ID"),
                    IsEnabled = table.Column<bool>(type: "tinyint(1)", nullable: false, comment: "是否启用"),
                    LastUsedAt = table.Column<DateTime>(type: "datetime(6)", nullable: true, comment: "最后使用时间"),
                    Prompt = table.Column<string>(type: "longtext", nullable: true, comment: "默认提示词"),
                    Introduction = table.Column<string>(type: "longtext", nullable: true, comment: "开场白"),
                    Model = table.Column<string>(type: "longtext", nullable: true, comment: "选择模型"),
                    RecommendedQuestions = table.Column<string>(type: "longtext", nullable: true),
                    Mcps = table.Column<string>(type: "longtext", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AppConfigs", x => x.Id);
                },
                comment: "应用配置表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "DailyStatistics",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    Date = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "统计日期"),
                    NewUsersCount = table.Column<int>(type: "int", nullable: false, comment: "新增用户数"),
                    NewRepositoriesCount = table.Column<int>(type: "int", nullable: false, comment: "新增仓库数"),
                    NewDocumentsCount = table.Column<int>(type: "int", nullable: false, comment: "新增文档数"),
                    PageViews = table.Column<int>(type: "int", nullable: false, comment: "页面访问量"),
                    UniqueVisitors = table.Column<int>(type: "int", nullable: false, comment: "独立访问用户数"),
                    ActiveUsers = table.Column<int>(type: "int", nullable: false, comment: "活跃用户数"),
                    UpdatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "更新时间"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DailyStatistics", x => x.Id);
                },
                comment: "每日统计表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "DocumentCatalogs",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "目录名称"),
                    Url = table.Column<string>(type: "longtext", nullable: false),
                    Description = table.Column<string>(type: "longtext", nullable: false, comment: "目录描述"),
                    ParentId = table.Column<string>(type: "varchar(255)", nullable: true, comment: "父级目录Id"),
                    Order = table.Column<int>(type: "int", nullable: false),
                    DucumentId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "文档Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "所属仓库Id"),
                    IsCompleted = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    Prompt = table.Column<string>(type: "longtext", nullable: false),
                    IsDeleted = table.Column<bool>(type: "tinyint(1)", nullable: false, comment: "是否已删除"),
                    DeletedTime = table.Column<DateTime>(type: "datetime(6)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCatalogs", x => x.Id);
                },
                comment: "文档目录表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "DocumentCommitRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库Id"),
                    CommitId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "提交Id"),
                    CommitMessage = table.Column<string>(type: "longtext", nullable: false, comment: "提交信息"),
                    Title = table.Column<string>(type: "longtext", nullable: false),
                    Author = table.Column<string>(type: "longtext", nullable: false, comment: "作者"),
                    LastUpdate = table.Column<DateTime>(type: "datetime(6)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCommitRecords", x => x.Id);
                },
                comment: "文档提交记录表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "DocumentFileItems",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    Title = table.Column<string>(type: "varchar(255)", nullable: false, comment: "文件标题"),
                    Description = table.Column<string>(type: "longtext", nullable: false, comment: "文件描述"),
                    Content = table.Column<string>(type: "longtext", nullable: false),
                    CommentCount = table.Column<long>(type: "bigint", nullable: false),
                    Size = table.Column<long>(type: "bigint", nullable: false),
                    DocumentCatalogId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "目录Id"),
                    RequestToken = table.Column<int>(type: "int", nullable: false),
                    ResponseToken = table.Column<int>(type: "int", nullable: false),
                    IsEmbedded = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    Metadata = table.Column<string>(type: "longtext", nullable: false, comment: "元数据"),
                    Extra = table.Column<string>(type: "longtext", nullable: false, comment: "扩展信息"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentFileItems", x => x.Id);
                },
                comment: "文档文件项表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "DocumentOverviews",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    DocumentId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "文档Id"),
                    Content = table.Column<string>(type: "longtext", nullable: false),
                    Title = table.Column<string>(type: "varchar(255)", nullable: false, comment: "文档标题"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentOverviews", x => x.Id);
                },
                comment: "文档概览表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "Documents",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "所属仓库Id"),
                    LastUpdate = table.Column<DateTime>(type: "datetime(6)", nullable: false),
                    Description = table.Column<string>(type: "longtext", nullable: false, comment: "文档描述"),
                    LikeCount = table.Column<long>(type: "bigint", nullable: false),
                    CommentCount = table.Column<long>(type: "bigint", nullable: false),
                    GitPath = table.Column<string>(type: "longtext", nullable: false),
                    Status = table.Column<byte>(type: "tinyint unsigned", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Documents", x => x.Id);
                },
                comment: "文档表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "MCPHistories",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    Question = table.Column<string>(type: "longtext", nullable: false),
                    Answer = table.Column<string>(type: "longtext", nullable: false),
                    UserId = table.Column<string>(type: "varchar(255)", nullable: true, comment: "用户Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: true, comment: "仓库Id"),
                    CostTime = table.Column<int>(type: "int", nullable: false),
                    Ip = table.Column<string>(type: "longtext", nullable: false),
                    UserAgent = table.Column<string>(type: "longtext", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MCPHistories", x => x.Id);
                },
                comment: "MCP历史记录")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "MiniMaps",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库Id"),
                    Value = table.Column<string>(type: "longtext", nullable: false, comment: "小地图数据"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MiniMaps", x => x.Id);
                },
                comment: "小地图表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "Roles",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "角色名称"),
                    Description = table.Column<string>(type: "longtext", nullable: false, comment: "角色描述"),
                    IsActive = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false),
                    IsSystemRole = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Roles", x => x.Id);
                },
                comment: "角色表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "TrainingDatasets",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库Id"),
                    UserId = table.Column<string>(type: "longtext", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间"),
                    UpdatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "数据集名称"),
                    Endpoint = table.Column<string>(type: "longtext", nullable: false),
                    ApiKey = table.Column<string>(type: "longtext", nullable: false),
                    Prompt = table.Column<string>(type: "longtext", nullable: false),
                    Model = table.Column<string>(type: "longtext", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TrainingDatasets", x => x.Id);
                },
                comment: "训练数据集表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "UserInAuths",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    UserId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "用户Id"),
                    Provider = table.Column<string>(type: "varchar(255)", nullable: false, comment: "认证提供方"),
                    AuthId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "认证Id"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserInAuths", x => x.Id);
                },
                comment: "用户认证表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "UserInRoles",
                columns: table => new
                {
                    UserId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "用户Id"),
                    RoleId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "角色Id")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserInRoles", x => new { x.UserId, x.RoleId });
                },
                comment: "用户角色关联表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "用户名"),
                    Email = table.Column<string>(type: "varchar(255)", nullable: false, comment: "邮箱"),
                    Password = table.Column<string>(type: "longtext", nullable: false, comment: "密码"),
                    Avatar = table.Column<string>(type: "longtext", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间"),
                    UpdatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: true),
                    LastLoginAt = table.Column<DateTime>(type: "datetime(6)", nullable: true, comment: "最后登录时间"),
                    LastLoginIp = table.Column<string>(type: "longtext", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Users", x => x.Id);
                },
                comment: "用户表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "WarehouseInRoles",
                columns: table => new
                {
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库Id"),
                    RoleId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "角色Id"),
                    IsReadOnly = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    IsWrite = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    IsDelete = table.Column<bool>(type: "tinyint(1)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_WarehouseInRoles", x => new { x.WarehouseId, x.RoleId });
                },
                comment: "仓库角色关联表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "Warehouses",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    OrganizationName = table.Column<string>(type: "varchar(255)", nullable: false, comment: "组织名称"),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库名称"),
                    Description = table.Column<string>(type: "longtext", nullable: false, comment: "仓库描述"),
                    Address = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库地址"),
                    GitUserName = table.Column<string>(type: "longtext", nullable: true),
                    GitPassword = table.Column<string>(type: "longtext", nullable: true),
                    Email = table.Column<string>(type: "longtext", nullable: true),
                    Type = table.Column<string>(type: "varchar(255)", nullable: true, comment: "仓库类型"),
                    Branch = table.Column<string>(type: "varchar(255)", nullable: true, comment: "分支"),
                    Status = table.Column<byte>(type: "tinyint unsigned", nullable: false, comment: "仓库状态"),
                    Error = table.Column<string>(type: "longtext", nullable: true),
                    Prompt = table.Column<string>(type: "longtext", nullable: true),
                    Version = table.Column<string>(type: "longtext", nullable: true),
                    IsEmbedded = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    IsRecommended = table.Column<bool>(type: "tinyint(1)", nullable: false),
                    OptimizedDirectoryStructure = table.Column<string>(type: "longtext", nullable: true),
                    Readme = table.Column<string>(type: "longtext", nullable: true),
                    Classify = table.Column<int>(type: "int", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Warehouses", x => x.Id);
                },
                comment: "知识仓库表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "FineTuningTasks",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "仓库Id"),
                    TrainingDatasetId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "训练数据集Id"),
                    DocumentCatalogId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "目录Id"),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "微调任务名称"),
                    UserId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "用户Id"),
                    Description = table.Column<string>(type: "longtext", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间"),
                    StartedAt = table.Column<DateTime>(type: "datetime(6)", nullable: true),
                    CompletedAt = table.Column<DateTime>(type: "datetime(6)", nullable: true),
                    Status = table.Column<int>(type: "int", nullable: false, comment: "任务状态"),
                    Dataset = table.Column<string>(type: "longtext", nullable: false),
                    Error = table.Column<string>(type: "longtext", nullable: true),
                    OriginalDataset = table.Column<string>(type: "longtext", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_FineTuningTasks", x => x.Id);
                    table.ForeignKey(
                        name: "FK_FineTuningTasks_DocumentCatalogs_DocumentCatalogId",
                        column: x => x.DocumentCatalogId,
                        principalTable: "DocumentCatalogs",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                },
                comment: "微调任务表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateTable(
                name: "DocumentFileItemSources",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false, comment: "主键Id"),
                    DocumentFileItemId = table.Column<string>(type: "varchar(255)", nullable: false, comment: "文件项Id"),
                    Address = table.Column<string>(type: "longtext", nullable: false),
                    Name = table.Column<string>(type: "varchar(255)", nullable: false, comment: "来源名称"),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentFileItemSources", x => x.Id);
                    table.ForeignKey(
                        name: "FK_DocumentFileItemSources_DocumentFileItems_DocumentFileItemId",
                        column: x => x.DocumentFileItemId,
                        principalTable: "DocumentFileItems",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                },
                comment: "文档文件项来源表")
                .Annotation("MySQL:Charset", "utf8mb4");

            migrationBuilder.CreateIndex(
                name: "IX_AccessRecords_CreatedAt",
                table: "AccessRecords",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_AccessRecords_IpAddress",
                table: "AccessRecords",
                column: "IpAddress");

            migrationBuilder.CreateIndex(
                name: "IX_AccessRecords_ResourceId",
                table: "AccessRecords",
                column: "ResourceId");

            migrationBuilder.CreateIndex(
                name: "IX_AccessRecords_ResourceType",
                table: "AccessRecords",
                column: "ResourceType");

            migrationBuilder.CreateIndex(
                name: "IX_AccessRecords_ResourceType_ResourceId",
                table: "AccessRecords",
                columns: new[] { "ResourceType", "ResourceId" });

            migrationBuilder.CreateIndex(
                name: "IX_AccessRecords_UserId",
                table: "AccessRecords",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_AppId",
                table: "AppConfigs",
                column: "AppId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_CreatedAt",
                table: "AppConfigs",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_IsEnabled",
                table: "AppConfigs",
                column: "IsEnabled");

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_Name",
                table: "AppConfigs",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_OrganizationName",
                table: "AppConfigs",
                column: "OrganizationName");

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_OrganizationName_RepositoryName",
                table: "AppConfigs",
                columns: new[] { "OrganizationName", "RepositoryName" });

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_RepositoryName",
                table: "AppConfigs",
                column: "RepositoryName");

            migrationBuilder.CreateIndex(
                name: "IX_AppConfigs_UserId",
                table: "AppConfigs",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_DailyStatistics_CreatedAt",
                table: "DailyStatistics",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DailyStatistics_Date",
                table: "DailyStatistics",
                column: "Date",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_CreatedAt",
                table: "DocumentCatalogs",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_DucumentId",
                table: "DocumentCatalogs",
                column: "DucumentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_IsDeleted",
                table: "DocumentCatalogs",
                column: "IsDeleted");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_Name",
                table: "DocumentCatalogs",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_ParentId",
                table: "DocumentCatalogs",
                column: "ParentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_WarehouseId",
                table: "DocumentCatalogs",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCommitRecords_CommitId",
                table: "DocumentCommitRecords",
                column: "CommitId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCommitRecords_WarehouseId",
                table: "DocumentCommitRecords",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItems_CreatedAt",
                table: "DocumentFileItems",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItems_DocumentCatalogId",
                table: "DocumentFileItems",
                column: "DocumentCatalogId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItems_Title",
                table: "DocumentFileItems",
                column: "Title");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemSources_CreatedAt",
                table: "DocumentFileItemSources",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemSources_DocumentFileItemId",
                table: "DocumentFileItemSources",
                column: "DocumentFileItemId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemSources_Name",
                table: "DocumentFileItemSources",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentOverviews_DocumentId",
                table: "DocumentOverviews",
                column: "DocumentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentOverviews_Title",
                table: "DocumentOverviews",
                column: "Title");

            migrationBuilder.CreateIndex(
                name: "IX_Documents_CreatedAt",
                table: "Documents",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Documents_WarehouseId",
                table: "Documents",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_CreatedAt",
                table: "FineTuningTasks",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_DocumentCatalogId",
                table: "FineTuningTasks",
                column: "DocumentCatalogId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_Name",
                table: "FineTuningTasks",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_Status",
                table: "FineTuningTasks",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_TrainingDatasetId",
                table: "FineTuningTasks",
                column: "TrainingDatasetId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_UserId",
                table: "FineTuningTasks",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_WarehouseId",
                table: "FineTuningTasks",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_MCPHistories_CreatedAt",
                table: "MCPHistories",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_MCPHistories_UserId",
                table: "MCPHistories",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_MCPHistories_WarehouseId",
                table: "MCPHistories",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_MiniMaps_WarehouseId",
                table: "MiniMaps",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_Roles_CreatedAt",
                table: "Roles",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Roles_Name",
                table: "Roles",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_TrainingDatasets_CreatedAt",
                table: "TrainingDatasets",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_TrainingDatasets_Name",
                table: "TrainingDatasets",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_TrainingDatasets_WarehouseId",
                table: "TrainingDatasets",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_UserInAuths_AuthId",
                table: "UserInAuths",
                column: "AuthId");

            migrationBuilder.CreateIndex(
                name: "IX_UserInAuths_Provider",
                table: "UserInAuths",
                column: "Provider");

            migrationBuilder.CreateIndex(
                name: "IX_UserInAuths_UserId",
                table: "UserInAuths",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_Users_CreatedAt",
                table: "Users",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Users_Email",
                table: "Users",
                column: "Email");

            migrationBuilder.CreateIndex(
                name: "IX_Users_LastLoginAt",
                table: "Users",
                column: "LastLoginAt");

            migrationBuilder.CreateIndex(
                name: "IX_Users_Name",
                table: "Users",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseInRoles_RoleId",
                table: "WarehouseInRoles",
                column: "RoleId");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseInRoles_WarehouseId",
                table: "WarehouseInRoles",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Address",
                table: "Warehouses",
                column: "Address");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Branch",
                table: "Warehouses",
                column: "Branch");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_CreatedAt",
                table: "Warehouses",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Name",
                table: "Warehouses",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_OrganizationName",
                table: "Warehouses",
                column: "OrganizationName");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Status",
                table: "Warehouses",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Type",
                table: "Warehouses",
                column: "Type");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "AccessRecords");

            migrationBuilder.DropTable(
                name: "AppConfigs");

            migrationBuilder.DropTable(
                name: "DailyStatistics");

            migrationBuilder.DropTable(
                name: "DocumentCommitRecords");

            migrationBuilder.DropTable(
                name: "DocumentFileItemSources");

            migrationBuilder.DropTable(
                name: "DocumentOverviews");

            migrationBuilder.DropTable(
                name: "Documents");

            migrationBuilder.DropTable(
                name: "FineTuningTasks");

            migrationBuilder.DropTable(
                name: "MCPHistories");

            migrationBuilder.DropTable(
                name: "MiniMaps");

            migrationBuilder.DropTable(
                name: "Roles");

            migrationBuilder.DropTable(
                name: "TrainingDatasets");

            migrationBuilder.DropTable(
                name: "UserInAuths");

            migrationBuilder.DropTable(
                name: "UserInRoles");

            migrationBuilder.DropTable(
                name: "Users");

            migrationBuilder.DropTable(
                name: "WarehouseInRoles");

            migrationBuilder.DropTable(
                name: "Warehouses");

            migrationBuilder.DropTable(
                name: "DocumentFileItems");

            migrationBuilder.DropTable(
                name: "DocumentCatalogs");
        }
    }
}
