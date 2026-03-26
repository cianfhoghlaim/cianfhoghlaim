using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddWarehouseSyncRecord : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "EnableSync",
                table: "Warehouses",
                type: "boolean",
                nullable: false,
                defaultValue: false);

            migrationBuilder.CreateTable(
                name: "WarehouseSyncRecords",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "text", nullable: false, comment: "仓库Id"),
                    Status = table.Column<int>(type: "integer", nullable: false, comment: "同步状态"),
                    StartTime = table.Column<DateTime>(type: "timestamp without time zone", nullable: false, comment: "同步开始时间"),
                    EndTime = table.Column<DateTime>(type: "timestamp without time zone", nullable: true, comment: "同步结束时间"),
                    FromVersion = table.Column<string>(type: "text", nullable: true, comment: "同步前的版本"),
                    ToVersion = table.Column<string>(type: "text", nullable: true, comment: "同步后的版本"),
                    ErrorMessage = table.Column<string>(type: "text", nullable: true, comment: "错误信息"),
                    FileCount = table.Column<int>(type: "integer", nullable: false, comment: "同步的文件数量"),
                    UpdatedFileCount = table.Column<int>(type: "integer", nullable: false, comment: "更新的文件数量"),
                    AddedFileCount = table.Column<int>(type: "integer", nullable: false, comment: "新增的文件数量"),
                    DeletedFileCount = table.Column<int>(type: "integer", nullable: false, comment: "删除的文件数量"),
                    Trigger = table.Column<int>(type: "integer", nullable: false, comment: "同步触发方式"),
                    CreatedAt = table.Column<DateTime>(type: "timestamp without time zone", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_WarehouseSyncRecords", x => x.Id);
                    table.ForeignKey(
                        name: "FK_WarehouseSyncRecords_Warehouses_WarehouseId",
                        column: x => x.WarehouseId,
                        principalTable: "Warehouses",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                },
                comment: "仓库同步记录表");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseSyncRecords_CreatedAt",
                table: "WarehouseSyncRecords",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseSyncRecords_StartTime",
                table: "WarehouseSyncRecords",
                column: "StartTime");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseSyncRecords_Status",
                table: "WarehouseSyncRecords",
                column: "Status");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseSyncRecords_Trigger",
                table: "WarehouseSyncRecords",
                column: "Trigger");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseSyncRecords_WarehouseId",
                table: "WarehouseSyncRecords",
                column: "WarehouseId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "WarehouseSyncRecords");

            migrationBuilder.DropColumn(
                name: "EnableSync",
                table: "Warehouses");
        }
    }
}
