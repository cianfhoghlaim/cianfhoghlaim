// 用户管理页面

import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Search, Plus, MoreHorizontal, Edit, Trash2, UserPlus, Filter, Key } from 'lucide-react'
import { userService, roleService, type UserInfo, type RoleInfo } from '@/services/admin.service'
import { toast } from 'sonner'
import UserDialog from '@/components/admin/UserDialog'
import UserRoleDialog from '@/components/admin/UserRoleDialog'
import UserPasswordDialog from '@/components/admin/UserPasswordDialog'
import BatchDeleteDialog from '@/components/admin/BatchDeleteDialog'

const UsersPage: React.FC = () => {
  const { t } = useTranslation('admin')
  const [searchQuery, setSearchQuery] = useState('')
  const [users, setUsers] = useState<UserInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(10)
  const [selectedUserIds, setSelectedUserIds] = useState<string[]>([])
  const [roleFilter, setRoleFilter] = useState<string>('all')
  const [roles, setRoles] = useState<RoleInfo[]>([])

  // 对话框状态
  const [userDialogOpen, setUserDialogOpen] = useState(false)
  const [userRoleDialogOpen, setUserRoleDialogOpen] = useState(false)
  const [userPasswordDialogOpen, setUserPasswordDialogOpen] = useState(false)
  const [batchDeleteDialogOpen, setBatchDeleteDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<UserInfo | null>(null)

  // 加载用户数据
  const loadUsers = async () => {
    try {
      setLoading(true)
      const response = await userService.getUserList(currentPage, pageSize, searchQuery || undefined)as any
      // 处理嵌套的data结构
      const data = response.data || response
      setUsers(data.items || [])
      setTotal(data.total || 0)
    } catch (error) {
      console.error('Failed to load users:', error)
      toast.error(t('users.load_failed'), {
        description: t('users.load_error')
      })
    } finally {
      setLoading(false)
    }
  }

  // 加载角色列表
  const loadRoles = async () => {
    try {
      const response = await roleService.getAllRoles() as any
      // 确保 response 是数组
      const rolesData = Array.isArray(response) ? response : (response?.data || [])
      setRoles(rolesData)
    } catch (error) {
      console.error('Failed to load roles:', error)
    }
  }

  useEffect(() => {
    loadUsers()
    loadRoles()
  }, [currentPage])

  // 搜索防抖
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) {
        loadUsers()
      } else {
        setCurrentPage(1)
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const getRoleBadge = (role?: string) => {
    if (!role) return null

    const colors: Record<string, string> = {
      admin: 'bg-red-100 text-red-800',
      moderator: 'bg-blue-100 text-blue-800',
      user: 'bg-green-100 text-green-800'
    }

    const roles = role.split(',').filter(Boolean)

    return (
      <div className="flex gap-1">
        {roles.map((r, index) => (
          <Badge key={index} className={colors[r.trim()] || 'bg-gray-100 text-gray-800'}>
            {r.trim()}
          </Badge>
        ))}
      </div>
    )
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return t('common.unknown')
    return new Date(dateString).toLocaleDateString()
  }

  const handleDeleteUser = async (id: string) => {
    if (!confirm(t('users.confirm_delete'))) return

    try {
      await userService.deleteUser(id)
      toast.success(t('users.delete_success'), {
        description: t('users.user_deleted')
      })
      loadUsers()
      setSelectedUserIds(prev => prev.filter(userId => userId !== id))
    } catch (error) {
      toast.error(t('users.delete_failed'), {
        description: t('users.delete_error')
      })
    }
  }

  // 处理全选
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedUserIds(users.map(user => user.id))
    } else {
      setSelectedUserIds([])
    }
  }

  // 处理单个用户选择
  const handleSelectUser = (userId: string, checked: boolean) => {
    setSelectedUserIds(prev => {
      if (checked) {
        return [...prev, userId]
      } else {
        return prev.filter(id => id !== userId)
      }
    })
  }

  // 处理创建用户
  const handleCreateUser = () => {
    setSelectedUser(null)
    setUserDialogOpen(true)
  }

  // 处理编辑用户
  const handleEditUser = (user: UserInfo) => {
    setSelectedUser(user)
    setUserDialogOpen(true)
  }

  // 处理角色分配
  const handleAssignRoles = (user: UserInfo) => {
    setSelectedUser(user)
    setUserRoleDialogOpen(true)
  }

  // 处理密码重置
  const handleResetPassword = (user: UserInfo) => {
    setSelectedUser(user)
    setUserPasswordDialogOpen(true)
  }

  // 处理批量删除
  const handleBatchDelete = () => {
    if (selectedUserIds.length === 0) {
      toast.error(t('users.select_users_to_delete'))
      return
    }
    setBatchDeleteDialogOpen(true)
  }

  // 获取选中的用户列表
  const getSelectedUsers = () => {
    return users.filter(user => selectedUserIds.includes(user.id))
  }

  // 重置选择
  const resetSelection = () => {
    setSelectedUserIds([])
  }

  // 过滤用户
  const filteredUsers = users.filter(user => {
    if (roleFilter && roleFilter !== 'all') {
      // 如果用户没有角色（空字符串或null/undefined），则不匹配任何角色过滤
      if (!user.role || user.role.trim() === '') {
        return false
      }
      // 检查角色字符串中是否包含所选角色（支持逗号分隔的多个角色）
      const userRoles = user.role.split(',').map(r => r.trim()).filter(Boolean)
      return userRoles.includes(roleFilter)
    }
    return true
  })

  return (
    <div className="space-y-6">
      {/* 页面标题和操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('users.title')}</h1>
          <p className="text-muted-foreground">{t('users.subtitle')}</p>
        </div>
        <div className="flex space-x-2">
          {selectedUserIds.length > 0 && (
            <Button
              variant="destructive"
              onClick={handleBatchDelete}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {t('users.delete_selected', { count: selectedUserIds.length })}
            </Button>
          )}
          <Button onClick={handleCreateUser}>
            <Plus className="mr-2 h-4 w-4" />
            {t('users.create')}
          </Button>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <Card>
        <CardHeader>
          <CardTitle>{t('users.userList')}</CardTitle>
          <CardDescription>{t('users.totalUsers', { count: total })}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                placeholder={t('users.searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-48">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder={t('users.filters.filter_by_role')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('users.filters.all_roles')}</SelectItem>
                {Array.isArray(roles) && roles.map((role) => (
                  <SelectItem key={role.id} value={role.name}>
                    {role.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedUserIds.length > 0 && (
              <Button
                variant="outline"
                onClick={resetSelection}
              >
                {t('users.actions.cancel_selection')}
              </Button>
            )}
          </div>

          {/* 用户表格 */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={users.length > 0 && selectedUserIds.length === users.length}
                      onCheckedChange={handleSelectAll}
                      aria-label={t('users.actions.select_all')}
                    />
                  </TableHead>
                  <TableHead>{t('users.table.username')}</TableHead>
                  <TableHead>{t('users.table.email')}</TableHead>
                  <TableHead>{t('users.table.role')}</TableHead>
                  <TableHead>{t('users.table.created_at')}</TableHead>
                  <TableHead>{t('users.table.updated_at')}</TableHead>
                  <TableHead className="text-right">{t('users.table.actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      {t('messages.loading')}
                    </TableCell>
                  </TableRow>
                ) : filteredUsers.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      {t('messages.no_data')}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredUsers.map((user) => (
                    <TableRow
                      key={user.id}
                      className={selectedUserIds.includes(user.id) ? 'bg-blue-50' : ''}
                    >
                      <TableCell>
                        <Checkbox
                          checked={selectedUserIds.includes(user.id)}
                          onCheckedChange={(checked) => handleSelectUser(user.id, checked as boolean)}
                          aria-label={t('users.select_user', { name: user.name })}
                        />
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <Avatar className="h-8 w-8">
                            <AvatarImage src={user.avatar} />
                            <AvatarFallback>{user.name[0]?.toUpperCase()}</AvatarFallback>
                          </Avatar>
                          <span className="font-medium">{user.name}</span>
                        </div>
                      </TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{getRoleBadge(user.role)}</TableCell>
                      <TableCell>{formatDate(user.createdAt)}</TableCell>
                      <TableCell>{formatDate(user.updatedAt || user.createdAt)}</TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <span className="sr-only">{t('users.open_menu')}</span>
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuLabel>{t('users.actions_menu')}</DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={() => handleEditUser(user)}>
                              <Edit className="mr-2 h-4 w-4" />
                              {t('users.edit')}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleAssignRoles(user)}>
                              <UserPlus className="mr-2 h-4 w-4" />
                              {t('users.assign_roles')}
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleResetPassword(user)}>
                              <Key className="mr-2 h-4 w-4" />
                              {t('users.actions.reset_password')}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => handleDeleteUser(user.id)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              {t('users.delete')}
                            </DropdownMenuItem>
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
                {t('users.pagination.previous')}
              </Button>
              <div className="text-sm text-muted-foreground">
                {t('users.pagination.page_info', {
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
                {t('users.pagination.next')}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 对话框 */}
      <UserDialog
        open={userDialogOpen}
        onOpenChange={setUserDialogOpen}
        user={selectedUser}
        onSuccess={() => {
          loadUsers()
          resetSelection()
        }}
      />

      <UserRoleDialog
        open={userRoleDialogOpen}
        onOpenChange={setUserRoleDialogOpen}
        user={selectedUser}
        onSuccess={() => {
          loadUsers()
          resetSelection()
        }}
      />

      <UserPasswordDialog
        open={userPasswordDialogOpen}
        onOpenChange={setUserPasswordDialogOpen}
        user={selectedUser}
        onSuccess={() => {
          loadUsers()
          resetSelection()
        }}
      />

      <BatchDeleteDialog
        open={batchDeleteDialogOpen}
        onOpenChange={setBatchDeleteDialogOpen}
        users={getSelectedUsers()}
        onSuccess={() => {
          loadUsers()
          resetSelection()
        }}
      />
    </div>
  )
}

export default UsersPage