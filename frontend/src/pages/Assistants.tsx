import React, { useState } from 'react'
import { useGetAssistantsQuery, useCreateAssistantMutation, useUpdateAssistantMutation, useDeleteAssistantMutation, useActivateAssistantMutation, useDeactivateAssistantMutation, type Assistant, type AssistantCreate } from '../services/apiSlice'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { Plus, Edit, Trash2, Play, Pause, Settings, Eye } from 'lucide-react'

interface AssistantFormData {
  name: string
  system_prompt: string
  description: string
  personality: string
  instructions: string
  model: string
  temperature: string
  max_tokens: string
  category: string
  tags: string
  is_public: boolean
  is_template: boolean
}

const Assistants: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingAssistant, setEditingAssistant] = useState<Assistant | null>(null)
  const [formData, setFormData] = useState<AssistantFormData>({
    name: '',
    system_prompt: '',
    description: '',
    personality: '',
    instructions: '',
    model: 'gpt-4',
    temperature: '0.7',
    max_tokens: '4096',
    category: '',
    tags: '',
    is_public: false,
    is_template: false,
  })

  const { data: assistants, isLoading, error } = useGetAssistantsQuery({})
  const [createAssistant, { isLoading: isCreating }] = useCreateAssistantMutation()
  const [updateAssistant, { isLoading: isUpdating }] = useUpdateAssistantMutation()
  const [deleteAssistant, { isLoading: isDeleting }] = useDeleteAssistantMutation()
  const [activateAssistant] = useActivateAssistantMutation()
  const [deactivateAssistant] = useDeactivateAssistantMutation()

  const handleInputChange = (field: keyof AssistantFormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const assistantData: AssistantCreate = {
      name: formData.name,
      system_prompt: formData.system_prompt,
      description: formData.description || undefined,
      personality: formData.personality || undefined,
      instructions: formData.instructions || undefined,
      model: formData.model,
      temperature: formData.temperature,
      max_tokens: formData.max_tokens,
      category: formData.category || undefined,
      tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : [],
      is_public: formData.is_public,
      is_template: formData.is_template,
    }

    try {
      if (editingAssistant) {
        await updateAssistant({ id: editingAssistant.id, data: assistantData }).unwrap()
        setEditingAssistant(null)
      } else {
        await createAssistant(assistantData).unwrap()
        setShowCreateForm(false)
      }
      
      // Reset form
      setFormData({
        name: '',
        system_prompt: '',
        description: '',
        personality: '',
        instructions: '',
        model: 'gpt-4',
        temperature: '0.7',
        max_tokens: '4096',
        category: '',
        tags: '',
        is_public: false,
        is_template: false,
      })
    } catch (error) {
      console.error('Failed to save assistant:', error)
    }
  }

  const handleEdit = (assistant: Assistant) => {
    setEditingAssistant(assistant)
    setFormData({
      name: assistant.name,
      system_prompt: assistant.system_prompt,
      description: assistant.description || '',
      personality: assistant.personality || '',
      instructions: assistant.instructions || '',
      model: assistant.model,
      temperature: assistant.temperature,
      max_tokens: assistant.max_tokens,
      category: assistant.category || '',
      tags: assistant.tags.join(', '),
      is_public: assistant.is_public,
      is_template: assistant.is_template,
    })
  }

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this assistant?')) {
      try {
        await deleteAssistant(id).unwrap()
      } catch (error) {
        console.error('Failed to delete assistant:', error)
      }
    }
  }

  const handleToggleStatus = async (assistant: Assistant) => {
    try {
      if (assistant.is_active) {
        await deactivateAssistant(assistant.id).unwrap()
      } else {
        await activateAssistant(assistant.id).unwrap()
      }
    } catch (error) {
      console.error('Failed to toggle assistant status:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading assistants...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error loading assistants</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Assistant Management</h1>
        <Button
          onClick={() => setShowCreateForm(true)}
          disabled={showCreateForm}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create Assistant
        </Button>
      </div>

      {/* Create/Edit Form */}
      {(showCreateForm || editingAssistant) && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>{editingAssistant ? 'Edit Assistant' : 'Create New Assistant'}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Name"
                  value={formData.name}
                  onChange={(value) => handleInputChange('name', value)}
                  required
                />
                <Input
                  label="Model"
                  value={formData.model}
                  onChange={(value) => handleInputChange('model', value)}
                  required
                />
                <Input
                  label="Category"
                  value={formData.category}
                  onChange={(value) => handleInputChange('category', value)}
                />
                <Input
                  label="Tags (comma-separated)"
                  value={formData.tags}
                  onChange={(value) => handleInputChange('tags', value)}
                />
                <Input
                  label="Temperature"
                  value={formData.temperature}
                  onChange={(value) => handleInputChange('temperature', value)}
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                />
                <Input
                  label="Max Tokens"
                  value={formData.max_tokens}
                  onChange={(value) => handleInputChange('max_tokens', value)}
                  type="number"
                  min="1"
                />
              </div>
              
              <Input
                label="Description"
                value={formData.description}
                onChange={(value) => handleInputChange('description', value)}
                multiline
                rows={2}
              />
              
              <Input
                label="System Prompt"
                value={formData.system_prompt}
                onChange={(value) => handleInputChange('system_prompt', value)}
                multiline
                rows={4}
                required
              />
              
              <Input
                label="Personality"
                value={formData.personality}
                onChange={(value) => handleInputChange('personality', value)}
                multiline
                rows={3}
              />
              
              <Input
                label="Instructions"
                value={formData.instructions}
                onChange={(value) => handleInputChange('instructions', value)}
                multiline
                rows={3}
              />

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_public}
                    onChange={(e) => handleInputChange('is_public', e.target.checked)}
                    className="rounded"
                  />
                  <span>Public Assistant</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_template}
                    onChange={(e) => handleInputChange('is_template', e.target.checked)}
                    className="rounded"
                  />
                  <span>Template</span>
                </label>
              </div>

              <div className="flex gap-2">
                <Button
                  type="submit"
                  disabled={isCreating || isUpdating}
                  className="flex items-center gap-2"
                >
                  {editingAssistant ? 'Update Assistant' : 'Create Assistant'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowCreateForm(false)
                    setEditingAssistant(null)
                    setFormData({
                      name: '',
                      system_prompt: '',
                      description: '',
                      personality: '',
                      instructions: '',
                      model: 'gpt-4',
                      temperature: '0.7',
                      max_tokens: '4096',
                      category: '',
                      tags: '',
                      is_public: false,
                      is_template: false,
                    })
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Assistants List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {assistants?.map((assistant) => (
          <Card key={assistant.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <CardTitle className="text-lg">{assistant.name}</CardTitle>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {assistant.description || 'No description'}
                  </p>
                </div>
                <div className="flex items-center gap-1">
                  {assistant.is_public && <Eye className="w-4 h-4 text-blue-500" />}
                  {assistant.is_template && <Settings className="w-4 h-4 text-purple-500" />}
                  <div className={`w-2 h-2 rounded-full ${assistant.is_active ? 'bg-green-500' : 'bg-gray-400'}`} />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Model:</span>
                  <span className="font-medium">{assistant.model}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Status:</span>
                  <span className={`font-medium ${assistant.is_active ? 'text-green-600' : 'text-gray-600'}`}>
                    {assistant.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Tools:</span>
                  <span className="font-medium">{assistant.tool_count}</span>
                </div>
                {assistant.category && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Category:</span>
                    <span className="font-medium">{assistant.category}</span>
                  </div>
                )}
              </div>

              {assistant.tags.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {assistant.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                      >
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
                  onClick={() => handleEdit(assistant)}
                  className="flex items-center gap-1"
                >
                  <Edit className="w-3 h-3" />
                  Edit
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleToggleStatus(assistant)}
                  className="flex items-center gap-1"
                >
                  {assistant.is_active ? (
                    <>
                      <Pause className="w-3 h-3" />
                      Deactivate
                    </>
                  ) : (
                    <>
                      <Play className="w-3 h-3" />
                      Activate
                    </>
                  )}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleDelete(assistant.id)}
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

      {assistants?.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <p className="text-gray-600 dark:text-gray-400 mb-4">No assistants found</p>
            <Button onClick={() => setShowCreateForm(true)}>
              Create Your First Assistant
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Assistants 