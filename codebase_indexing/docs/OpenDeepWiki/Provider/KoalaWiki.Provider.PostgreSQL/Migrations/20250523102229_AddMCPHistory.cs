using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddMCPHistory : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "MCPHistories",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false, comment: "主键Id"),
                    Question = table.Column<string>(type: "text", nullable: false),
                    Answer = table.Column<string>(type: "text", nullable: false),
                    UserId = table.Column<string>(type: "text", nullable: true),
                    WarehouseId = table.Column<string>(type: "text", nullable: true),
                    CostTime = table.Column<int>(type: "integer", nullable: false),
                    Ip = table.Column<string>(type: "text", nullable: false),
                    UserAgent = table.Column<string>(type: "text", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MCPHistories", x => x.Id);
                },
                comment: "MCP历史记录");

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
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "MCPHistories");
        }
    }
}
