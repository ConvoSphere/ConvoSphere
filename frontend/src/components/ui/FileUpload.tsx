import React, { useState, useRef, useCallback } from 'react'
import { fileService, type UploadProgress, type UploadResult } from '../../services/fileService'
import { cn } from '../../utils/cn'
import Button from './Button'

interface FileUploadProps {
  onUpload?: (result: UploadResult) => void
  onUploadMultiple?: (results: UploadResult[]) => void
  onError?: (error: Error) => void
  multiple?: boolean
  accept?: string
  maxSize?: number
  className?: string
  disabled?: boolean
  variant?: 'default' | 'knowledge' | 'chat'
}

const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  onUploadMultiple,
  onError,
  multiple = false,
  accept,
  maxSize,
  className,
  disabled = false,
  variant = 'default'
}) => {
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState<UploadProgress | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFiles = useCallback(async (files: FileList) => {
    if (disabled || uploading) return

    const fileArray = Array.from(files)
    if (fileArray.length === 0) return

    setUploading(true)
    setProgress(null)

    try {
      if (multiple) {
        const results = await fileService.uploadFiles(fileArray, {
          maxSize,
          onProgress: (progress) => setProgress(progress),
          onError
        })
        onUploadMultiple?.(results)
      } else {
        const result = await fileService.uploadFile(fileArray[0], {
          maxSize,
          onProgress: (progress) => setProgress(progress),
          onError
        })
        onUpload?.(result)
      }
    } catch (error) {
      onError?.(error as Error)
    } finally {
      setUploading(false)
      setProgress(null)
    }
  }, [disabled, uploading, multiple, maxSize, onUpload, onUploadMultiple, onError])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled) {
      setIsDragOver(true)
    }
  }, [disabled])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    if (!disabled) {
      handleFiles(e.dataTransfer.files)
    }
  }, [disabled, handleFiles])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files)
    }
  }, [handleFiles])

  const handleClick = useCallback(() => {
    if (!disabled) {
      fileInputRef.current?.click()
    }
  }, [disabled])

  const getUploadText = () => {
    if (uploading) {
      return progress ? `Uploading... ${progress.percentage}%` : 'Uploading...'
    }
    
    switch (variant) {
      case 'knowledge':
        return 'Drop documents here or click to upload'
      case 'chat':
        return 'Drop files here or click to attach'
      default:
        return 'Drop files here or click to upload'
    }
  }

  const getAcceptedTypes = () => {
    if (accept) return accept
    
    switch (variant) {
      case 'knowledge':
        return '.pdf,.doc,.docx,.txt,.md'
      case 'chat':
        return '.pdf,.doc,.docx,.txt,.md,.jpg,.jpeg,.png,.gif'
      default:
        return '*'
    }
  }

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer',
          isDragOver && !disabled && 'border-indigo bg-indigo/5',
          disabled && 'opacity-50 cursor-not-allowed',
          uploading && 'pointer-events-none',
          'hover:border-indigo/50'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="space-y-4">
          <div className="text-4xl">
            {uploading ? '⏳' : '📁'}
          </div>
          
          <div>
            <p className="text-lg font-medium">
              {getUploadText()}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {variant === 'knowledge' && 'Supports PDF, Word, and text files'}
              {variant === 'chat' && 'Supports documents and images'}
              {variant === 'default' && 'All file types supported'}
            </p>
          </div>

          {progress && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-indigo h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
          )}

          {!uploading && (
            <Button
              variant="outline"
              size="sm"
              disabled={disabled}
              onClick={(e) => {
                e.stopPropagation()
                handleClick()
              }}
            >
              Choose Files
            </Button>
          )}
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple={multiple}
        accept={getAcceptedTypes()}
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled || uploading}
      />
    </div>
  )
}

export default FileUpload 