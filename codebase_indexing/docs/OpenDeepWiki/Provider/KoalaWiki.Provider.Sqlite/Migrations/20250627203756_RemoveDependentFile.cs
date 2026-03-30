using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class RemoveDependentFile : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ChatShareMessageItems");

            migrationBuilder.DropTable(
                name: "ChatShareMessages");

            migrationBuilder.DropColumn(
                name: "DependentFile",
                table: "DocumentCatalogs");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "DependentFile",
                table: "DocumentCatalogs",
                type: "TEXT",
                nullable: false,
                defaultValue: "",
                comment: "依赖文件");

            migrationBuilder.CreateTable(
                name: "ChatShareMessageItems",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false, comment: "主键Id"),
                    Answer = table.Column<string>(type: "TEXT", nullable: false),
                    ChatShareMessageId = table.Column<string>(type: "TEXT", nullable: false, comment: "聊天分享消息Id"),
                    CompletionToken = table.Column<int>(type: "INTEGER", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    Files = table.Column<string>(type: "TEXT", nullable: false, comment: "相关文件"),
                    PromptToken = table.Column<int>(type: "INTEGER", nullable: false),
                    Question = table.Column<string>(type: "TEXT", nullable: false, comment: "问题内容"),
                    Think = table.Column<string>(type: "TEXT", nullable: false),
                    TotalTime = table.Column<int>(type: "INTEGER", nullable: false),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false, comment: "仓库Id")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChatShareMessageItems", x => x.Id);
                },
                comment: "聊天分享消息项表");

            migrationBuilder.CreateTable(
                name: "ChatShareMessages",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false, comment: "主键Id"),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    Ip = table.Column<string>(type: "TEXT", nullable: false),
                    IsDeep = table.Column<bool>(type: "INTEGER", nullable: false),
                    Question = table.Column<string>(type: "TEXT", nullable: false),
                    Title = table.Column<string>(type: "TEXT", nullable: false),
                    UserId = table.Column<string>(type: "TEXT", nullable: true),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false, comment: "仓库Id")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChatShareMessages", x => x.Id);
                },
                comment: "聊天分享消息表");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_ChatShareMessageId",
                table: "ChatShareMessageItems",
                column: "ChatShareMessageId");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_Question",
                table: "ChatShareMessageItems",
                column: "Question");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_WarehouseId",
                table: "ChatShareMessageItems",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessages_WarehouseId",
                table: "ChatShareMessages",
                column: "WarehouseId");
        }
    }
}
