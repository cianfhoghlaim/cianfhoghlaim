// 用户个人资料信息组件
import { useState, useRef } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { toast as sonnerToast } from 'sonner'
import {
  Camera,
  Save,
  Edit,
  X,
  Loader2
} from 'lucide-react'
import { userService } from '@/services/userService'

export const ProfileInfo: React.FC = () => {
  const { user } = useAuth()
  const { t } = useTranslation()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [isEditing, setIsEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  // 表单数据
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    bio: '',
    location: '',
    website: '',
    company: ''
  })

  // 处理表单输入变化
  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // 保存用户信息
  const handleSave = async () => {
    setLoading(true)
    try {
      await userService.updateProfile(formData)
      setIsEditing(false)
      sonnerToast.success(t('profile.info.saveSuccess'), { description: t('profile.info.saveProfileInfo') })
    } catch (error: any) {
      sonnerToast.error(t('profile.info.saveFailed'), { description: error.message || '' })
    } finally {
      setLoading(false)
    }
  }

  // 取消编辑
  const handleCancel = () => {
    setFormData({
      username: user?.username || '',
      email: user?.email || '',
      bio: '',
      location: '',
      website: '',
      company: ''
    })
    setIsEditing(false)
  }

  // 处理头像上传
  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    // 验证文件类型
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!validTypes.includes(file.type)) {
      sonnerToast.error(t('profile.info.uploadFileTypeError'), { description: t('profile.info.uploadFileTypeErrorDesc') })
      return
    }

    // 验证文件大小（5MB）
    if (file.size > 5 * 1024 * 1024) {
      sonnerToast.error(t('profile.info.uploadFileSizeError'), { description: t('profile.info.uploadFileSizeErrorDesc') })
      return
    }

    setUploadingAvatar(true)
    try {
      const formData = new FormData()
      formData.append('avatar', file)

      await userService.uploadAvatar(formData)

      sonnerToast.success(t('profile.info.uploadSuccess'), { description: '' })
    } catch (error: any) {
      sonnerToast.error(t('profile.info.uploadFailed'), { description: error.message || '' })
    } finally {
      setUploadingAvatar(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  // 删除头像
  const handleDeleteAvatar = async () => {
    try {
      await userService.deleteAvatar()
      setShowDeleteDialog(false)
      sonnerToast.success(t('profile.info.deleteSuccess'), { description: '' })
    } catch (error: any) {
      sonnerToast.error(t('profile.info.deleteFailed'), { description: error.message || '' })
    }
  }

  return (
    <div className="space-y-6">
      {/* 头像部分 */}
      <div className="flex items-center space-x-6">
        <div className="relative">
          <Avatar className="h-24 w-24">
            <AvatarImage src={user?.avatar} alt={user?.username} />
            <AvatarFallback className="text-2xl">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>

          {/* 头像操作按钮 */}
          <div className="absolute -bottom-2 -right-2 flex space-x-1">
            <Button
              size="sm"
              variant="secondary"
              className="h-8 w-8 rounded-full p-0"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadingAvatar}
            >
              {uploadingAvatar ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Camera className="h-4 w-4" />
              )}
            </Button>
            {user?.avatar && (
              <Button
                size="sm"
                variant="destructive"
                className="h-8 w-8 rounded-full p-0"
                onClick={() => setShowDeleteDialog(true)}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleAvatarUpload}
          />
        </div>

        <div className="flex-1">
          <h2 className="text-2xl font-semibold">{user?.username}</h2>
          <p className="text-muted-foreground">{user?.email}</p>
        </div>

        {/* 编辑按钮 */}
        {!isEditing && (
          <Button onClick={() => setIsEditing(true)} variant="outline">
            <Edit className="h-4 w-4 mr-2" />
            {t('profile.info.editProfile')}
          </Button>
        )}
      </div>

      {/* 表单部分 */}
      <div className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="username">{t('profile.info.username')}</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              disabled={!isEditing}
              placeholder={t('profile.info.username')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">{t('profile.info.email')}</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              disabled={!isEditing}
              placeholder={t('profile.info.email')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">{t('profile.info.location')}</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              disabled={!isEditing}
              placeholder={t('profile.info.locationPlaceholder')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="company">{t('profile.info.company')}</Label>
            <Input
              id="company"
              value={formData.company}
              onChange={(e) => handleInputChange('company', e.target.value)}
              disabled={!isEditing}
              placeholder={t('profile.info.companyPlaceholder')}
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="website">{t('profile.info.website')}</Label>
            <Input
              id="website"
              type="url"
              value={formData.website}
              onChange={(e) => handleInputChange('website', e.target.value)}
              disabled={!isEditing}
              placeholder={t('profile.info.websitePlaceholder')}
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label htmlFor="bio">{t('profile.info.bio')}</Label>
            <Textarea
              id="bio"
              value={formData.bio}
              onChange={(e) => handleInputChange('bio', e.target.value)}
              disabled={!isEditing}
              placeholder={t('profile.info.bioPlaceholder')}
              rows={4}
              className="resize-none"
            />
          </div>
        </div>

        {/* 操作按钮 */}
        {isEditing && (
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={loading}
            >
              <X className="h-4 w-4 mr-2" />
              {t('profile.info.cancel')}
            </Button>
            <Button
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  {t('profile.info.saving')}
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {t('profile.info.saveChanges')}
                </>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* 删除头像确认对话框 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t('profile.info.confirmDeleteAvatar')}</AlertDialogTitle>
            <AlertDialogDescription>
              {t('profile.info.deleteAvatarDesc')}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t('profile.info.cancel')}</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteAvatar}>
              {t('common.confirm')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export default ProfileInfo
