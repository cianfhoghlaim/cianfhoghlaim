// 角色管理页面

import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Search, Plus, MoreHorizontal, Edit, Trash2, Shield, Settings, Copy, Users } from 'lucide-react'
import { roleService, type RoleInfo } from '@/services/role.service'
import { toast } from 'sonner'
import RoleDialog from './RoleDialog'
import RolePermissionDialog from './RolePermissionDialog'
import RoleCopyDialog from './RoleCopyDialog'
import RoleMembersDialog from './RoleMembersDialog'

const RolesPage: React.FC = () => {
  const { t } = useTranslation('admin')
  const [searchQuery, setSearchQuery] = useState('')
  const [roles, setRoles] = useState<RoleInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>(undefined)

  // 对话框状态
  const [roleDialogOpen, setRoleDialogOpen] = useState(false)
  const [permissionDialogOpen, setPermissionDialogOpen] = useState(false)
  const [copyDialogOpen, setCopyDialogOpen] = useState(false)
  const [membersDialogOpen, setMembersDialogOpen] = useState(false)
  const [selectedRole, setSelectedRole] = useState<RoleInfo | null>(null)

  // 加载角色数据
  const loadRoles = async () => {
    try {
      setLoading(true)
      const response = await roleService.getRoleList({
        page: currentPage,
        pageSize: pageSize,
        keyword: searchQuery || undefined,
        isActive: statusFilter
      }) as any
      // 处理嵌套的data结构
      const data = response.data || response
      setRoles(data.items || [])
      setTotal(data.total || 0)
    } catch (error) {
      console.error('Failed to load roles:', error)
      toast.error(t('roles.load_failed'), {
        description: t('roles.load_error')
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRoles()
  }, [currentPage, statusFilter])

  // 搜索防抖
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) {
        loadRoles()
      } else {
        setCurrentPage(1)
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const getStatusBadge = (isActive: boolean) => {
    return (
      <Badge variant={isActive ? 'default' : 'secondary'}>
        {isActive ? t('roles.status.active') : t('roles.status.inactive')}
      </Badge>
    )
  }

  const getRoleTypeBadge = (isSystemRole: boolean) => {
    return isSystemRole ? (
      <Badge variant="outline" className="text-blue-600 border-blue-600">
        {t('roles.type.system')}
      </Badge>
    ) : (
      <Badge variant="outline">
        {t('roles.type.custom')}
      </Badge>
    )
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return t('common.unknown')
    return new Date(dateString).toLocaleDateString()
  }

  const handleDeleteRole = async (id: string, name: string) => {
    if (!confirm(t('roles.confirm_delete', { name }))) return

    try {
      await roleService.deleteRole(id)
      toast.success(t('roles.delete_success'), {
        description: t('roles.role_deleted')
      })
      loadRoles()
    } catch (error: any) {
      toast.error(t('roles.delete_failed'), {
        description: error?.message || t('roles.delete_error')
      })
    }
  }

  // 处理角色操作
  const handleCreateRole = () => {
    setSelectedRole(null)
    setRoleDialogOpen(true)
  }

  const handleEditRole = (role: RoleInfo) => {
    setSelectedRole(role)
    setRoleDialogOpen(true)
  }

  const handleCopyRole = (role: RoleInfo) => {
    setSelectedRole(role)
    setCopyDialogOpen(true)
  }

  const handleManagePermissions = (role: RoleInfo) => {
    setSelectedRole(role)
    setPermissionDialogOpen(true)
  }

  const handleViewMembers = (role: RoleInfo) => {
    setSelectedRole(role)
    setMembersDialogOpen(true)
  }

  const handleRoleDialogSuccess = () => {
    loadRoles()
  }

  const handleToggleStatus = async (role: RoleInfo) => {
    try {
      await roleService.batchUpdateRoleStatus([role.id], !role.isActive)
      toast.success(t('roles.status_update_success'), {
        description: t('roles.status_updated', {
          status: role.isActive ? t('roles.status.inactive') : t('roles.status.active')
        })
      })
      loadRoles()
    } catch (error: any) {
      toast.error(t('roles.status_update_failed'), {
        description: error?.message || t('roles.status_update_error')
      })
    }
  }

  // 计算统计数据
  const stats = {
    total: total,
    active: roles.filter(r => r.isActive).length,
    totalUsers: roles.reduce((sum, role) => sum + (role.userCount || 0), 0)
  }

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('roles.title')}</h1>
          <p className="text-muted-foreground">{t('roles.subtitle')}</p>
        </div>
        <Button onClick={handleCreateRole}>
          <Plus className="mr-2 h-4 w-4" />
          {t('roles.create')}
        </Button>
      </div>

      {/* 角色统计卡片 */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('roles.stats.totalRoles')}</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">{t('roles.stats.totalRolesDescription')}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('roles.stats.activeRoles')}</CardTitle>
            <Shield className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-muted-foreground">{t('roles.stats.activeRolesDescription')}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('roles.stats.assignedUsers')}</CardTitle>
            <Shield className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">{t('roles.stats.assignedUsersDescription')}</p>
          </CardContent>
        </Card>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardHeader>
          <CardTitle>{t('roles.listTitle')}</CardTitle>
          <CardDescription>{t('roles.total_roles', { count: total })}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder={t('roles.search_placeholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center space-x-2">
              <select
                value={statusFilter === undefined ? 'all' : statusFilter ? 'active' : 'inactive'}
                onChange={(e) => {
                  const value = e.target.value
                  setStatusFilter(
                    value === 'all' ? undefined :
                    value === 'active' ? true : false
                  )
                  setCurrentPage(1)
                }}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">{t('roles.filters.all_status')}</option>
                <option value="active">{t('roles.filters.active')}</option>
                <option value="inactive">{t('roles.filters.inactive')}</option>
              </select>
            </div>
          </div>

          {/* 角色表格 */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('roles.table.name')}</TableHead>
                  <TableHead>{t('roles.table.description')}</TableHead>
                  <TableHead className="text-center">{t('roles.table.users_count')}</TableHead>
                  <TableHead className="text-center">{t('roles.table.permissions_count')}</TableHead>
                  <TableHead>{t('roles.table.status')}</TableHead>
                  <TableHead>{t('roles.table.created_at')}</TableHead>
                  <TableHead className="text-right">{t('roles.table.actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      {t('messages.loading')}
                    </TableCell>
                  </TableRow>
                ) : roles.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      {t('messages.no_data')}
                    </TableCell>
                  </TableRow>
                ) : (
                  roles.map((role) => (
                    <TableRow key={role.id}>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{role.name}</span>
                            {getRoleTypeBadge(role.isSystemRole)}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="max-w-xs">
                        <span className="text-sm text-muted-foreground">
                          {role.description || t('roles.no_description')}
                        </span>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="secondary">{role.userCount || 0}</Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">{role.warehousePermissionCount || 0}</Badge>
                      </TableCell>
                      <TableCell>{getStatusBadge(role.isActive)}</TableCell>
                      <TableCell>{formatDate(role.createdAt)}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">{t('roles.open_menu')}</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>{t('roles.actions_menu')}</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleEditRole(role)}>
                              <Edit className="mr-2 h-4 w-4" />
                              {t('roles.edit')}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleManagePermissions(role)}>
                              <Settings className="mr-2 h-4 w-4" />
                              {t('roles.permissions')}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleViewMembers(role)}>
                              <Users className="mr-2 h-4 w-4" />
                              {t('roles.view_members')}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleCopyRole(role)}>
                              <Copy className="mr-2 h-4 w-4" />
                              {t('roles.copy_role')}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleToggleStatus(role)}>
                              <Shield className="mr-2 h-4 w-4" />
                              {role.isActive ? t('roles.disable') : t('roles.enable')}
                            </DropdownMenuItem>
                            {!role.isSystemRole && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  className="text-red-600"
                                  onClick={() => handleDeleteRole(role.id, role.name)}
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  {t('roles.delete')}
                                </DropdownMenuItem>
                              </>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* 分页 */}
          {total > pageSize && (
            <div className="flex items-center justify-end space-x-2 py-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
              >
                {t('roles.pagination.previous')}
              </Button>
              <div className="text-sm text-muted-foreground">
                {t('roles.pagination.page_info', {
                  current: currentPage,
                  total: Math.ceil(total / pageSize)
                })}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => prev + 1)}
                disabled={currentPage >= Math.ceil(total / pageSize)}
              >
                {t('roles.pagination.next')}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 对话框组件 */}
      <RoleDialog
        open={roleDialogOpen}
        onOpenChange={setRoleDialogOpen}
        role={selectedRole}
        onSuccess={handleRoleDialogSuccess}
      />

      <RolePermissionDialog
        open={permissionDialogOpen}
        onOpenChange={setPermissionDialogOpen}
        role={selectedRole}
        onSuccess={loadRoles}
      />

      <RoleCopyDialog
        open={copyDialogOpen}
        onOpenChange={setCopyDialogOpen}
        sourceRole={selectedRole}
        onSuccess={handleRoleDialogSuccess}
      />

      <RoleMembersDialog
        open={membersDialogOpen}
        onOpenChange={setMembersDialogOpen}
        role={selectedRole}
      />
    </div>
  )
}

export default RolesPage