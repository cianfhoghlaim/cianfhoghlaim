using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.PostgreSQL.Migrations
{
    /// <inheritdoc />
    public partial class AddAuth : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "UserInAuths",
                columns: table => new
                {
                    Id = table.Column<string>(type: "text", nullable: false),
                    UserId = table.Column<string>(type: "text", nullable: false),
                    Provider = table.Column<string>(type: "text", nullable: false),
                    AuthId = table.Column<string>(type: "text", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "timestamp without time zone", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserInAuths", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_UserInAuths_AuthId",
                table: "UserInAuths",
                column: "AuthId");

            migrationBuilder.CreateIndex(
                name: "IX_UserInAuths_Provider",
                table: "UserInAuths",
                column: "Provider");

            migrationBuilder.CreateIndex(
                name: "IX_UserInAuths_UserId",
                table: "UserInAuths",
                column: "UserId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "UserInAuths");
        }
    }
}
