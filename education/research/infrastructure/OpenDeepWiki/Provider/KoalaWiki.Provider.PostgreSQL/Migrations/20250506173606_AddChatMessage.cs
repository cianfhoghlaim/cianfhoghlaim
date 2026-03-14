using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddChatMessage : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "ChatShareMessageItems",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    ChatShareMessageId = table.Column<string>(type: "text", nullable: false),
                    WarehouseId = table.Column<string>(type: "text", nullable: false),
                    Question = table.Column<string>(type: "text", nullable: false),
                    Answer = table.Column<string>(type: "text", nullable: false),
                    Think = table.Column<string>(type: "text", nullable: false),
                    PromptToken = table.Column<int>(type: "integer", nullable: false),
                    CompletionToken = table.Column<int>(type: "integer", nullable: false),
                    TotalTime = table.Column<int>(type: "integer", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChatShareMessageItems", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "ChatShareMessages",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    WarehouseId = table.Column<string>(type: "text", nullable: false),
                    IsDeep = table.Column<bool>(type: "boolean", nullable: false),
                    Title = table.Column<string>(type: "text", nullable: false),
                    Ip = table.Column<string>(type: "text", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChatShareMessages", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_ChatShareMessageId",
                table: "ChatShareMessageItems",
                column: "ChatShareMessageId");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_Question",
                table: "ChatShareMessageItems",
                column: "Question");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessages_WarehouseId",
                table: "ChatShareMessages",
                column: "WarehouseId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ChatShareMessageItems");

            migrationBuilder.DropTable(
                name: "ChatShareMessages");
        }
    }
}
