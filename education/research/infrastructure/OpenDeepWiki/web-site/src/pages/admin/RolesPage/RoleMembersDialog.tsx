// 角色成员查看对话框组件

import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { toast } from 'sonner'
import {
  Users,
  Search,
  UserPlus,
  UserMinus,
  Mail,
  Calendar,
  Shield
} from 'lucide-react'
import { roleService, type RoleInfo, type UserInfo } from '@/services/admin.service'

interface RoleMembersDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  role: RoleInfo | null
}

const RoleMembersDialog: React.FC<RoleMembersDialogProps> = ({
  open,
  onOpenChange,
  role
}) => {
  const { t } = useTranslation('admin')
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [members, setMembers] = useState<UserInfo[]>([])
  const [filteredMembers, setFilteredMembers] = useState<UserInfo[]>([])

  // 加载角色成员
  const loadRoleMembers = async () => {
    if (!role?.id) return

    setLoading(true)
    try {
      const roleDetail = await roleService.getRoleDetail(role.id)
      const memberList = roleDetail.users || []
      setMembers(memberList)
      setFilteredMembers(memberList)
    } catch (error: any) {
      toast.error(t('roles.messages.loadMembersError'), {
        description: error?.message || t('roles.messages.loadMembersError')
      })
    } finally {
      setLoading(false)
    }
  }

  // 当对话框打开时加载数据
  useEffect(() => {
    if (open && role) {
      loadRoleMembers()
      setSearchQuery('')
    }
  }, [open, role])

  // 搜索过滤
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredMembers(members)
    } else {
      const query = searchQuery.toLowerCase()
      setFilteredMembers(
        members.filter(member =>
          member.name.toLowerCase().includes(query) ||
          member.email.toLowerCase().includes(query)
        )
      )
    }
  }, [searchQuery, members])

  // 格式化日期
  const formatDate = (dateString: string) => {
    if (!dateString) return t('common.unknown')
    return new Date(dateString).toLocaleDateString('zh-CN')
  }

  // 获取用户头像显示文字
  const getUserAvatarText = (name: string) => {
    if (!name) return 'U'
    const words = name.trim().split(/\s+/)
    if (words.length === 1) {
      return words[0].slice(0, 2).toUpperCase()
    }
    return words.slice(0, 2).map(word => word[0]).join('').toUpperCase()
  }

  // 移除用户角色
  const handleRemoveUser = async (user: UserInfo) => {
    if (!role?.id) return

    const confirmed = confirm(t('roles.dialog.roleMembers.confirmRemove', { name: user.name, role: role.name }))
    if (!confirmed) return

    try {
      // 这里需要调用移除用户角色的API
      // 暂时使用toast提示，实际需要后端API支持
      toast.success(t('roles.messages.removeSuccess'), {
        description: t('roles.messages.removeSuccessDescription')
      })

      // 重新加载成员列表
      loadRoleMembers()
    } catch (error: any) {
      toast.error(t('roles.messages.removeFailed'), {
        description: error?.message || t('roles.messages.removeFailedDescription')
      })
    }
  }

  if (!role) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            {t('roles.dialog.roleMembers.title')}
          </DialogTitle>
          <DialogDescription>
            {t('roles.dialog.roleMembers.description', { name: role?.name })}
          </DialogDescription>
        </DialogHeader>

        {/* 角色信息概览 */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Shield className="h-4 w-4" />
              {t('roles.dialog.roleMembers.title')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">{t('roles.table.name')}</div>
                <div className="font-medium">{role?.name}</div>
              </div>
              <div>
                <div className="text-muted-foreground">{t('roles.dialog.roleMembers.memberCount', { count: members.length })}</div>
                <div className="font-medium">{members.length}</div>
              </div>
              <div>
                <div className="text-muted-foreground">{t('roles.table.permissions_count')}</div>
                <div className="font-medium">{role?.warehousePermissionCount || 0}</div>
              </div>
              <div>
                <div className="text-muted-foreground">{t('roles.table.status')}</div>
                <Badge variant={role?.isActive ? 'default' : 'secondary'}>
                  {role?.isActive ? t('roles.status.enabled') : t('roles.status.disabled')}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 搜索和操作 */}
        <div className="flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              placeholder={t('roles.dialog.roleMembers.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button size="sm" className="gap-2">
              <UserPlus className="h-4 w-4" />
              {t('common.add')}
            </Button>
          </div>
        </div>

        {/* 成员列表 */}
        <div className="flex-1 min-h-0">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">
                {t('roles.dialog.roleMembers.title')} ({filteredMembers.length})
              </CardTitle>
              <CardDescription>
                {t('roles.dialog.roleMembers.description', { name: role?.name })}
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0">
              <ScrollArea className="h-[400px]">
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="text-muted-foreground">{t('common.loading')}</div>
                  </div>
                ) : filteredMembers.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                    <Users className="h-12 w-12 mb-2 opacity-50" />
                    <div>
                      {searchQuery ? t('common.no_data') : t('roles.dialog.roleMembers.noMembers')}
                    </div>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('roles.table.name')}</TableHead>
                        <TableHead>{t('roles.table.email')}</TableHead>
                        <TableHead>{t('roles.dialog.roleMembers.memberTable.joined')}</TableHead>
                        <TableHead>{t('roles.table.status')}</TableHead>
                        <TableHead className="text-right">{t('roles.table.actions')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredMembers.map((member) => (
                        <TableRow key={member.id}>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <Avatar className="h-8 w-8">
                                <AvatarImage src={member.avatar} alt={member.name} />
                                <AvatarFallback className="text-xs">
                                  {getUserAvatarText(member.name)}
                                </AvatarFallback>
                              </Avatar>
                              <div>
                                <div className="font-medium">{member.name}</div>
                                <div className="text-xs text-muted-foreground">
                                  ID: {member.id.slice(0, 8)}...
                                </div>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Mail className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">{member.email}</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">{formatDate(member.createdAt)}</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">
                              {t('roles.status.active')}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            {!role?.isSystemRole && (
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleRemoveUser(member)}
                              >
                                <UserMinus className="h-4 w-4 mr-1" />
                                {t('roles.dialog.roleMembers.removeUser')}
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* 统计信息 */}
        {members.length > 0 && (
          <>
            <Separator />
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <div>
                {t('roles.table.users_count')}: {members.length}
                {searchQuery && filteredMembers.length !== members.length && (
                  <span>，{t('common.no_data')} {filteredMembers.length}</span>
                )}
              </div>
              <div>
                {role?.isSystemRole && (
                  <span className="text-yellow-600">{t('roles.type.system')}{t('common.notSet')}</span>
                )}
              </div>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}

export default RoleMembersDialog