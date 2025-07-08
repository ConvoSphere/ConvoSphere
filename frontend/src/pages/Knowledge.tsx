import React, { useState } from 'react'
import { useGetDocumentsQuery, useUploadDocumentMutation, useDeleteDocumentMutation, useProcessDocumentMutation, useSearchDocumentsMutation, useGetSupportedFormatsQuery, type SearchRequest } from '../services/apiSlice'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { Upload, Search, FileText, Trash2, Play, Tag } from 'lucide-react'

interface UploadFormData {
  title: string
  description: string
  tags: string
}

const Knowledge: React.FC = () => {
  const [showUploadForm, setShowUploadForm] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadFormData, setUploadFormData] = useState<UploadFormData>({
    title: '',
    description: '',
    tags: '',
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])

  const { data: documents, isLoading, error } = useGetDocumentsQuery({ limit: 100 })
  const [uploadDocument, { isLoading: isUploading }] = useUploadDocumentMutation()
  const [deleteDocument, { isLoading: isDeleting }] = useDeleteDocumentMutation()
  const [processDocument] = useProcessDocumentMutation()
  const [searchDocuments] = useSearchDocumentsMutation()
  const { data: supportedFormats } = useGetSupportedFormatsQuery()

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      // Auto-fill title from filename if not set
      if (!uploadFormData.title) {
        setUploadFormData(prev => ({
          ...prev,
          title: file.name.replace(/\.[^/.]+$/, '') // Remove extension
        }))
      }
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) return

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('title', uploadFormData.title)
    if (uploadFormData.description) {
      formData.append('description', uploadFormData.description)
    }
    if (uploadFormData.tags) {
      formData.append('tags', uploadFormData.tags)
    }

    try {
      await uploadDocument(formData).unwrap()
      setShowUploadForm(false)
      setSelectedFile(null)
      setUploadFormData({ title: '', description: '', tags: '' })
    } catch (error) {
      console.error('Failed to upload document:', error)
    }
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(id).unwrap()
      } catch (error) {
        console.error('Failed to delete document:', error)
      }
    }
  }

  const handleProcess = async (id: string) => {
    try {
      await processDocument(id).unwrap()
    } catch (error) {
      console.error('Failed to process document:', error)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      const searchRequest: SearchRequest = {
        query: searchQuery,
        limit: 10,
        include_metadata: true
      }
      const result = await searchDocuments(searchRequest).unwrap()
      setSearchResults(result.results)
    } catch (error) {
      console.error('Failed to search documents:', error)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'processed':
        return 'text-green-600'
      case 'processing':
        return 'text-yellow-600'
      case 'failed':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading knowledge base...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error loading knowledge base</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Knowledge Base</h1>
        <Button
          onClick={() => setShowUploadForm(true)}
          disabled={showUploadForm}
          className="flex items-center gap-2"
        >
          <Upload className="w-4 h-4" />
          Upload Document
        </Button>
      </div>

      {/* Upload Form */}
      {showUploadForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpload} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Title"
                  value={uploadFormData.title}
                  onChange={(value) => setUploadFormData(prev => ({ ...prev, title: value }))}
                  required
                />
                <Input
                  label="Tags (comma-separated)"
                  value={uploadFormData.tags}
                  onChange={(value) => setUploadFormData(prev => ({ ...prev, tags: value }))}
                />
              </div>
              
              <Input
                label="Description"
                value={uploadFormData.description}
                onChange={(value) => setUploadFormData(prev => ({ ...prev, description: value }))}
                multiline
                rows={3}
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  File
                </label>
                <input
                  type="file"
                  onChange={handleFileSelect}
                  accept={supportedFormats?.join(',') || '.pdf,.txt,.doc,.docx,.md'}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 dark:file:bg-indigo-900 dark:file:text-indigo-300"
                  required
                />
                {selectedFile && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                  </p>
                )}
                {supportedFormats && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Supported formats: {supportedFormats.join(', ')}
                  </p>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  type="submit"
                  disabled={isUploading || !selectedFile}
                  className="flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  Upload Document
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowUploadForm(false)
                    setSelectedFile(null)
                    setUploadFormData({ title: '', description: '', tags: '' })
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Search Documents</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search in your documents..."
              className="flex-1"
            />
            <Button type="submit" className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              Search
            </Button>
          </form>

          {searchResults.length > 0 && (
            <div className="mt-4 space-y-2">
              <h3 className="font-medium">Search Results</h3>
              {searchResults.map((result, index) => (
                <div key={index} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium">{result.title}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {result.content.substring(0, 200)}...
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Score: {result.score.toFixed(3)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Documents List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documents?.documents.map((document) => (
          <Card key={document.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-lg">{document.title}</CardTitle>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {document.description || 'No description'}
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  <FileText className="w-4 h-4 text-blue-500" />
                  <span className={`text-xs font-medium ${getStatusColor(document.status)}`}>
                    {document.status}
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">File:</span>
                  <span className="font-medium">{document.file_name}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Size:</span>
                  <span className="font-medium">{formatFileSize(document.file_size)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Chunks:</span>
                  <span className="font-medium">{document.chunk_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Tokens:</span>
                  <span className="font-medium">{document.total_tokens.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Created:</span>
                  <span className="font-medium">
                    {new Date(document.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {document.tags.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {document.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded flex items-center gap-1"
                      >
                        <Tag className="w-3 h-3" />
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleProcess(document.id)}
                  disabled={document.status === 'processing'}
                  className="flex items-center gap-1"
                >
                  <Play className="w-3 h-3" />
                  {document.status === 'processing' ? 'Processing...' : 'Process'}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleDelete(document.id)}
                  disabled={isDeleting}
                  className="flex items-center gap-1 text-red-600 hover:text-red-700"
                >
                  <Trash2 className="w-3 h-3" />
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {documents?.documents.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-600 dark:text-gray-400 mb-4">No documents found</p>
            <Button onClick={() => setShowUploadForm(true)}>
              Upload Your First Document
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Knowledge 