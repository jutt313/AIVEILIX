import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import { filesAPI } from '../services/api'

export default function FilesCard({ bucketId, files, onFilesUpdate, onFileSelect, selectedFiles = [], canDelete = true }) {
  const { isDark } = useTheme()
  const [expandedFolders, setExpandedFolders] = useState(new Set())
  const [isCollapsed, setIsCollapsed] = useState(false)

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
      alert('Failed to delete file: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleFileClick = (file) => {
    if (onFileSelect) {
      onFileSelect(file)
    }
  }

  const handleDownloadCreatedFile = async (file, e) => {
    e.stopPropagation()
    try {
      const response = await filesAPI.getContent(bucketId, file.id)
      const content = response.data?.content ?? ''
      if (!content) {
        alert('File is still processing or empty.')
        return
      }
      const blob = new Blob([content], { type: file.mime_type || 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
      alert('Failed to download file: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleOpenCreatedFile = async (file, e) => {
    e.stopPropagation()
    try {
      const response = await filesAPI.getContent(bucketId, file.id)
      const content = response.data?.content ?? ''
      if (!content) {
        alert('File is still processing or empty.')
        return
      }
      const blob = new Blob([content], { type: file.mime_type || 'text/plain' })
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank', 'noopener,noreferrer')
      setTimeout(() => URL.revokeObjectURL(url), 30000)
    } catch (error) {
      console.error('Open failed:', error)
      alert('Failed to open file: ' + (error.response?.data?.detail || error.message))
    }
  }

  const isSelected = (fileId) => {
    return selectedFiles.some(f => f.id === fileId)
  }

  const isFolderSelected = (folderFiles) => {
    return folderFiles.length > 0 && folderFiles.every(file => isSelected(file.id))
  }

  const toggleFolder = (folderPath, e) => {
    if (e) e.stopPropagation()
    const newExpanded = new Set(expandedFolders)
    if (newExpanded.has(folderPath)) {
      newExpanded.delete(folderPath)
    } else {
      newExpanded.add(folderPath)
    }
    setExpandedFolders(newExpanded)
  }

  const handleFolderSelect = (folderFiles) => {
    if (!onFileSelect) return

    const allSelected = isFolderSelected(folderFiles)

    if (allSelected) {
      folderFiles.forEach(file => {
        onFileSelect(file)
      })
    } else {
      folderFiles.forEach(file => {
        if (!selectedFiles.some(f => f.id === file.id)) {
          onFileSelect(file)
        }
      })
    }
  }

  // Build folder tree structure
  const buildFolderTree = (files) => {
    const tree = { children: {}, files: [] }
    const rootFiles = []

    files.forEach(file => {
      if (file.folder_path) {
        const parts = file.folder_path.split('/')
        let current = tree
        let currentPath = ''

        parts.forEach((part, index) => {
          currentPath = currentPath ? `${currentPath}/${part}` : part
          if (!current.children[part]) {
            current.children[part] = {
              name: part,
              path: currentPath,
              children: {},
              files: []
            }
          }
          current = current.children[part]
        })

        current.files.push(file)
      } else {
        rootFiles.push(file)
      }
    })

    return { tree, rootFiles }
  }

  // Recursive folder component
  const FolderNode = ({ folder, level = 0 }) => {
    const folderPath = folder.path
    const isExpanded = expandedFolders.has(folderPath)
    const folderSelected = isFolderSelected(folder.files)
    const childFolders = Object.values(folder.children)
    const hasChildren = childFolders.length > 0 || folder.files.length > 0

    const allFilesInFolder = [
      ...folder.files,
      ...childFolders.flatMap(child => getAllFilesInFolder(child))
    ]

    return (
      <div className="space-y-1">
        {/* Folder Header */}
        <div
          className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${folderSelected
            ? isDark
              ? 'bg-dark-accent/20 border border-dark-accent/50'
              : 'bg-[#1FE0A5]/20 border border-[#1FE0A5]/50'
            : isDark
              ? 'hover:bg-white/5'
              : 'hover:bg-black/5'
            }`}
          style={{ marginLeft: `${level * 16}px` }}
        >
          <div
            onClick={(e) => {
              e.stopPropagation()
              toggleFolder(folderPath, e)
            }}
            className="flex items-center gap-1"
          >
            {hasChildren ? (
              <svg
                className={`w-4 h-4 flex-shrink-0 dark:text-dark-accent text-light-accent transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            ) : (
              <div className="w-4 h-4" />
            )}
            {folderSelected ? (
              <div className="w-4 h-4 flex-shrink-0 rounded-full bg-dark-accent flex items-center justify-center">
                <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            ) : (
              <svg className="w-4 h-4 flex-shrink-0 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            )}
          </div>
          <div
            onClick={() => handleFolderSelect(allFilesInFolder)}
            className="flex items-center gap-2 flex-1"
          >
            <span className={`text-sm font-medium ${folderSelected
              ? isDark ? 'text-dark-accent' : 'text-light-accent'
              : isDark ? 'text-dark-text' : 'text-[#062A33]'
              }`}>
              {folder.name}
            </span>
            <span className={`text-xs ml-auto ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
              }`}>
              {allFilesInFolder.length} file{allFilesInFolder.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="space-y-1">
            {/* Child Folders */}
            {childFolders.map(childFolder => (
              <FolderNode key={childFolder.path} folder={childFolder} level={level + 1} />
            ))}

            {/* Files in this folder */}
            {folder.files.map((file) => {
              const selected = isSelected(file.id)
              return (
                <div
                  key={file.id}
                  onClick={() => handleFileClick(file)}
                  className={`group flex items-center justify-between p-2 rounded-lg transition-colors cursor-pointer ${selected
                    ? isDark
                      ? 'bg-dark-accent/20 border border-dark-accent/50'
                      : 'bg-[#1FE0A5]/20 border border-[#1FE0A5]/50'
                    : isDark
                      ? 'hover:bg-white/5'
                      : 'hover:bg-black/5'
                    }`}
                  style={{ marginLeft: `${(level + 1) * 16}px` }}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {selected ? (
                      <div className={`w-4 h-4 flex-shrink-0 rounded-full flex items-center justify-center ${isDark ? 'bg-dark-accent' : 'bg-light-accent'
                        }`}>
                        <svg className="w-2.5 h-2.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    ) : (
                      <svg className={`w-4 h-4 flex-shrink-0 ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                        }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm truncate ${selected
                        ? isDark
                          ? 'text-dark-accent font-medium'
                          : 'text-light-accent font-medium'
                        : isDark
                          ? 'text-dark-text'
                          : 'text-[#062A33]'
                        }`}>
                        {file.name}
                      </p>
                      <p className={`text-xs ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                        }`}>
                        {formatSize(file.size_bytes)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {/* Delete button */}
                    <button
                      onClick={(e) => handleDeleteFile(file.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/10 text-red-400 transition-all"
                      title="Delete file"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  // Helper to get all files recursively from a folder
  const getAllFilesInFolder = (folder) => {
    const files = [...folder.files]
    Object.values(folder.children).forEach(child => {
      files.push(...getAllFilesInFolder(child))
    })
    return files
  }

  const createdFiles = files.filter(file => file.source === 'created')
  const uploadedFiles = files.filter(file => file.source !== 'created')
  const { tree, rootFiles } = buildFolderTree(uploadedFiles)
  const rootFolders = Object.values(tree.children).sort((a, b) => a.name.localeCompare(b.name))

  return (
    <div className={`h-full rounded-2xl backdrop-blur-xl flex flex-col transition-all duration-300 ${isDark ? 'bg-white/5' : 'bg-black/5'
      } ${isCollapsed ? 'w-16' : 'w-80'}`}>
      {/* Header with collapse button */}
      <div className="p-4 flex items-center justify-between">
        {!isCollapsed && (
          <h3 className={`font-semibold ${isDark ? 'text-dark-text' : 'text-[#062A33]'
            }`}>Files & Folders</h3>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={`p-1.5 rounded transition-colors ml-auto ${isDark ? 'hover:bg-white/10' : 'hover:bg-black/10'
            }`}
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          <svg
            className={`w-5 h-5 transition-transform ${isCollapsed ? 'rotate-180' : ''
              } ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Files List - Only show when not collapsed */}
      {!isCollapsed && (
        <div className="flex-1 overflow-y-auto px-3">
          {files.length === 0 ? (
            <div className="text-center py-12">
              <p className={`text-sm ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                }`}>
                No files yet
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              {createdFiles.length > 0 && (
                <div className="pt-1">
                  <p className={`px-2 pb-1 text-[11px] uppercase tracking-wide ${isDark ? 'text-dark-text/40' : 'text-[#062A33]/40'
                    }`}>
                    Created Files
                  </p>
                  {createdFiles.map((file) => {
                    const selected = isSelected(file.id)
                    return (
                      <div
                        key={file.id}
                        onClick={() => handleFileClick(file)}
                        className={`group flex items-center justify-between p-3 rounded-lg transition-colors cursor-pointer ${selected
                          ? isDark
                            ? 'bg-dark-accent/20 border border-dark-accent/50'
                            : 'bg-[#1FE0A5]/20 border border-[#1FE0A5]/50'
                          : isDark
                            ? 'hover:bg-white/5'
                            : 'hover:bg-black/5'
                          }`}
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {selected ? (
                            <div className={`w-5 h-5 flex-shrink-0 rounded-full flex items-center justify-center ${isDark ? 'bg-dark-accent' : 'bg-light-accent'
                              }`}>
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          ) : (
                            <svg className={`w-5 h-5 flex-shrink-0 ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                              }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          )}
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm truncate font-medium ${selected
                              ? isDark
                                ? 'text-dark-accent'
                                : 'text-light-accent'
                              : isDark
                                ? 'text-dark-text'
                                : 'text-[#062A33]'
                              }`}>
                              {file.name}
                            </p>
                            <p className={`text-xs ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                              }`}>
                              {formatSize(file.size_bytes)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={(e) => handleDownloadCreatedFile(file, e)}
                            className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-white/10 text-blue-400 transition-all"
                            title="Download file"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4" />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => handleOpenCreatedFile(file, e)}
                            className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-white/10 text-emerald-400 transition-all"
                            title="Open in new tab"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 3h7v7m0-7L10 14m-4 7h12a2 2 0 002-2V9" />
                            </svg>
                          </button>
                          <button
                            onClick={(e) => handleDeleteFile(file.id, e)}
                            className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-red-500/10 text-red-400 transition-all"
                            title="Delete file"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              {(rootFolders.length > 0 || rootFiles.length > 0) && (
                <div className="pt-2">
                  <p className={`px-2 pb-1 text-[11px] uppercase tracking-wide ${isDark ? 'text-dark-text/40' : 'text-[#062A33]/40'
                    }`}>
                    Uploaded Files
                  </p>
                  {/* Root Folders (recursive tree) */}
                  {rootFolders.map(folder => (
                    <FolderNode key={folder.path} folder={folder} level={0} />
                  ))}

                  {/* Root Files (files without folder_path) */}
                  {rootFiles.map((file) => {
                    const selected = isSelected(file.id)
                    return (
                      <div
                        key={file.id}
                        onClick={() => handleFileClick(file)}
                        className={`group flex items-center justify-between p-3 rounded-lg transition-colors cursor-pointer ${selected
                          ? isDark
                            ? 'bg-dark-accent/20 border border-dark-accent/50'
                            : 'bg-[#1FE0A5]/20 border border-[#1FE0A5]/50'
                          : isDark
                            ? 'hover:bg-white/5'
                            : 'hover:bg-black/5'
                          }`}
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {selected ? (
                            <div className={`w-5 h-5 flex-shrink-0 rounded-full flex items-center justify-center ${isDark ? 'bg-dark-accent' : 'bg-light-accent'
                              }`}>
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            </div>
                          ) : (
                            <svg className={`w-5 h-5 flex-shrink-0 ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                              }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          )}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1.5">
                              {file.uploaded_by_color && (
                                <div
                                  className="w-2 h-2 rounded-full flex-shrink-0"
                                  style={{ backgroundColor: file.uploaded_by_color }}
                                  title={file.uploaded_by_name || ''}
                                />
                              )}
                              <p className={`text-sm truncate font-medium ${selected
                                ? isDark
                                  ? 'text-dark-accent'
                                  : 'text-light-accent'
                                : isDark
                                  ? 'text-dark-text'
                                  : 'text-[#062A33]'
                                }`}>
                                {file.name}
                              </p>
                            </div>
                            <p className={`text-xs ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'
                              }`}>
                              {formatSize(file.size_bytes)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          {canDelete && (
                            <button
                              onClick={(e) => handleDeleteFile(file.id, e)}
                              className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-red-500/10 text-red-400 transition-all"
                              title="Delete file"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      )}

    </div>
  )
}
