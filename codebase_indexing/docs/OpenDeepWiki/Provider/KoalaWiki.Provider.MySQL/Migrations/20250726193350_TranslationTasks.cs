using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.MySQL.Migrations
{
    /// <inheritdoc />
    public partial class TranslationTasks : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "TranslationTasks",
                columns: table => new
                {
                    Id = table.Column<string>(type: "varchar(255)", nullable: false),
                    WarehouseId = table.Column<string>(type: "longtext", nullable: false),
                    TargetLanguage = table.Column<string>(type: "longtext", nullable: false),
                    SourceLanguage = table.Column<string>(type: "longtext", nullable: false),
                    Status = table.Column<int>(type: "int", nullable: false),
                    TaskType = table.Column<int>(type: "int", nullable: false),
                    TargetId = table.Column<string>(type: "longtext", nullable: false),
                    ErrorMessage = table.Column<string>(type: "longtext", nullable: true),
                    CatalogsTranslated = table.Column<int>(type: "int", nullable: false),
                    FilesTranslated = table.Column<int>(type: "int", nullable: false),
                    TotalCatalogs = table.Column<int>(type: "int", nullable: false),
                    TotalFiles = table.Column<int>(type: "int", nullable: false),
                    StartedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false),
                    CompletedAt = table.Column<DateTime>(type: "datetime(6)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime(6)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TranslationTasks", x => x.Id);
                })
                .Annotation("MySQL:Charset", "utf8mb4");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "TranslationTasks");
        }
    }
}
