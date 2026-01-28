import { useTheme } from '../context/ThemeContext'

export default function BucketsTable({ buckets, onDelete, onBucketClick }) {
  const { isDark } = useTheme()
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  const formatStorage = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const handleDelete = async (e, bucketId) => {
    e.stopPropagation()
    if (window.confirm('Are you sure you want to delete this bucket? All files will be deleted.')) {
      await onDelete(bucketId)
    }
  }

  if (buckets.length === 0) {
    return (
      <div className={`rounded-xl p-12 backdrop-blur-xl border text-center transition-all duration-300 ${
        isDark
          ? 'border-white/10 bg-white/5 hover:border-[#0B3C49]/50 hover:bg-[#0B3C49]/5'
          : 'border-light-accent/20 bg-light-surface hover:border-light-accent hover:bg-light-accent/5'
      }`}>
        <p className={isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}>
          No buckets yet. Create your first bucket to get started!
        </p>
      </div>
    )
  }

  return (
    <div className={`rounded-xl backdrop-blur-xl border overflow-hidden ${
      isDark
        ? 'border-white/10 bg-white/5'
        : 'border-light-accent/20 bg-light-surface'
    }`}>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className={`${isDark ? 'border-b border-white/10' : 'border-b border-light-accent/20'}`}>
              <th className={`px-6 py-4 text-left text-xs font-medium uppercase tracking-wider ${
                isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
              }`}>
                Name
              </th>
              <th className={`px-6 py-4 text-left text-xs font-medium uppercase tracking-wider ${
                isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
              }`}>
                ID
              </th>
              <th className={`px-6 py-4 text-left text-xs font-medium uppercase tracking-wider ${
                isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
              }`}>
                Created At
              </th>
              <th className={`px-6 py-4 text-left text-xs font-medium uppercase tracking-wider ${
                isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
              }`}>
                Files
              </th>
              <th className={`px-6 py-4 text-left text-xs font-medium uppercase tracking-wider ${
                isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
              }`}>
                Storage
              </th>
              <th className={`px-6 py-4 text-right text-xs font-medium uppercase tracking-wider ${
                isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
              }`}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody className={`${isDark ? 'divide-y divide-white/10' : 'divide-y divide-light-accent/20'}`}>
            {buckets.map((bucket) => (
              <tr
                key={bucket.id}
                onClick={() => onBucketClick(bucket.id)}
                className={`cursor-pointer transition-all duration-300 group ${
                  isDark ? 'hover:bg-[#0B3C49]/10' : 'hover:bg-light-accent/10'
                }`}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`font-medium transition-colors ${
                    isDark 
                      ? 'text-dark-text group-hover:text-[#0B3C49]' 
                      : 'text-[#062A33] group-hover:text-light-accent'
                  }`}>
                    {bucket.name}
                  </div>
                  {bucket.description && (
                    <div className={`text-sm mt-1 ${
                      isDark ? 'text-dark-text/50' : 'text-[#062A33]/60'
                    }`}>
                      {bucket.description}
                    </div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <code className={`text-xs font-mono ${
                    isDark ? 'text-dark-text/50' : 'text-[#062A33]/60'
                  }`}>
                    {bucket.id.slice(0, 8)}...
                  </code>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                  isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'
                }`}>
                  {formatDate(bucket.created_at)}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap ${
                  isDark ? 'text-dark-text' : 'text-[#062A33]'
                }`}>
                  {bucket.file_count}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap ${
                  isDark ? 'text-dark-text' : 'text-[#062A33]'
                }`}>
                  {formatStorage(bucket.total_size_bytes)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <button
                    onClick={(e) => handleDelete(e, bucket.id)}
                    className="p-2 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
                    title="Delete bucket"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
