// 权限保护组件

import React from 'react'
import { usePermissions } from '@/hooks/usePermissions'

interface Permission {
  action: string
  resource?: string
}

interface PermissionGuardProps {
  children: React.ReactNode
  permission?: Permission
  permissions?: Permission[]
  requireAll?: boolean // 是否需要所有权限，默认为false（任意一个即可）
  fallback?: React.ReactNode // 无权限时显示的内容
  role?: string | string[] // 直接检查角色
}

/**
 * 权限保护组件
 * 根据用户权限决定是否渲染子组件
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  permission,
  permissions,
  requireAll = false,
  fallback = null,
  role
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, getUserRoles } = usePermissions()

  // 角色检查
  if (role) {
    const userRoles = getUserRoles()
    const rolesToCheck = Array.isArray(role) ? role : [role]
    const hasRequiredRole = rolesToCheck.some(r => userRoles.includes(r.toLowerCase()))

    if (!hasRequiredRole) {
      return <>{fallback}</>
    }
  }

  // 权限检查
  let hasAccess = true

  if (permission) {
    hasAccess = hasPermission(permission)
  } else if (permissions && permissions.length > 0) {
    hasAccess = requireAll
      ? hasAllPermissions(permissions)
      : hasAnyPermission(permissions)
  }

  if (!hasAccess) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

// 预定义的权限保护组件

/**
 * 管理员权限保护
 */
export const AdminGuard: React.FC<Omit<PermissionGuardProps, 'role'>> = (props) => (
  <PermissionGuard {...props} role="admin" />
)

/**
 * 版主权限保护
 */
export const ModeratorGuard: React.FC<Omit<PermissionGuardProps, 'role'>> = (props) => (
  <PermissionGuard {...props} role={['admin', 'moderator']} />
)

/**
 * 编辑者权限保护
 */
export const EditorGuard: React.FC<Omit<PermissionGuardProps, 'role'>> = (props) => (
  <PermissionGuard {...props} role={['admin', 'moderator', 'editor']} />
)

/**
 * 用户管理权限保护
 */
export const UserManagementGuard: React.FC<Omit<PermissionGuardProps, 'permission'>> = (props) => (
  <PermissionGuard {...props} permission={{ action: 'manage_users' }} />
)

/**
 * 角色管理权限保护
 */
export const RoleManagementGuard: React.FC<Omit<PermissionGuardProps, 'permission'>> = (props) => (
  <PermissionGuard {...props} permission={{ action: 'manage_roles' }} />
)

/**
 * 内容管理权限保护
 */
export const ContentManagementGuard: React.FC<Omit<PermissionGuardProps, 'permission'>> = (props) => (
  <PermissionGuard {...props} permission={{ action: 'manage_content' }} />
)

export default PermissionGuard