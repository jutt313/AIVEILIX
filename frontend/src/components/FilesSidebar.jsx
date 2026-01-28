import { useState } from 'react'
import { filesAPI } from '../services/api'
import FilePreviewModal from './FilePreviewModal'
import { useTheme } from '../context/ThemeContext'

export default function FilesSidebar({ bucketId, files, onFilesUpdate, categories = [] }) {
  const { isDark } = useTheme()
  const [uploading, setUploading] = useState(false)
  const [previewFile, setPreviewFile] = useState(null)

  const handleFileUpload = async (fileList) => {
    if (!fileList || fileList.length === 0) return

    setUploading(true)
    try {
      for (const file of Array.from(fileList)) {
        // Extract folder path from webkitRelativePath if available
        let folderPath = null
        if (file.webkitRelativePath) {
          const pathParts = file.webkitRelativePath.split('/')
          if (pathParts.length > 1) {
            folderPath = pathParts.slice(0, -1).join('/')
          }
        }
        await filesAPI.upload(bucketId, file, folderPath)
      }
      if (onFilesUpdate) onFilesUpdate()
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files)
    }
  }

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const handleDeleteFile = async (fileId, e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this file?')) return
    try {
      await filesAPI.delete(bucketId, fileId)
      if (onFilesUpdate) onFilesUpdate()
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }

  return (
    <div className="h-full flex flex-col border-l border-white/5">
      {/* Header */}
      <div className="p-4 border-b border-white/5">
        <h3 className="font-semibold dark:text-dark-text text-light-text mb-3">Files</h3>
        
        {/* Upload Button */}
        <input
          type="file"
          id="sidebar-file-upload"
          multiple
          onChange={handleFileInput}
          className="hidden"
          disabled={uploading}
        />
        <input
          type="file"
          id="sidebar-folder-upload"
          webkitdirectory=""
          directory=""
          multiple
          onChange={handleFileInput}
          className="hidden"
          disabled={uploading}
        />
        
        <div className="flex gap-2">
          <label
            htmlFor="sidebar-file-upload"
            className="flex-1 px-3 py-2 text-sm rounded-lg cursor-pointer transition-colors text-center bg-[#0B3C49] text-white hover:bg-[#0B3C49]/80"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </label>
          <label
            htmlFor="sidebar-folder-upload"
            className="px-3 py-2 text-sm rounded-lg bg-white/5 hover:bg-white/10 dark:text-dark-text text-light-text cursor-pointer transition-colors"
            title="Upload folder"
          >
            📁
          </label>
        </div>
      </div>

      {/* Categories (if any) */}
      {categories.length > 0 && (
        <div className="p-4 border-b border-white/5">
          <h4 className="text-xs font-medium dark:text-dark-text/70 text-light-text/70 mb-2 uppercase">Categories</h4>
          <div className="space-y-1">
            {categories.map((cat) => (
              <div
                key={cat.id}
                className="px-2 py-1.5 rounded text-sm dark:text-dark-text/70 text-light-text/70 hover:bg-white/5 cursor-pointer"
              >
                {cat.name}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Files List */}
      <div className="flex-1 overflow-y-auto p-2">
        {files.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm dark:text-dark-text/50 text-light-text/50">
              No files yet
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {files.map((file) => (
              <div
                key={file.id}
                className="group flex items-center justify-between p-2 rounded hover:bg-white/5 transition-colors cursor-pointer"
                onClick={() => setPreviewFile(file)}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <svg className="w-4 h-4 flex-shrink-0 dark:text-dark-text/50 text-light-text/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm dark:text-dark-text text-light-text truncate">
                      {file.name}
                    </p>
                    <p className="text-xs dark:text-dark-text/50 text-light-text/50">
                      {formatSize(file.size_bytes)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {/* Preview button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setPreviewFile(file)
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-white/10 dark:text-dark-text/70 text-light-text/70 transition-all"
                    title="Preview file"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  {/* Delete button */}
                  <button
                    onClick={(e) => handleDeleteFile(file.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/10 text-red-400 transition-all"
                    title="Delete file"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File Preview Modal */}
      <FilePreviewModal
        isOpen={!!previewFile}
        onClose={() => setPreviewFile(null)}
        bucketId={bucketId}
        file={previewFile}
      />
    </div>
  )
}
