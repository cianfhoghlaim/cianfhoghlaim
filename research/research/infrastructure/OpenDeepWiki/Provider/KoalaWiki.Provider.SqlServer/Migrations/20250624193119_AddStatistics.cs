using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.SqlServer.Migrations
{
    /// <inheritdoc />
    public partial class AddStatistics : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "AccessRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "主键Id"),
                    ResourceType = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "资源类型"),
                    ResourceId = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "资源Id"),
                    UserId = table.Column<string>(type: "nvarchar(450)", nullable: true, comment: "用户Id"),
                    IpAddress = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "IP地址"),
                    UserAgent = table.Column<string>(type: "nvarchar(max)", nullable: false, comment: "用户代理"),
                    Path = table.Column<string>(type: "nvarchar(max)", nullable: false, comment: "访问路径"),
                    Method = table.Column<string>(type: "nvarchar(max)", nullable: false, comment: "请求方法"),
                    StatusCode = table.Column<int>(type: "int", nullable: false, comment: "状态码"),
                    ResponseTime = table.Column<long>(type: "bigint", nullable: false, comment: "响应时间"),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AccessRecords", x => x.Id);
                },
                comment: "访问记录表");

            migrationBuilder.CreateTable(
                name: "DailyStatistics",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "主键Id"),
                    Date = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "统计日期"),
                    NewUsersCount = table.Column<int>(type: "int", nullable: false, comment: "新增用户数"),
                    NewRepositoriesCount = table.Column<int>(type: "int", nullable: false, comment: "新增仓库数"),
                    NewDocumentsCount = table.Column<int>(type: "int", nullable: false, comment: "新增文档数"),
                    PageViews = table.Column<int>(type: "int", nullable: false, comment: "页面访问量"),
                    UniqueVisitors = table.Column<int>(type: "int", nullable: false, comment: "独立访问用户数"),
                    ActiveUsers = table.Column<int>(type: "int", nullable: false, comment: "活跃用户数"),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "更新时间"),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DailyStatistics", x => x.Id);
                },
                comment: "每日统计表");

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
                name: "IX_DailyStatistics_CreatedAt",
                table: "DailyStatistics",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DailyStatistics_Date",
                table: "DailyStatistics",
                column: "Date",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "AccessRecords");

            migrationBuilder.DropTable(
                name: "DailyStatistics");
        }
    }
}
