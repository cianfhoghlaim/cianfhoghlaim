using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class AddDocumentCommitRecords : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "DocumentCommitRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false),
                    CommitId = table.Column<string>(type: "TEXT", nullable: false),
                    CommitMessage = table.Column<string>(type: "TEXT", nullable: false),
                    Author = table.Column<string>(type: "TEXT", nullable: false),
                    LastUpdate = table.Column<DateTime>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCommitRecords", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCommitRecords_CommitId",
                table: "DocumentCommitRecords",
                column: "CommitId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCommitRecords_WarehouseId",
                table: "DocumentCommitRecords",
                column: "WarehouseId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "DocumentCommitRecords");
        }
    }
}
