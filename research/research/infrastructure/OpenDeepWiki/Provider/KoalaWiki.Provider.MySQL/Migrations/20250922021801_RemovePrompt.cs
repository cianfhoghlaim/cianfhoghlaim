using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.MySQL.Migrations
{
    /// <inheritdoc />
    public partial class RemovePrompt : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "OptimizedDirectoryStructure",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "Prompt",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "Readme",
                table: "Warehouses");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "OptimizedDirectoryStructure",
                table: "Warehouses",
                type: "longtext",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Prompt",
                table: "Warehouses",
                type: "longtext",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Readme",
                table: "Warehouses",
                type: "longtext",
                nullable: true);
        }
    }
}
