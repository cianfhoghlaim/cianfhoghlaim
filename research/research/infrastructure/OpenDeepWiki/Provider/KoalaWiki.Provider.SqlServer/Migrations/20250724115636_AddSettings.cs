using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.SqlServer.Migrations
{
    /// <inheritdoc />
    public partial class AddSettings : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "SystemSettings",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "主键Id"),
                    Key = table.Column<string>(type: "nvarchar(100)", maxLength: 100, nullable: false, comment: "设置键名"),
                    Value = table.Column<string>(type: "nvarchar(max)", nullable: true, comment: "设置值"),
                    Group = table.Column<string>(type: "nvarchar(50)", maxLength: 50, nullable: false, comment: "设置分组"),
                    ValueType = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false, comment: "设置类型"),
                    Description = table.Column<string>(type: "nvarchar(500)", maxLength: 500, nullable: true, comment: "设置描述"),
                    IsSensitive = table.Column<bool>(type: "bit", nullable: false, comment: "是否敏感信息"),
                    RequiresRestart = table.Column<bool>(type: "bit", nullable: false, comment: "是否需要重启生效"),
                    DefaultValue = table.Column<string>(type: "nvarchar(max)", nullable: true, comment: "默认值"),
                    Order = table.Column<int>(type: "int", nullable: false, comment: "排序顺序"),
                    IsEnabled = table.Column<bool>(type: "bit", nullable: false, comment: "是否启用"),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "创建时间"),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "更新时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SystemSettings", x => x.Id);
                },
                comment: "系统设置表");

            migrationBuilder.CreateIndex(
                name: "IX_SystemSettings_Group",
                table: "SystemSettings",
                column: "Group");

            migrationBuilder.CreateIndex(
                name: "IX_SystemSettings_IsEnabled",
                table: "SystemSettings",
                column: "IsEnabled");

            migrationBuilder.CreateIndex(
                name: "IX_SystemSettings_Key",
                table: "SystemSettings",
                column: "Key",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_SystemSettings_Order",
                table: "SystemSettings",
                column: "Order");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "SystemSettings");
        }
    }
}
