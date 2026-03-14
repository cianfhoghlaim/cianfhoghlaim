using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddDeletedTime : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<DateTime>(
                name: "DeletedTime",
                table: "DocumentCatalogs",
                type: "timestamp without time zone",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsDeleted",
                table: "DocumentCatalogs",
                type: "boolean",
                nullable: false,
                defaultValue: false);

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_IsDeleted",
                table: "DocumentCatalogs",
                column: "IsDeleted");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_DocumentCatalogs_IsDeleted",
                table: "DocumentCatalogs");

            migrationBuilder.DropColumn(
                name: "DeletedTime",
                table: "DocumentCatalogs");

            migrationBuilder.DropColumn(
                name: "IsDeleted",
                table: "DocumentCatalogs");
        }
    }
}
