using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.Sqlite.Migrations
{
    /// <inheritdoc />
    public partial class AddMiniMap : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "MiniMaps",
                columns: table => new
                {
                    Id = table.Column<string>(type: "TEXT", nullable: false, comment: "主键Id"),
                    WarehouseId = table.Column<string>(type: "TEXT", nullable: false, comment: "仓库Id"),
                    Value = table.Column<string>(type: "TEXT", nullable: false, comment: "小地图数据"),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MiniMaps", x => x.Id);
                },
                comment: "小地图表");

            migrationBuilder.CreateIndex(
                name: "IX_MiniMaps_WarehouseId",
                table: "MiniMaps",
                column: "WarehouseId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "MiniMaps");
        }
    }
}
