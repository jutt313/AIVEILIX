import { useState } from 'react'
import { filesAPI } from '../services/api'

export default function FileUpload({ bucketId, onUploadSuccess }) {
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return

    const allFiles = Array.from(files)
    const batchMeta = {
      count: allFiles.length,
      totalBytes: allFiles.reduce((sum, f) => sum + (f.size || 0), 0),
    }

    setUploading(true)
    try {
      for (const file of allFiles) {
        // Extract folder path from webkitRelativePath if available
        let folderPath = null
        if (file.webkitRelativePath) {
          const pathParts = file.webkitRelativePath.split('/')
          if (pathParts.length > 1) {
            folderPath = pathParts.slice(0, -1).join('/')
          }
        }
        await filesAPI.upload(bucketId, file, folderPath, batchMeta)
      }
      if (onUploadSuccess) onUploadSuccess()
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileUpload(e.dataTransfer.files)
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileUpload(e.target.files)
    }
  }

  return (
    <div>
      <div
        className={`border border-dashed rounded-lg p-6 text-center transition-all duration-300 ${
          dragActive
            ? 'border-[#0B3C49] bg-[#0B3C49]/10'
            : 'border-white/10 hover:border-[#0B3C49]/30'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload-input"
          multiple
          onChange={handleFileInput}
          className="hidden"
          disabled={uploading}
        />
        <input
          type="file"
          id="folder-upload-input"
          webkitdirectory=""
          directory=""
          multiple
          onChange={handleFileInput}
          className="hidden"
          disabled={uploading}
        />
        
        {uploading ? (
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-dark-accent mb-4"></div>
            <p className="dark:text-dark-text text-light-text">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <label
              htmlFor="file-upload-input"
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
              <div className="flex-1 h-px bg-white/10"></div>
              <span className="text-xs dark:text-dark-text/40 text-light-text/40">OR</span>
              <div className="flex-1 h-px bg-white/10"></div>
            </div>

            <label
              htmlFor="folder-upload-input"
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
          </div>
        )}
      </div>
    </div>
  )
}
