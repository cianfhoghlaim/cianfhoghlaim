using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class AddFineTuning : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "FineTuningTasks",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false),
                    TrainingDatasetId = table.Column<string>(type: "TEXT", nullable: false),
                    DocumentCatalogId = table.Column<string>(type: "TEXT", nullable: false),
                    Name = table.Column<string>(type: "TEXT", nullable: false),
                    UserId = table.Column<string>(type: "TEXT", nullable: false),
                    Description = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    StartedAt = table.Column<DateTime>(type: "TEXT", nullable: true),
                    CompletedAt = table.Column<DateTime>(type: "TEXT", nullable: true),
                    Status = table.Column<int>(type: "INTEGER", nullable: false),
                    Dataset = table.Column<string>(type: "TEXT", nullable: false),
                    Error = table.Column<string>(type: "TEXT", nullable: true),
                    OriginalDataset = table.Column<string>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_FineTuningTasks", x => x.Id);
                    table.ForeignKey(
                        name: "FK_FineTuningTasks_DocumentCatalogs_DocumentCatalogId",
                        column: x => x.DocumentCatalogId,
                        principalTable: "DocumentCatalogs",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "TrainingDatasets",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false),
                    UserId = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    Status = table.Column<int>(type: "INTEGER", nullable: false),
                    Name = table.Column<string>(type: "TEXT", nullable: false),
                    Endpoint = table.Column<string>(type: "TEXT", nullable: false),
                    ApiKey = table.Column<string>(type: "TEXT", nullable: false),
                    Prompt = table.Column<string>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TrainingDatasets", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_CreatedAt",
                table: "FineTuningTasks",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_DocumentCatalogId",
                table: "FineTuningTasks",
                column: "DocumentCatalogId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_Name",
                table: "FineTuningTasks",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_Status",
                table: "FineTuningTasks",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_TrainingDatasetId",
                table: "FineTuningTasks",
                column: "TrainingDatasetId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_UserId",
                table: "FineTuningTasks",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_FineTuningTasks_WarehouseId",
                table: "FineTuningTasks",
                column: "WarehouseId");

            migrationBuilder.CreateIndex(
                name: "IX_TrainingDatasets_CreatedAt",
                table: "TrainingDatasets",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_TrainingDatasets_Name",
                table: "TrainingDatasets",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_TrainingDatasets_WarehouseId",
                table: "TrainingDatasets",
                column: "WarehouseId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "FineTuningTasks");

            migrationBuilder.DropTable(
                name: "TrainingDatasets");
        }
    }
}
