import { useForm, type UseFormProps, type UseFormReturn, type FieldValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCallback } from 'react'
import { toast } from 'sonner'

interface UseFormWithValidationOptions<T extends FieldValues> extends Omit<UseFormProps<T>, 'resolver'> {
  schema: z.ZodSchema<T>
  onSubmitSuccess?: (data: T) => void | Promise<void>
  onSubmitError?: (error: unknown) => void
  submitToast?: {
    loading?: string
    success?: string
    error?: string
  }
  showErrorToasts?: boolean // 是否显示字段验证错误的 toast
}

interface UseFormWithValidationReturn<T extends FieldValues> extends UseFormReturn<T> {
  handleSubmit: (onValid: (data: T) => void | Promise<void>) => (e?: React.BaseSyntheticEvent) => Promise<void>
  isSubmitting: boolean
  submitWithToast: (onValid: (data: T) => void | Promise<void>) => (e?: React.BaseSyntheticEvent) => Promise<void>
}

export function useFormWithValidation<T extends FieldValues = FieldValues>(
  options: UseFormWithValidationOptions<T>
): UseFormWithValidationReturn<T> {
  const {
    schema,
    onSubmitSuccess,
    onSubmitError,
    submitToast = {
      loading: '提交中...',
      success: '操作成功',
      error: '操作失败'
    },
    showErrorToasts = true,
    ...formOptions
  } = options

  const form = useForm<T>({
    resolver: zodResolver(schema) as any,
    mode: 'onChange',
    ...formOptions
  })

  const { formState: { isSubmitting } } = form

  // 处理字段验证错误，显示 toast
  const handleFieldErrors = useCallback((errors: typeof form.formState.errors) => {
    if (!showErrorToasts) return

    const errorMessages = Object.values(errors)
      .map(error => error?.message)
      .filter(Boolean)

    if (errorMessages.length > 0) {
      errorMessages.forEach((message:any) => {
        if (message) toast.error(message.toString())
      })
    }
  }, [showErrorToasts])

  // 基础的表单提交处理
  const handleSubmit = useCallback((onValid: (data: T) => void | Promise<void>) => {
    return form.handleSubmit(
      async (data:any) => {
        try {
          await onValid(data)
          onSubmitSuccess?.(data)
        } catch (error) {
          console.error('Form submission error:', error)
          onSubmitError?.(error)
          throw error // 重新抛出错误，让上层处理
        }
      },
      (errors) => {
        handleFieldErrors(errors)
      }
    )
  }, [form, onSubmitSuccess, onSubmitError, handleFieldErrors])

  // 带 toast 提示的表单提交处理
  const submitWithToast = useCallback((onValid: (data: T) => void | Promise<void>) => {
    return form.handleSubmit(
      async (data) => {
        const toastId = submitToast.loading ? toast.loading(submitToast.loading) : null

        try {
          await onValid(data)

          if (toastId) toast.dismiss(toastId)
          if (submitToast.success) {
            toast.success(submitToast.success)
          }

          onSubmitSuccess?.(data)
        } catch (error) {
          if (toastId) toast.dismiss(toastId)

          const errorMessage = error instanceof Error ? error.message : submitToast.error || '操作失败'
          toast.error(errorMessage)

          onSubmitError?.(error)
          console.error('Form submission error:', error)
        }
      },
      (errors) => {
        handleFieldErrors(errors)
      }
    )
  }, [form, submitToast, onSubmitSuccess, onSubmitError, handleFieldErrors])

  return {
    ...form,
    handleSubmit,
    isSubmitting,
    submitWithToast
  } as any
}

// 预定义的常用验证模式
export const commonSchemas = {
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string().min(8, '密码长度至少8位').regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]/,
    '密码必须包含大小写字母和数字'
  ),
  username: z.string().min(2, '用户名至少2位').max(50, '用户名最多50位'),
  url: z.string().url('请输入有效的URL地址'),
  required: z.string().min(1, '此字段为必填项'),
  optionalString: z.string().optional(),
  positiveNumber: z.number().positive('必须是正数'),
  integer: z.number().int('必须是整数')
}

// 通用的表单状态类型
export interface FormState {
  isLoading: boolean
  isSubmitting: boolean
  isDirty: boolean
  isValid: boolean
  errors: Record<string, string>
}

// 表单字段配置类型
export interface FormFieldConfig {
  name: string
  label: string
  type?: 'text' | 'email' | 'password' | 'textarea' | 'select' | 'checkbox' | 'number'
  placeholder?: string
  required?: boolean
  disabled?: boolean
  options?: Array<{ label: string; value: string }>
  validation?: z.ZodSchema<any>
}

// 动态表单生成器的类型
export interface DynamicFormConfig<T extends FieldValues> {
  schema: z.ZodSchema<T>
  fields: FormFieldConfig[]
  defaultValues?: Partial<T>
  onSubmit: (data: T) => void | Promise<void>
  submitButtonText?: string
  resetAfterSubmit?: boolean
}

// 批量操作表单的 Hook
export function useBatchForm<T extends FieldValues>(
  schema: z.ZodSchema<T>,
  batchSize: number = 10
) {
  const form = useFormWithValidation({ schema })

  const processBatch = useCallback(async (
    items: any[],
    processor: (item: any, data: T) => Promise<void>
  ) => {
    const data = form.getValues()
    const batches = []

    for (let i = 0; i < items.length; i += batchSize) {
      batches.push(items.slice(i, i + batchSize))
    }

    for (const batch of batches) {
      await Promise.all(
        batch.map(item => processor(item, data))
      )
    }
  }, [form, batchSize])

  return {
    ...form,
    processBatch
  }
}

export default useFormWithValidation