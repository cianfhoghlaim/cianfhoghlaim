using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddEmbedded : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Model",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "OpenAIEndpoint",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "OpenAIKey",
                table: "Warehouses");

            migrationBuilder.AddColumn<bool>(
                name: "IsEmbedded",
                table: "Warehouses",
                type: "boolean",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<bool>(
                name: "IsEmbedded",
                table: "DocumentFileItems",
                type: "boolean",
                nullable: false,
                defaultValue: false);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "IsEmbedded",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "IsEmbedded",
                table: "DocumentFileItems");

            migrationBuilder.AddColumn<string>(
                name: "Model",
                table: "Warehouses",
                type: "text",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "OpenAIEndpoint",
                table: "Warehouses",
                type: "text",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "OpenAIKey",
                table: "Warehouses",
                type: "text",
                nullable: false,
                defaultValue: "");
        }
    }
}
