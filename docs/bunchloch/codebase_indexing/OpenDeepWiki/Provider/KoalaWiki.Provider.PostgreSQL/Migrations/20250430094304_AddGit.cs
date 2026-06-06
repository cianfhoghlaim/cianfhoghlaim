using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddGit : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "GitPassword",
                table: "Warehouses",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "GitUserName",
                table: "Warehouses",
                type: "text",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "GitPassword",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "GitUserName",
                table: "Warehouses");
        }
    }
}
