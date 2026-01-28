import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import Button from './Button'
import Input from './Input'

export default function CreateBucketModal({ isOpen, onClose, onCreate }) {
  const { isDark } = useTheme()
  const [formData, setFormData] = useState({ name: '', description: '' })
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name.trim()) {
      setError('Bucket name is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      await onCreate(formData.name, formData.description || null, files)
      setFormData({ name: '', description: '' })
      setFiles([])
      onClose()
    } catch (err) {
      setError(err.message || 'Failed to create bucket')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles([...files, ...selectedFiles])
  }

  const handleFolderChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    setFiles([...files, ...selectedFiles])
  }

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm ${
      isDark ? 'bg-black/50' : 'bg-white/50'
    }`}>
      <div className={`w-full max-w-4xl rounded-3xl backdrop-blur-xl border p-8 ${
        isDark 
          ? 'border-white/10 bg-white/5' 
          : 'border-[#1FE0A5]/20 bg-[#F6FFFC]'
      }`}>
        <div className="mb-6">
          <h2 className="text-2xl font-bold dark:text-dark-text text-light-text">
            Create New Bucket
          </h2>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Side - Name & Description */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">
                Bucket Details
              </h3>
              
              <Input
                label="Bucket Name"
                placeholder="My Knowledge Bucket"
                value={formData.name}
                onChange={(e) => {
                  setFormData({ ...formData, name: e.target.value })
                  setError('')
                }}
                required
              />

              <div className="mb-4">
                <label className={`block text-sm font-medium mb-2 ${
                  isDark ? 'text-dark-text' : 'text-[#062A33]'
                }`}>
                  Description (optional)
                </label>
                <textarea
                  placeholder="What's in this bucket?"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={4}
                  className={`w-full px-4 py-3 rounded-xl border resize-none focus:outline-none focus:ring-2 transition-all duration-200 ${
                    isDark 
                      ? 'bg-black/20 border-white/10 text-dark-text placeholder:text-dark-text/40 focus:ring-dark-accent/50' 
                      : 'bg-white/50 border-[#1FE0A5]/20 text-light-text placeholder:text-light-text/40 focus:ring-light-accent/50'
                  }`}
                />
              </div>

              <div className="pt-4">
                <Button
                  type="submit"
                  loading={loading}
                  className="w-full"
                >
                  Create Bucket
                </Button>
              </div>
            </div>

            {/* Right Side - Upload Section */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold dark:text-dark-text text-light-text mb-4">
                Upload Files (Optional)
              </h3>
              
              <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors min-h-[300px] flex flex-col justify-center ${
                isDark 
                  ? 'border-white/10 hover:border-[#0B3C49]/50' 
                  : 'border-[#1FE0A5]/30 hover:border-light-accent'
              }`}>
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                />
                <input
                  type="file"
                  id="folder-upload"
                  webkitdirectory=""
                  directory=""
                  multiple
                  onChange={handleFolderChange}
                  className="hidden"
                />
                <div className="flex flex-col items-center gap-4">
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    <svg className="w-12 h-12 mb-4 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="dark:text-dark-text text-light-text font-medium mb-2">
                      Click to upload files
                    </p>
                    <p className="text-sm dark:text-dark-text/50 text-light-text/50">
                      Any file type
                    </p>
                  </label>
                  
                  <div className="flex items-center gap-2 my-2">
                    <div className={`flex-1 h-px ${
                      isDark ? 'bg-white/10' : 'bg-[#1FE0A5]/20'
                    }`}></div>
                    <span className="text-xs dark:text-dark-text/40 text-light-text/40">OR</span>
                    <div className={`flex-1 h-px ${
                      isDark ? 'bg-white/10' : 'bg-[#1FE0A5]/20'
                    }`}></div>
                  </div>

                  <label
                    htmlFor="folder-upload"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    <svg className="w-12 h-12 mb-4 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <p className="dark:text-dark-text text-light-text font-medium mb-2">
                      Click to upload folder
                    </p>
                    <p className="text-sm dark:text-dark-text/50 text-light-text/50">
                      Upload entire folder with all files
                    </p>
                  </label>

                  <p className="text-xs dark:text-dark-text/40 text-light-text/40 mt-4">
                    You can upload files later
                  </p>
                </div>
              </div>

              {/* File List */}
              {files.length > 0 && (
                <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                  <p className="text-sm font-medium dark:text-dark-text/70 text-light-text/70 mb-2">
                    Selected Files ({files.length})
                  </p>
                  {files.map((file, index) => {
                    // Extract folder path if it exists (from webkitRelativePath)
                    const relativePath = file.webkitRelativePath || file.name
                    const pathParts = relativePath.split('/')
                    const fileName = pathParts[pathParts.length - 1]
                    const folderPath = pathParts.length > 1 ? pathParts.slice(0, -1).join('/') : null
                    
                    return (
                      <div
                        key={index}
                        className={`flex items-center justify-between p-3 rounded-lg border ${
                          isDark 
                            ? 'bg-white/5 border-white/10' 
                            : 'bg-white/50 border-[#1FE0A5]/20'
                        }`}
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {folderPath ? (
                            <svg className="w-5 h-5 flex-shrink-0 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5 flex-shrink-0 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          )}
                          <div className="flex-1 min-w-0">
                            <span className="text-sm dark:text-dark-text text-light-text block truncate">
                              {fileName}
                            </span>
                            {folderPath && (
                              <span className="text-xs dark:text-dark-text/50 text-light-text/50 block truncate">
                                {folderPath}
                              </span>
                            )}
                          </div>
                          <span className="text-xs dark:text-dark-text/50 text-light-text/50 flex-shrink-0 ml-2">
                            {(file.size / 1024).toFixed(1)} KB
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(index)}
                          className="p-1 rounded hover:bg-red-500/10 text-red-400 transition-colors ml-2"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
