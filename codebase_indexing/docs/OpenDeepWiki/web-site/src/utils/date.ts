// 日期处理工具函数

import i18n from '@/i18n'

export function formatDistanceToNow(date: string | Date): string {
  const now = new Date()
  const past = new Date(date)
  const diffMs = now.getTime() - past.getTime()
  
  const seconds = Math.floor(diffMs / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)
  
  const t = i18n.t.bind(i18n)
  
  if (years > 0) {
    return t('common.time.yearsAgo', { count: years })
  } else if (months > 0) {
    return t('common.time.monthsAgo', { count: months })
  } else if (days > 0) {
    return t('common.time.daysAgo', { count: days })
  } else if (hours > 0) {
    return t('common.time.hoursAgo', { count: hours })
  } else if (minutes > 0) {
    return t('common.time.minutesAgo', { count: minutes })
  } else {
    return t('common.time.justNow')
  }
}

export function formatDate(date: string | Date, format = 'YYYY-MM-DD'): string {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}