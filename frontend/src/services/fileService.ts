import { authService } from './authService'

export interface UploadProgress {
  loaded: number
  total: number
  percentage: number
}

export interface UploadResult {
  id: string
  filename: string
  size: number
  mime_type: string
  url: string
  uploaded_at: string
}

export interface FileUploadOptions {
  onProgress?: (progress: UploadProgress) => void
  onError?: (error: Error) => void
  maxSize?: number // in bytes
  allowedTypes?: string[]
}

class FileService {
  private readonly maxFileSize = 10 * 1024 * 1024 // 10MB
  private readonly allowedMimeTypes = [
    'text/plain',
    'text/markdown',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp'
  ]

  /**
   * Upload a file to the server
   */
  public async uploadFile(
    file: File,
    options: FileUploadOptions = {}
  ): Promise<UploadResult> {
    // Validate file
    this.validateFile(file, options)

    const formData = new FormData()
    formData.append('file', file)

    const token = await authService.getValidToken()
    if (!token) {
      throw new Error('No valid authentication token')
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      // Progress tracking
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && options.onProgress) {
          const progress: UploadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: Math.round((event.loaded / event.total) * 100)
          }
          options.onProgress(progress)
        }
      })

      // Response handling
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const result: UploadResult = JSON.parse(xhr.responseText)
            resolve(result)
          } catch {
            reject(new Error('Failed to parse upload response'))
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`))
        }
      })

      // Error handling
      xhr.addEventListener('error', () => {
        const err = new Error('Network error during upload')
        if (options.onError) {
          options.onError(err)
        }
        reject(err)
      })

      xhr.addEventListener('abort', () => {
        const err = new Error('Upload was aborted')
        if (options.onError) {
          options.onError(err)
        }
        reject(err)
      })

      // Send request
      xhr.open('POST', `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/files/upload`)
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.send(formData)
    })
  }

  /**
   * Upload multiple files
   */
  public async uploadFiles(
    files: File[],
    options: FileUploadOptions = {}
  ): Promise<UploadResult[]> {
    const uploadPromises = files.map(file => this.uploadFile(file, options))
    return Promise.all(uploadPromises)
  }

  /**
   * Upload a file for knowledge base
   */
  public async uploadKnowledgeDocument(
    file: File,
    metadata: {
      title?: string
      description?: string
      tags?: string[]
      category?: string
    } = {},
    options: FileUploadOptions = {}
  ): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))

    const token = await authService.getValidToken()
    if (!token) {
      throw new Error('No valid authentication token')
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && options.onProgress) {
          const progress: UploadProgress = {
            loaded: event.loaded,
            total: event.total,
            percentage: Math.round((event.loaded / event.total) * 100)
          }
          options.onProgress(progress)
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          try {
            const result: UploadResult = JSON.parse(xhr.responseText)
            resolve(result)
          } catch {
            reject(new Error('Failed to parse upload response'))
          }
        } else {
          reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`))
        }
      })

      xhr.addEventListener('error', () => {
        const err = new Error('Network error during upload')
        if (options.onError) {
          options.onError(err)
        }
        reject(err)
      })

      xhr.open('POST', `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/knowledge/upload`)
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.send(formData)
    })
  }

  /**
   * Get file information
   */
  public async getFileInfo(fileId: string): Promise<UploadResult> {
    const token = await authService.getValidToken()
    if (!token) {
      throw new Error('No valid authentication token')
    }

    const response = await fetch(
      `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/files/${fileId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to get file info: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Delete a file
   */
  public async deleteFile(fileId: string): Promise<void> {
    const token = await authService.getValidToken()
    if (!token) {
      throw new Error('No valid authentication token')
    }

    const response = await fetch(
      `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/files/${fileId}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to delete file: ${response.status}`)
    }
  }

  /**
   * Validate file before upload
   */
  private validateFile(file: File, options: FileUploadOptions): void {
    const maxSize = options.maxSize || this.maxFileSize
    const allowedTypes = options.allowedTypes || this.allowedMimeTypes

    if (file.size > maxSize) {
      throw new Error(`File size exceeds maximum allowed size of ${this.formatFileSize(maxSize)}`)
    }

    if (!allowedTypes.includes(file.type)) {
      throw new Error(`File type ${file.type} is not allowed`)
    }
  }

  /**
   * Format file size for display
   */
  public formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  /**
   * Get file icon based on MIME type
   */
  public getFileIcon(mimeType: string): string {
    if (mimeType.startsWith('image/')) return '🖼️'
    if (mimeType === 'application/pdf') return '📄'
    if (mimeType.includes('word')) return '📝'
    if (mimeType === 'text/plain') return '📄'
    if (mimeType === 'text/markdown') return '📝'
    return '📎'
  }

  /**
   * Check if file is an image
   */
  public isImage(mimeType: string): boolean {
    return mimeType.startsWith('image/')
  }

  /**
   * Check if file is a document
   */
  public isDocument(mimeType: string): boolean {
    return [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'text/markdown'
    ].includes(mimeType)
  }
}

// Export singleton instance
export const fileService = new FileService() 