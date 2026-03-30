using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class AddStart : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "Forks",
                table: "Warehouses",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "Stars",
                table: "Warehouses",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AlterColumn<string>(
                name: "Prompt",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true,
                comment: "默认提示词",
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "Model",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true,
                comment: "选择模型",
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "Introduction",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true,
                comment: "开场白",
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Forks",
                table: "Warehouses");

            migrationBuilder.DropColumn(
                name: "Stars",
                table: "Warehouses");

            migrationBuilder.AlterColumn<string>(
                name: "Prompt",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true,
                oldComment: "默认提示词");

            migrationBuilder.AlterColumn<string>(
                name: "Model",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true,
                oldComment: "选择模型");

            migrationBuilder.AlterColumn<string>(
                name: "Introduction",
                table: "AppConfigs",
                type: "TEXT",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true,
                oldComment: "开场白");
        }
    }
}
