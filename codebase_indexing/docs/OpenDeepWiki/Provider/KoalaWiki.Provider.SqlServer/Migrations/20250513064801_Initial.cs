using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.SqlServer.Migrations
{
    /// <inheritdoc />
    public partial class Initial : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "ChatShareMessageItems",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    ChatShareMessageId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Question = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Answer = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Think = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    PromptToken = table.Column<int>(type: "int", nullable: false),
                    CompletionToken = table.Column<int>(type: "int", nullable: false),
                    TotalTime = table.Column<int>(type: "int", nullable: false),
                    Files = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChatShareMessageItems", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "ChatShareMessages",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    IsDeep = table.Column<bool>(type: "bit", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Ip = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Question = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChatShareMessages", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentCatalogs",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Url = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    ParentId = table.Column<string>(type: "nvarchar(450)", nullable: true),
                    Order = table.Column<int>(type: "int", nullable: false),
                    DucumentId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    IsCompleted = table.Column<bool>(type: "bit", nullable: false),
                    Prompt = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    IsDeleted = table.Column<bool>(type: "bit", nullable: false),
                    DeletedTime = table.Column<DateTime>(type: "datetime2", nullable: true),
                    DependentFile = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCatalogs", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentCommitRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CommitId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CommitMessage = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Author = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    LastUpdate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentCommitRecords", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentFileItems",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Content = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CommentCount = table.Column<long>(type: "bigint", nullable: false),
                    Size = table.Column<long>(type: "bigint", nullable: false),
                    DocumentCatalogId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    RequestToken = table.Column<int>(type: "int", nullable: false),
                    ResponseToken = table.Column<int>(type: "int", nullable: false),
                    IsEmbedded = table.Column<bool>(type: "bit", nullable: false),
                    Metadata = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Extra = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentFileItems", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentOverviews",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    DocumentId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Content = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Title = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_DocumentOverviews", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Documents",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    LastUpdate = table.Column<DateTime>(type: "datetime2", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    LikeCount = table.Column<long>(type: "bigint", nullable: false),
                    CommentCount = table.Column<long>(type: "bigint", nullable: false),
                    GitPath = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Status = table.Column<byte>(type: "tinyint", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Documents", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "Warehouses",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    OrganizationName = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Address = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    GitUserName = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    GitPassword = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Email = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Type = table.Column<string>(type: "nvarchar(450)", nullable: true),
                    Branch = table.Column<string>(type: "nvarchar(450)", nullable: true),
                    Status = table.Column<byte>(type: "tinyint", nullable: false),
                    Error = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Prompt = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Version = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    IsEmbedded = table.Column<bool>(type: "bit", nullable: false),
                    IsRecommended = table.Column<bool>(type: "bit", nullable: false),
                    OptimizedDirectoryStructure = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    Readme = table.Column<string>(type: "nvarchar(max)", nullable: true),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Warehouses", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "DocumentFileItemSources",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    DocumentFileItemId = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    Address = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    Name = table.Column<string>(type: "nvarchar(450)", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false)
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
                name: "IX_ChatShareMessageItems_ChatShareMessageId",
                table: "ChatShareMessageItems",
                column: "ChatShareMessageId");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_Question",
                table: "ChatShareMessageItems",
                column: "Question");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessageItems_WarehouseId",
                table: "ChatShareMessageItems",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_ChatShareMessages_WarehouseId",
                table: "ChatShareMessages",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_CreatedAt",
                table: "DocumentCatalogs",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_DucumentId",
                table: "DocumentCatalogs",
                column: "DucumentId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCatalogs_IsDeleted",
                table: "DocumentCatalogs",
                column: "IsDeleted");

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
                name: "IX_DocumentCommitRecords_CommitId",
                table: "DocumentCommitRecords",
                column: "CommitId");

            migrationBuilder.CreateIndex(
                name: "IX_DocumentCommitRecords_WarehouseId",
                table: "DocumentCommitRecords",
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
                name: "ChatShareMessageItems");

            migrationBuilder.DropTable(
                name: "ChatShareMessages");

            migrationBuilder.DropTable(
                name: "DocumentCatalogs");

            migrationBuilder.DropTable(
                name: "DocumentCommitRecords");

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
