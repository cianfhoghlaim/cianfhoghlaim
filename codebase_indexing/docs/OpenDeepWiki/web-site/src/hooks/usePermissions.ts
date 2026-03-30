// 权限控制Hook

import { useAuth } from './useAuth'

interface Permission {
  action: string
  resource?: string
}

/**
 * 权限控制Hook
 * 提供统一的权限检查逻辑
 */
export const usePermissions = () => {
  const { user, isAuthenticated } = useAuth()

  /**
   * 检查是否为管理员
   */
  const isAdmin = () => {
    if (!user?.role) return false
    return user.role.includes('admin') || user.role.includes('Admin')
  }

  /**
   * 检查是否为版主
   */
  const isModerator = () => {
    if (!user?.role) return false
    return user.role.includes('moderator') || user.role.includes('Moderator') || isAdmin()
  }

  /**
   * 检查是否有特定权限
   * @param permission 权限对象
   */
  const hasPermission = (permission: Permission): boolean => {
    if (!isAuthenticated || !user) return false

    const { action, resource } = permission

    // 管理员拥有所有权限
    if (isAdmin()) return true

    // 根据角色和操作类型检查权限
    const userRoles = user.role?.toLowerCase().split(',').map(r => r.trim()) || []

    switch (action) {
      case 'read':
        // 所有认证用户都有读取权限
        return true

      case 'write':
      case 'create':
      case 'update':
        // 版主和管理员有写入权限
        return userRoles.some(role => ['admin', 'moderator', 'editor'].includes(role))

      case 'delete':
        // 只有管理员和版主有删除权限
        return userRoles.some(role => ['admin', 'moderator'].includes(role))

      case 'manage_users':
      case 'manage_roles':
      case 'manage_system':
        // 只有管理员有用户和系统管理权限
        return isAdmin()

      case 'manage_content':
        // 版主和管理员有内容管理权限
        return isModerator()

      default:
        return false
    }
  }

  /**
   * 检查是否有多个权限中的任意一个
   * @param permissions 权限数组
   */
  const hasAnyPermission = (permissions: Permission[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }

  /**
   * 检查是否拥有所有指定权限
   * @param permissions 权限数组
   */
  const hasAllPermissions = (permissions: Permission[]): boolean => {
    return permissions.every(permission => hasPermission(permission))
  }

  /**
   * 检查是否可以访问管理员控制台
   */
  const canAccessAdmin = (): boolean => {
    return hasPermission({ action: 'manage_system' })
  }

  /**
   * 检查是否可以管理用户
   */
  const canManageUsers = (): boolean => {
    return hasPermission({ action: 'manage_users' })
  }

  /**
   * 检查是否可以管理角色
   */
  const canManageRoles = (): boolean => {
    return hasPermission({ action: 'manage_roles' })
  }

  /**
   * 检查是否可以管理内容
   */
  const canManageContent = (): boolean => {
    return hasPermission({ action: 'manage_content' })
  }

  /**
   * 获取用户角色列表
   */
  const getUserRoles = (): string[] => {
    if (!user?.role) return []
    return user.role.toLowerCase().split(',').map(r => r.trim())
  }

  return {
    // 基础权限检查
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,

    // 角色检查
    isAdmin,
    isModerator,
    getUserRoles,

    // 具体功能权限检查
    canAccessAdmin,
    canManageUsers,
    canManageRoles,
    canManageContent,

    // 用户信息
    user,
    isAuthenticated
  }
}