using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace KoalaWiki.Provider.SqlServer.Migrations
{
    /// <inheritdoc />
    public partial class AddRole : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Role",
                table: "Users");

            migrationBuilder.AlterTable(
                name: "Warehouses",
                comment: "知识仓库表");

            migrationBuilder.AlterTable(
                name: "Users",
                comment: "用户表");

            migrationBuilder.AlterTable(
                name: "UserInAuths",
                comment: "用户认证表");

            migrationBuilder.AlterTable(
                name: "TrainingDatasets",
                comment: "训练数据集表");

            migrationBuilder.AlterTable(
                name: "FineTuningTasks",
                comment: "微调任务表");

            migrationBuilder.AlterTable(
                name: "Documents",
                comment: "文档表");

            migrationBuilder.AlterTable(
                name: "DocumentOverviews",
                comment: "文档概览表");

            migrationBuilder.AlterTable(
                name: "DocumentFileItemSources",
                comment: "文档文件项来源表");

            migrationBuilder.AlterTable(
                name: "DocumentFileItems",
                comment: "文档文件项表");

            migrationBuilder.AlterTable(
                name: "DocumentCommitRecords",
                comment: "文档提交记录表");

            migrationBuilder.AlterTable(
                name: "DocumentCatalogs",
                comment: "文档目录表");

            migrationBuilder.AlterTable(
                name: "ChatShareMessages",
                comment: "聊天分享消息表");

            migrationBuilder.AlterTable(
                name: "ChatShareMessageItems",
                comment: "聊天分享消息项表");

            migrationBuilder.AlterColumn<string>(
                name: "Type",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: true,
                comment: "仓库类型",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AlterColumn<byte>(
                name: "Status",
                table: "Warehouses",
                type: "tinyint",
                nullable: false,
                comment: "仓库状态",
                oldClrType: typeof(byte),
                oldType: "tinyint");

            migrationBuilder.AlterColumn<string>(
                name: "OrganizationName",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                comment: "组织名称",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库名称",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "Warehouses",
                type: "nvarchar(max)",
                nullable: false,
                comment: "仓库描述",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "Warehouses",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Branch",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: true,
                comment: "分支",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "Address",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库地址",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Password",
                table: "Users",
                type: "nvarchar(max)",
                nullable: false,
                comment: "密码",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "Users",
                type: "nvarchar(450)",
                nullable: false,
                comment: "用户名",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "LastLoginAt",
                table: "Users",
                type: "datetime2",
                nullable: true,
                comment: "最后登录时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "Email",
                table: "Users",
                type: "nvarchar(450)",
                nullable: false,
                comment: "邮箱",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "Users",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "Users",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                comment: "用户Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Provider",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                comment: "认证提供方",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "AuthId",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                comment: "认证Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "TrainingDatasets",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "TrainingDatasets",
                type: "nvarchar(450)",
                nullable: false,
                comment: "数据集名称",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "TrainingDatasets",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "TrainingDatasets",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "MCPHistories",
                type: "nvarchar(450)",
                nullable: true,
                comment: "仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "MCPHistories",
                type: "nvarchar(450)",
                nullable: true,
                comment: "用户Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "MCPHistories",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                comment: "用户Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "TrainingDatasetId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                comment: "训练数据集Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<int>(
                name: "Status",
                table: "FineTuningTasks",
                type: "int",
                nullable: false,
                comment: "任务状态",
                oldClrType: typeof(int),
                oldType: "int");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                comment: "微调任务名称",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentCatalogId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                comment: "目录Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "FineTuningTasks",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "Documents",
                type: "nvarchar(450)",
                nullable: false,
                comment: "所属仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "Documents",
                type: "nvarchar(max)",
                nullable: false,
                comment: "文档描述",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "Documents",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "Documents",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Title",
                table: "DocumentOverviews",
                type: "nvarchar(450)",
                nullable: false,
                comment: "文档标题",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentId",
                table: "DocumentOverviews",
                type: "nvarchar(450)",
                nullable: false,
                comment: "文档Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentOverviews",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "DocumentFileItemSources",
                type: "nvarchar(450)",
                nullable: false,
                comment: "来源名称",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentFileItemId",
                table: "DocumentFileItemSources",
                type: "nvarchar(450)",
                nullable: false,
                comment: "文件项Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "DocumentFileItemSources",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentFileItemSources",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Title",
                table: "DocumentFileItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "文件标题",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Metadata",
                table: "DocumentFileItems",
                type: "nvarchar(max)",
                nullable: false,
                comment: "元数据",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "Extra",
                table: "DocumentFileItems",
                type: "nvarchar(max)",
                nullable: false,
                comment: "扩展信息",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentCatalogId",
                table: "DocumentFileItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "目录Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "DocumentFileItems",
                type: "nvarchar(max)",
                nullable: false,
                comment: "文件描述",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "DocumentFileItems",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentFileItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "DocumentCommitRecords",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "CommitMessage",
                table: "DocumentCommitRecords",
                type: "nvarchar(max)",
                nullable: false,
                comment: "提交信息",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "CommitId",
                table: "DocumentCommitRecords",
                type: "nvarchar(450)",
                nullable: false,
                comment: "提交Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Author",
                table: "DocumentCommitRecords",
                type: "nvarchar(max)",
                nullable: false,
                comment: "作者",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentCommitRecords",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                comment: "所属仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "ParentId",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: true,
                comment: "父级目录Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                comment: "目录名称",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<bool>(
                name: "IsDeleted",
                table: "DocumentCatalogs",
                type: "bit",
                nullable: false,
                comment: "是否已删除",
                oldClrType: typeof(bool),
                oldType: "bit");

            migrationBuilder.AlterColumn<string>(
                name: "DucumentId",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                comment: "文档Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "DocumentCatalogs",
                type: "nvarchar(max)",
                nullable: false,
                comment: "目录描述",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "DependentFile",
                table: "DocumentCatalogs",
                type: "nvarchar(max)",
                nullable: false,
                comment: "依赖文件",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "DocumentCatalogs",
                type: "datetime2",
                nullable: false,
                comment: "创建时间",
                oldClrType: typeof(DateTime),
                oldType: "datetime2");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "ChatShareMessages",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "ChatShareMessages",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "仓库Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Question",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "问题内容",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Files",
                table: "ChatShareMessageItems",
                type: "nvarchar(max)",
                nullable: false,
                comment: "相关文件",
                oldClrType: typeof(string),
                oldType: "nvarchar(max)");

            migrationBuilder.AlterColumn<string>(
                name: "ChatShareMessageId",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "聊天分享消息Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                comment: "主键Id",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.CreateTable(
                name: "Roles",
                columns: table => new
                {
                    Id = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "主键Id"),
                    Name = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "角色名称"),
                    Description = table.Column<string>(type: "nvarchar(max)", nullable: false, comment: "角色描述"),
                    IsActive = table.Column<bool>(type: "bit", nullable: false),
                    UpdatedAt = table.Column<DateTime>(type: "datetime2", nullable: false),
                    IsSystemRole = table.Column<bool>(type: "bit", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "datetime2", nullable: false, comment: "创建时间")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Roles", x => x.Id);
                },
                comment: "角色表");

            migrationBuilder.CreateTable(
                name: "UserInRoles",
                columns: table => new
                {
                    UserId = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "用户Id"),
                    RoleId = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "角色Id")
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserInRoles", x => new { x.UserId, x.RoleId });
                },
                comment: "用户角色关联表");

            migrationBuilder.CreateTable(
                name: "WarehouseInRoles",
                columns: table => new
                {
                    WarehouseId = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "仓库Id"),
                    RoleId = table.Column<string>(type: "nvarchar(450)", nullable: false, comment: "角色Id"),
                    IsReadOnly = table.Column<bool>(type: "bit", nullable: false),
                    IsWrite = table.Column<bool>(type: "bit", nullable: false),
                    IsDelete = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_WarehouseInRoles", x => new { x.WarehouseId, x.RoleId });
                },
                comment: "仓库角色关联表");

            migrationBuilder.CreateIndex(
                name: "IX_Roles_CreatedAt",
                table: "Roles",
                column: "CreatedAt");

            migrationBuilder.CreateIndex(
                name: "IX_Roles_Name",
                table: "Roles",
                column: "Name");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseInRoles_RoleId",
                table: "WarehouseInRoles",
                column: "RoleId");

            migrationBuilder.CreateIndex(
                name: "IX_WarehouseInRoles_WarehouseId",
                table: "WarehouseInRoles",
                column: "WarehouseId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Roles");

            migrationBuilder.DropTable(
                name: "UserInRoles");

            migrationBuilder.DropTable(
                name: "WarehouseInRoles");

            migrationBuilder.AlterTable(
                name: "Warehouses",
                oldComment: "知识仓库表");

            migrationBuilder.AlterTable(
                name: "Users",
                oldComment: "用户表");

            migrationBuilder.AlterTable(
                name: "UserInAuths",
                oldComment: "用户认证表");

            migrationBuilder.AlterTable(
                name: "TrainingDatasets",
                oldComment: "训练数据集表");

            migrationBuilder.AlterTable(
                name: "FineTuningTasks",
                oldComment: "微调任务表");

            migrationBuilder.AlterTable(
                name: "Documents",
                oldComment: "文档表");

            migrationBuilder.AlterTable(
                name: "DocumentOverviews",
                oldComment: "文档概览表");

            migrationBuilder.AlterTable(
                name: "DocumentFileItemSources",
                oldComment: "文档文件项来源表");

            migrationBuilder.AlterTable(
                name: "DocumentFileItems",
                oldComment: "文档文件项表");

            migrationBuilder.AlterTable(
                name: "DocumentCommitRecords",
                oldComment: "文档提交记录表");

            migrationBuilder.AlterTable(
                name: "DocumentCatalogs",
                oldComment: "文档目录表");

            migrationBuilder.AlterTable(
                name: "ChatShareMessages",
                oldComment: "聊天分享消息表");

            migrationBuilder.AlterTable(
                name: "ChatShareMessageItems",
                oldComment: "聊天分享消息项表");

            migrationBuilder.AlterColumn<string>(
                name: "Type",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true,
                oldComment: "仓库类型");

            migrationBuilder.AlterColumn<byte>(
                name: "Status",
                table: "Warehouses",
                type: "tinyint",
                nullable: false,
                oldClrType: typeof(byte),
                oldType: "tinyint",
                oldComment: "仓库状态");

            migrationBuilder.AlterColumn<string>(
                name: "OrganizationName",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "组织名称");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库名称");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "Warehouses",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "仓库描述");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "Warehouses",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Branch",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true,
                oldComment: "分支");

            migrationBuilder.AlterColumn<string>(
                name: "Address",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库地址");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "Warehouses",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "Password",
                table: "Users",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "密码");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "Users",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "用户名");

            migrationBuilder.AlterColumn<DateTime>(
                name: "LastLoginAt",
                table: "Users",
                type: "datetime2",
                nullable: true,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldNullable: true,
                oldComment: "最后登录时间");

            migrationBuilder.AlterColumn<string>(
                name: "Email",
                table: "Users",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "邮箱");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "Users",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "Users",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AddColumn<string>(
                name: "Role",
                table: "Users",
                type: "nvarchar(max)",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "用户Id");

            migrationBuilder.AlterColumn<string>(
                name: "Provider",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "认证提供方");

            migrationBuilder.AlterColumn<string>(
                name: "AuthId",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "认证Id");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "UserInAuths",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "TrainingDatasets",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "TrainingDatasets",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "数据集名称");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "TrainingDatasets",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "TrainingDatasets",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "MCPHistories",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true,
                oldComment: "仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "MCPHistories",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true,
                oldComment: "用户Id");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "MCPHistories",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "UserId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "用户Id");

            migrationBuilder.AlterColumn<string>(
                name: "TrainingDatasetId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "训练数据集Id");

            migrationBuilder.AlterColumn<int>(
                name: "Status",
                table: "FineTuningTasks",
                type: "int",
                nullable: false,
                oldClrType: typeof(int),
                oldType: "int",
                oldComment: "任务状态");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "微调任务名称");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentCatalogId",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "目录Id");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "FineTuningTasks",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "FineTuningTasks",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "Documents",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "所属仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "Documents",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "文档描述");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "Documents",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "Documents",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "Title",
                table: "DocumentOverviews",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "文档标题");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentId",
                table: "DocumentOverviews",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "文档Id");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentOverviews",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "DocumentFileItemSources",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "来源名称");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentFileItemId",
                table: "DocumentFileItemSources",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "文件项Id");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "DocumentFileItemSources",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentFileItemSources",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "Title",
                table: "DocumentFileItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "文件标题");

            migrationBuilder.AlterColumn<string>(
                name: "Metadata",
                table: "DocumentFileItems",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "元数据");

            migrationBuilder.AlterColumn<string>(
                name: "Extra",
                table: "DocumentFileItems",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "扩展信息");

            migrationBuilder.AlterColumn<string>(
                name: "DocumentCatalogId",
                table: "DocumentFileItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "目录Id");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "DocumentFileItems",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "文件描述");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "DocumentFileItems",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentFileItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "DocumentCommitRecords",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "CommitMessage",
                table: "DocumentCommitRecords",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "提交信息");

            migrationBuilder.AlterColumn<string>(
                name: "CommitId",
                table: "DocumentCommitRecords",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "提交Id");

            migrationBuilder.AlterColumn<string>(
                name: "Author",
                table: "DocumentCommitRecords",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "作者");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentCommitRecords",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "所属仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "ParentId",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true,
                oldComment: "父级目录Id");

            migrationBuilder.AlterColumn<string>(
                name: "Name",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "目录名称");

            migrationBuilder.AlterColumn<bool>(
                name: "IsDeleted",
                table: "DocumentCatalogs",
                type: "bit",
                nullable: false,
                oldClrType: typeof(bool),
                oldType: "bit",
                oldComment: "是否已删除");

            migrationBuilder.AlterColumn<string>(
                name: "DucumentId",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "文档Id");

            migrationBuilder.AlterColumn<string>(
                name: "Description",
                table: "DocumentCatalogs",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "目录描述");

            migrationBuilder.AlterColumn<string>(
                name: "DependentFile",
                table: "DocumentCatalogs",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "依赖文件");

            migrationBuilder.AlterColumn<DateTime>(
                name: "CreatedAt",
                table: "DocumentCatalogs",
                type: "datetime2",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "datetime2",
                oldComment: "创建时间");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "DocumentCatalogs",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "ChatShareMessages",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "ChatShareMessages",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");

            migrationBuilder.AlterColumn<string>(
                name: "WarehouseId",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "仓库Id");

            migrationBuilder.AlterColumn<string>(
                name: "Question",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "问题内容");

            migrationBuilder.AlterColumn<string>(
                name: "Files",
                table: "ChatShareMessageItems",
                type: "nvarchar(max)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(max)",
                oldComment: "相关文件");

            migrationBuilder.AlterColumn<string>(
                name: "ChatShareMessageId",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "聊天分享消息Id");

            migrationBuilder.AlterColumn<string>(
                name: "Id",
                table: "ChatShareMessageItems",
                type: "nvarchar(450)",
                nullable: false,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldComment: "主键Id");
        }
    }
}
