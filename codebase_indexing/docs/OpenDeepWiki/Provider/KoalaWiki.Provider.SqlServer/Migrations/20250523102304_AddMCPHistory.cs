using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.SqlServer.Migrations
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
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "主键Id"),
                    Question = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Answer = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    UserId = table.Column<string>(type: "nvarchar(450)", nullable: true),
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: true),
                    CostTime = table.Column<int>(type: "int", nullable: false),
                    Ip = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    UserAgent = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
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
