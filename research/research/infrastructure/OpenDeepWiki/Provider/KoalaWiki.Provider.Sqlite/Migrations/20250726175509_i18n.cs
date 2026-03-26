using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class i18n : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "DocumentCatalogI18ns",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false, comment: "主键Id"),
                    DocumentCatalogId = table.Column<string>(type: "TEXT", nullable: false, comment: "文档目录Id"),
                    LanguageCode = table.Column<string>(type: "TEXT", maxLength: 10, nullable: false, comment: "语言代码"),
                    Name = table.Column<string>(type: "TEXT", nullable: false, comment: "多语言目录名称"),
                    Description = table.Column<string>(type: "TEXT", nullable: false, comment: "多语言目录描述"),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false, comment: "创建时间"),
                    UpdatedAt = table.Column<DateTime>(type: "TEXT", nullable: false, comment: "更新时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCatalogI18ns", x => x.Id);
                    table.ForeignKey(
                        name: "FK_DocumentCatalogI18ns_DocumentCatalogs_DocumentCatalogId",
                        column: x => x.DocumentCatalogId,
                        principalTable: "DocumentCatalogs",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                },
                comment: "文档目录多语言表");

            migrationBuilder.CreateTable(
                name: "DocumentFileItemI18ns",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false, comment: "主键Id"),
                    DocumentFileItemId = table.Column<string>(type: "TEXT", nullable: false, comment: "文档文件Id"),
                    LanguageCode = table.Column<string>(type: "TEXT", maxLength: 10, nullable: false, comment: "语言代码"),
                    Title = table.Column<string>(type: "TEXT", nullable: false, comment: "多语言标题"),
                    Description = table.Column<string>(type: "TEXT", nullable: false, comment: "多语言描述"),
                    Content = table.Column<string>(type: "TEXT", nullable: false, comment: "多语言内容"),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false, comment: "创建时间"),
                    UpdatedAt = table.Column<DateTime>(type: "TEXT", nullable: false, comment: "更新时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentFileItemI18ns", x => x.Id);
                    table.ForeignKey(
                        name: "FK_DocumentFileItemI18ns_DocumentFileItems_DocumentFileItemId",
                        column: x => x.DocumentFileItemId,
                        principalTable: "DocumentFileItems",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                },
                comment: "文档文件多语言表");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogI18ns_DocumentCatalogId",
                table: "DocumentCatalogI18ns",
                column: "DocumentCatalogId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogI18ns_DocumentCatalogId_LanguageCode",
                table: "DocumentCatalogI18ns",
                columns: new[] { "DocumentCatalogId", "LanguageCode" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogI18ns_LanguageCode",
                table: "DocumentCatalogI18ns",
                column: "LanguageCode");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemI18ns_DocumentFileItemId",
                table: "DocumentFileItemI18ns",
                column: "DocumentFileItemId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemI18ns_DocumentFileItemId_LanguageCode",
                table: "DocumentFileItemI18ns",
                columns: new[] { "DocumentFileItemId", "LanguageCode" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemI18ns_LanguageCode",
                table: "DocumentFileItemI18ns",
                column: "LanguageCode");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "DocumentCatalogI18ns");

            migrationBuilder.DropTable(
                name: "DocumentFileItemI18ns");
        }
    }
}
