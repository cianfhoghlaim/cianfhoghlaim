// 用户密码重置对话框

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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { toast } from 'sonner'
import { userService, UserInfo } from '@/services/admin.service'
import { Loader2, AlertTriangle } from 'lucide-react'

interface UserPasswordDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  user?: UserInfo | null
  onSuccess?: () => void
}

const UserPasswordDialog: React.FC<UserPasswordDialogProps> = ({
  open,
  onOpenChange,
  user,
  onSuccess
}) => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    newPassword: '',
    confirmPassword: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  // 重置表单
  const resetForm = () => {
    setForm({
      newPassword: '',
      confirmPassword: ''
    })
    setErrors({})
  }

  // 表单验证
  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!form.newPassword) {
      newErrors.newPassword = '新密码不能为空'
    } else if (form.newPassword.length < 6) {
      newErrors.newPassword = '密码至少6个字符'
    }

    if (!form.confirmPassword) {
      newErrors.confirmPassword = '请确认新密码'
    } else if (form.newPassword !== form.confirmPassword) {
      newErrors.confirmPassword = '两次输入的密码不一致'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // 提交重置
  const handleSubmit = async () => {
    if (!user?.id || !validateForm()) return

    try {
      setLoading(true)

      await userService.resetUserPassword(user.id, form.newPassword)

      toast.success('重置成功', {
        description: '用户密码已重置'
      })

      onOpenChange(false)
      onSuccess?.()
    } catch (error: any) {
      const message = error?.response?.data?.message || error?.message || '重置失败'
      toast.error('重置失败', {
        description: message
      })
    } finally {
      setLoading(false)
    }
  }

  // 监听对话框开关
  React.useEffect(() => {
    if (open) {
      resetForm()
    }
  }, [open])

  if (!user) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>重置用户密码</DialogTitle>
          <DialogDescription>
            为用户设置新的登录密码
          </DialogDescription>
        </DialogHeader>

        {/* 用户信息 */}
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg">
          <Avatar className="h-10 w-10">
            <AvatarImage src={user.avatar} />
            <AvatarFallback>{user.name[0]?.toUpperCase()}</AvatarFallback>
          </Avatar>
          <div>
            <div className="font-medium">{user.name}</div>
            <div className="text-sm text-gray-500">{user.email}</div>
          </div>
        </div>

        {/* 安全提示 */}
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            密码重置后，用户需要使用新密码重新登录。请确保将新密码安全地传达给用户。
          </AlertDescription>
        </Alert>

        <div className="space-y-4">
          {/* 新密码 */}
          <div className="space-y-2">
            <Label htmlFor="newPassword">新密码</Label>
            <Input
              id="newPassword"
              type="password"
              value={form.newPassword}
              onChange={(e) => setForm(prev => ({ ...prev, newPassword: e.target.value }))}
              placeholder="请输入新密码"
              className={errors.newPassword ? 'border-red-500' : ''}
            />
            {errors.newPassword && (
              <p className="text-sm text-red-500">{errors.newPassword}</p>
            )}
            <p className="text-xs text-gray-500">
              密码建议至少6个字符，包含字母和数字
            </p>
          </div>

          {/* 确认密码 */}
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">确认新密码</Label>
            <Input
              id="confirmPassword"
              type="password"
              value={form.confirmPassword}
              onChange={(e) => setForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
              placeholder="请再次输入新密码"
              className={errors.confirmPassword ? 'border-red-500' : ''}
            />
            {errors.confirmPassword && (
              <p className="text-sm text-red-500">{errors.confirmPassword}</p>
            )}
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
            onClick={handleSubmit}
            disabled={loading}
            variant="destructive"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                重置中...
              </>
            ) : (
              '确认重置'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default UserPasswordDialog