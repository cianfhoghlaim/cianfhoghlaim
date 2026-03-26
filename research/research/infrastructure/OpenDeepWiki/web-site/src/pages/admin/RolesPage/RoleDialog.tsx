// 角色创建/编辑对话框组件

import React, { useState, useEffect } from 'react'
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
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { toast } from "sonner"
import { roleService, type RoleInfo, type CreateRoleDto, type UpdateRoleDto } from '@/services/admin.service'

interface RoleDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  role?: RoleInfo | null // 编辑模式时传入角色信息
  onSuccess?: (role: RoleInfo) => void
}

const RoleDialog: React.FC<RoleDialogProps> = ({
  open,
  onOpenChange,
  role,
  onSuccess
}) => {
  const { t } = useTranslation('admin')
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<{
    name: string
    description: string
    isActive: boolean
  }>({
    name: '',
    description: '',
    isActive: true
  })

  const isEditMode = Boolean(role)
  const dialogTitle = isEditMode ? t('roles.dialog.form.title.edit') : t('roles.dialog.form.title.create')

  // 当对话框打开或角色数据变化时，初始化表单
  useEffect(() => {
    if (open) {
      if (role) {
        setFormData({
          name: role.name,
          description: role.description || '',
          isActive: role.isActive
        })
      } else {
        setFormData({
          name: '',
          description: '',
          isActive: true
        })
      }
    }
  }, [open, role])

  // 表单字段变化处理
  const handleFieldChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // 表单验证
  const validateForm = () => {
    if (!formData.name.trim()) {
      toast.error(t('roles.validation.validationFailed'), {
        description: t('roles.validation.nameRequired')
      })
      return false
    }

    if (formData.name.trim().length < 2) {
      toast.error(t('roles.validation.validationFailed'), {
        description: t('roles.validation.nameMinLength')
      })
      return false
    }

    if (formData.name.trim().length > 50) {
      toast.error(t('roles.validation.validationFailed'), {
        description: t('roles.validation.nameMaxLength')
      })
      return false
    }

    if (formData.description.length > 200) {
      toast.error(t('roles.validation.validationFailed'), {
        description: t('roles.validation.descriptionMaxLength')
      })
      return false
    }

    return true
  }

  // 提交表单
  const handleSubmit = async () => {
    if (!validateForm()) {
      return
    }

    setLoading(true)
    try {
      let result: RoleInfo

      if (isEditMode && role) {
        // 编辑模式
        const updateData: UpdateRoleDto = {
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          isActive: formData.isActive
        }
        result = await roleService.updateRole(role.id, updateData)
        toast.success(t('roles.messages.updateSuccess'), {
          description: t('roles.messages.updateSuccessDescription')
        })
      } else {
        // 创建模式
        const createData: CreateRoleDto = {
          name: formData.name.trim(),
          description: formData.description.trim() || undefined,
          isActive: formData.isActive
        }
        result = await roleService.createRole(createData)
        toast.success(t('roles.messages.createSuccess'), {
          description: t('roles.messages.createSuccessDescription')
        })
      }

      onSuccess?.(result)
      onOpenChange(false)
    } catch (error: any) {
      toast.error(
        isEditMode ? t('roles.messages.updateFailed') : t('roles.messages.createFailed'),
        {
          description: error?.message || t('roles.messages.operationFailed')
        }
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{dialogTitle}</DialogTitle>
          <DialogDescription>
            {isEditMode
              ? t('roles.dialog.form.description.edit')
              : t('roles.dialog.form.description.create')
            }
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {/* 角色名称 */}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              {t('roles.dialog.form.roleNameRequired')}
            </Label>
            <div className="col-span-3">
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleFieldChange('name', e.target.value)}
                placeholder={t('roles.dialog.form.roleNamePlaceholder')}
                disabled={loading || (isEditMode && role?.isSystemRole)}
                maxLength={50}
              />
              <div className="text-xs text-muted-foreground mt-1">
                {formData.name.length}/50
              </div>
            </div>
          </div>

          {/* 角色描述 */}
          <div className="grid grid-cols-4 items-start gap-4">
            <Label htmlFor="description" className="text-right mt-2">
              {t('roles.dialog.form.roleDescription')}
            </Label>
            <div className="col-span-3">
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleFieldChange('description', e.target.value)}
                placeholder={t('roles.dialog.form.roleDescriptionPlaceholder')}
                disabled={loading}
                maxLength={200}
                rows={3}
              />
              <div className="text-xs text-muted-foreground mt-1">
                {formData.description.length}/200
              </div>
            </div>
          </div>

          {/* 启用状态 */}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="isActive" className="text-right">
              {t('roles.dialog.form.enableStatus')}
            </Label>
            <div className="col-span-3 flex items-center space-x-2">
              <Switch
                id="isActive"
                checked={formData.isActive}
                onCheckedChange={(checked) => handleFieldChange('isActive', checked)}
                disabled={loading || (isEditMode && role?.isSystemRole)}
              />
              <span className="text-sm text-muted-foreground">
                {formData.isActive ? t('roles.dialog.form.enabled') : t('roles.dialog.form.disabled')}
              </span>
            </div>
          </div>

          {/* 系统角色提示 */}
          {isEditMode && role?.isSystemRole && (
            <div className="col-span-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <div className="text-sm text-yellow-800">
                <strong>{t('roles.dialog.form.systemRoleWarning')}：</strong> {t('roles.dialog.form.systemRoleWarningMessage')}
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            {t('roles.dialog.form.cancel')}
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading 
              ? (isEditMode ? t('roles.dialog.form.submit.updateLoading') : t('roles.dialog.form.submit.createLoading')) 
              : (isEditMode ? t('roles.dialog.form.submit.update') : t('roles.dialog.form.submit.create'))}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default RoleDialog