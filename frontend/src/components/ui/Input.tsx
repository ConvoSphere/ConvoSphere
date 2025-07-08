import React from 'react'
import { cn } from '../../utils/cn'

interface BaseInputProps {
  label?: string
  error?: string
  helperText?: string
  multiline?: boolean
  rows?: number
  onChange?: (value: string) => void
}

interface InputProps extends BaseInputProps, Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  multiline?: false
}

interface TextareaProps extends BaseInputProps, Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange'> {
  multiline: true
}

type InputComponentProps = InputProps | TextareaProps

const Input = React.forwardRef<HTMLInputElement | HTMLTextAreaElement, InputComponentProps>(
  ({ className, label, error, helperText, id, multiline, rows = 3, onChange, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      if (onChange) {
        onChange(e.target.value)
      }
    }
    
    const inputClasses = cn(
      'flex w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus-visible:ring-indigo',
      error && 'border-red-500 focus-visible:ring-red-500',
      multiline ? 'min-h-[80px] resize-vertical' : 'h-10',
      className
    )
    
    return (
      <div className="space-y-2">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {label}
          </label>
        )}
        {multiline ? (
          <textarea
            id={inputId}
            className={inputClasses}
            rows={rows}
            ref={ref as React.Ref<HTMLTextAreaElement>}
            onChange={handleChange}
            {...(props as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
          />
        ) : (
          <input
            id={inputId}
            className={inputClasses}
            ref={ref as React.Ref<HTMLInputElement>}
            onChange={handleChange}
            {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
          />
        )}
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}
        {helperText && !error && (
          <p className="text-sm text-gray-500 dark:text-gray-400">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input 