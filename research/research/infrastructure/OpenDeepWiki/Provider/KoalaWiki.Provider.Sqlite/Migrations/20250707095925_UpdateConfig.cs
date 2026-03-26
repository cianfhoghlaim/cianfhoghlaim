using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class UpdateConfig : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Introduction",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Mcps",
                table: "AppConfigs",
                type: "TEXT",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<string>(
                name: "Model",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "Prompt",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "RecommendedQuestions",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Introduction",
                table: "AppConfigs");

            migrationBuilder.DropColumn(
                name: "Mcps",
                table: "AppConfigs");

            migrationBuilder.DropColumn(
                name: "Model",
                table: "AppConfigs");

            migrationBuilder.DropColumn(
                name: "Prompt",
                table: "AppConfigs");

            migrationBuilder.DropColumn(
                name: "RecommendedQuestions",
                table: "AppConfigs");
        }
    }
}
