using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class Initial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "DocumentCatalogs",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    Name = table.Column<string>(type: "TEXT", nullable: false),
                    Url = table.Column<string>(type: "TEXT", nullable: false),
                    Description = table.Column<string>(type: "TEXT", nullable: false),
                    ParentId = table.Column<string>(type: "TEXT", nullable: true),
                    Order = table.Column<int>(type: "INTEGER", nullable: false),
                    DucumentId = table.Column<string>(type: "TEXT", nullable: false),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCatalogs", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentFileItems",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    Title = table.Column<string>(type: "TEXT", nullable: false),
                    Description = table.Column<string>(type: "TEXT", nullable: false),
                    Content = table.Column<string>(type: "TEXT", nullable: false),
                    CommentCount = table.Column<long>(type: "INTEGER", nullable: false),
                    Size = table.Column<long>(type: "INTEGER", nullable: false),
                    DocumentCatalogId = table.Column<string>(type: "TEXT", nullable: false),
                    RequestToken = table.Column<int>(type: "INTEGER", nullable: false),
                    ResponseToken = table.Column<int>(type: "INTEGER", nullable: false),
                    Metadata = table.Column<string>(type: "TEXT", nullable: false),
                    Extra = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentFileItems", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentOverviews",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    DocumentId = table.Column<string>(type: "TEXT", nullable: false),
                    Content = table.Column<string>(type: "TEXT", nullable: false),
                    Title = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentOverviews", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Documents",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false),
                    LastUpdate = table.Column<DateTime>(type: "TEXT", nullable: false),
                    Description = table.Column<string>(type: "TEXT", nullable: false),
                    LikeCount = table.Column<long>(type: "INTEGER", nullable: false),
                    CommentCount = table.Column<long>(type: "INTEGER", nullable: false),
                    GitPath = table.Column<string>(type: "TEXT", nullable: false),
                    Status = table.Column<byte>(type: "INTEGER", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Documents", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Warehouses",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    OrganizationName = table.Column<string>(type: "TEXT", nullable: false),
                    Name = table.Column<string>(type: "TEXT", nullable: false),
                    Description = table.Column<string>(type: "TEXT", nullable: false),
                    Address = table.Column<string>(type: "TEXT", nullable: false),
                    Type = table.Column<string>(type: "TEXT", nullable: false),
                    Branch = table.Column<string>(type: "TEXT", nullable: false),
                    Status = table.Column<byte>(type: "INTEGER", nullable: false),
                    Error = table.Column<string>(type: "TEXT", nullable: false),
                    Prompt = table.Column<string>(type: "TEXT", nullable: false),
                    Version = table.Column<string>(type: "TEXT", nullable: false),
                    Model = table.Column<string>(type: "TEXT", nullable: false),
                    OpenAIKey = table.Column<string>(type: "TEXT", nullable: false),
                    OpenAIEndpoint = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Warehouses", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentFileItemSources",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    DocumentFileItemId = table.Column<string>(type: "TEXT", nullable: false),
                    Address = table.Column<string>(type: "TEXT", nullable: false),
                    Name = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentFileItemSources", x => x.Id);
                    table.ForeignKey(
                        name: "FK_DocumentFileItemSources_DocumentFileItems_DocumentFileItemId",
                        column: x => x.DocumentFileItemId,
                        principalTable: "DocumentFileItems",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_CreatedAt",
                table: "DocumentCatalogs",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_DucumentId",
                table: "DocumentCatalogs",
                column: "DucumentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_Name",
                table: "DocumentCatalogs",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_ParentId",
                table: "DocumentCatalogs",
                column: "ParentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_WarehouseId",
                table: "DocumentCatalogs",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItems_CreatedAt",
                table: "DocumentFileItems",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItems_DocumentCatalogId",
                table: "DocumentFileItems",
                column: "DocumentCatalogId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItems_Title",
                table: "DocumentFileItems",
                column: "Title");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemSources_CreatedAt",
                table: "DocumentFileItemSources",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemSources_DocumentFileItemId",
                table: "DocumentFileItemSources",
                column: "DocumentFileItemId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentFileItemSources_Name",
                table: "DocumentFileItemSources",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentOverviews_DocumentId",
                table: "DocumentOverviews",
                column: "DocumentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentOverviews_Title",
                table: "DocumentOverviews",
                column: "Title");

            migrationBuilder.CreateIndex(
                name: "IX_Documents_CreatedAt",
                table: "Documents",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Documents_WarehouseId",
                table: "Documents",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Address",
                table: "Warehouses",
                column: "Address");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Branch",
                table: "Warehouses",
                column: "Branch");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_CreatedAt",
                table: "Warehouses",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Name",
                table: "Warehouses",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_OrganizationName",
                table: "Warehouses",
                column: "OrganizationName");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Status",
                table: "Warehouses",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_Warehouses_Type",
                table: "Warehouses",
                column: "Type");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "DocumentCatalogs");

            migrationBuilder.DropTable(
                name: "DocumentFileItemSources");

            migrationBuilder.DropTable(
                name: "DocumentOverviews");

            migrationBuilder.DropTable(
                name: "Documents");

            migrationBuilder.DropTable(
                name: "Warehouses");

            migrationBuilder.DropTable(
                name: "DocumentFileItems");
        }
    }
}
