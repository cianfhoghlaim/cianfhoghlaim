using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.SqlServer.Migrations
{
    /// <inheritdoc />
    public partial class AddApp : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "AppConfigs",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "主键Id"),
                    AppId = table.Column<string>(type: "nvarchar(64)", maxLength: 64, nullable: false, comment: "应用ID"),
                    Name = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false, comment: "应用名称"),
                    OrganizationName = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false, comment: "组织名称"),
                    RepositoryName = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false, comment: "仓库名称"),
                    AllowedDomainsJson = table.Column<string>(type: "nvarchar(max)", nullable: false, comment: "允许的域名列表JSON"),
                    EnableDomainValidation = table.Column<bool>(type: "bit", nullable: false, comment: "是否启用域名验证"),
                    Description = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: false, comment: "应用描述"),
                    UserId = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "创建用户ID"),
                    IsEnabled = table.Column<bool>(type: "bit", nullable: false, comment: "是否启用"),
                    LastUsedAt = table.Column<DateTime>(type: "datetime2", nullable: true, comment: "最后使用时间"),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_AppConfigs", x => x.Id);
                },
                comment: "应用配置表");

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
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "AppConfigs");
        }
    }
}
