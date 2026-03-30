// 批量删除确认对话框

import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { toast } from 'sonner'
import { userService, UserInfo } from '@/services/admin.service'
import { Loader2, AlertTriangle, Trash2 } from 'lucide-react'

interface BatchDeleteDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  users: UserInfo[]
  onSuccess?: () => void
}

const BatchDeleteDialog: React.FC<BatchDeleteDialogProps> = ({
  open,
  onOpenChange,
  users,
  onSuccess
}) => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)

  // 提交批量删除
  const handleSubmit = async () => {
    if (users.length === 0) return

    try {
      setLoading(true)

      const userIds = users.map(user => user.id)
      await userService.batchDeleteUsers(userIds)

      toast.success('删除成功', {
        description: `已删除 ${users.length} 个用户`
      })

      onOpenChange(false)
      onSuccess?.()
    } catch (error: any) {
      const message = error?.response?.data?.message || error?.message || '删除失败'
      toast.error('删除失败', {
        description: message
      })
    } finally {
      setLoading(false)
    }
  }

  if (users.length === 0) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Trash2 className="h-5 w-5 text-red-500" />
            <span>批量删除用户</span>
          </DialogTitle>
          <DialogDescription>
            确认删除以下 {users.length} 个用户？此操作不可撤销。
          </DialogDescription>
        </DialogHeader>

        {/* 安全警告 */}
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>警告：</strong>删除用户将会：
            <ul className="mt-2 ml-4 list-disc space-y-1">
              <li>永久删除用户账户信息</li>
              <li>移除所有角色分配</li>
              <li>用户将无法登录系统</li>
            </ul>
          </AlertDescription>
        </Alert>

        {/* 用户列表 */}
        <div className="space-y-3 max-h-64 overflow-y-auto">
          <div className="font-medium text-sm text-gray-700">
            将要删除的用户：
          </div>
          {users.map((user) => (
            <div
              key={user.id}
              className="flex items-center space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg"
            >
              <Avatar className="h-8 w-8">
                <AvatarImage src={user.avatar} />
                <AvatarFallback>{user.name[0]?.toUpperCase()}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{user.name}</div>
                <div className="text-xs text-gray-500 truncate">{user.email}</div>
              </div>
              <div className="text-xs text-red-600 font-medium">
                将被删除
              </div>
            </div>
          ))}
        </div>

        {/* 确认提示 */}
        <div className="p-4 bg-gray-50 border rounded-lg">
          <div className="font-medium text-sm mb-2">操作确认</div>
          <div className="text-sm text-gray-600">
            请确认您要删除这 <strong className="text-red-600">{users.length}</strong> 个用户。
            此操作将立即生效且无法撤销。
          </div>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            取消
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                删除中...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4 mr-2" />
                确认删除 ({users.length})
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default BatchDeleteDialog