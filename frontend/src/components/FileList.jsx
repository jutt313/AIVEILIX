export default function FileList({ files, onDelete }) {
  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready':
        return 'text-green-400'
      case 'processing':
        return 'text-yellow-400'
      case 'failed':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  if (files.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="dark:text-dark-text/70 text-light-text/70">
          No files uploaded yet. Upload files to get started!
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2 max-h-[400px] overflow-y-auto">
      {files.map((file) => (
        <div
          key={file.id}
          className="flex items-center justify-between p-3 rounded-lg hover:bg-white/5 transition-all"
        >
          <div className="flex items-center gap-3 flex-1 min-w-0">
            <svg className="w-6 h-6 flex-shrink-0 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div className="flex-1 min-w-0">
              <p className="dark:text-dark-text text-light-text font-medium truncate">
                {file.name}
              </p>
              <div className="flex items-center gap-3 mt-1 text-xs dark:text-dark-text/50 text-light-text/50">
                <span>{formatSize(file.size_bytes)}</span>
                {file.word_count && <span>• {file.word_count.toLocaleString()} words</span>}
                <span className={getStatusColor(file.status)}>• {file.status}</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => onDelete(file.id)}
            className="p-2 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors ml-2"
            title="Delete file"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  )
}
