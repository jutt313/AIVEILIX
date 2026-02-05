import DashboardGraph from './DashboardGraph'
import BucketsTable from './BucketsTable'

const DashboardPreview = () => {
  // Mock data
  const mockStats = {
    total_buckets: 12,
    total_files: 248,
    total_storage_bytes: 536870912 // 512 MB
  }

  const mockBuckets = [
    {
      id: '1',
      name: 'Research Papers',
      description: 'Academic research and scientific papers',
      file_count: 45,
      total_size_bytes: 125829120,
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: '2',
      name: 'Project Documentation',
      description: 'Technical docs and specifications',
      file_count: 89,
      total_size_bytes: 209715200,
      created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: '3',
      name: 'Code Snippets',
      description: 'Useful code examples and templates',
      file_count: 67,
      total_size_bytes: 47185920,
      created_at: new Date(Date.now() - 21 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: '4',
      name: 'Meeting Notes',
      description: 'Team meetings and brainstorming sessions',
      file_count: 34,
      total_size_bytes: 29360128,
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
    },
    {
      id: '5',
      name: 'Design Assets',
      description: 'UI/UX designs and brand materials',
      file_count: 13,
      total_size_bytes: 124780544,
      created_at: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString()
    }
  ]

  const mockActivityData = [
    { date: '2024-01-01', buckets: 5, files: 120, storage: 200 },
    { date: '2024-01-08', buckets: 7, files: 165, storage: 285 },
    { date: '2024-01-15', buckets: 9, files: 198, storage: 380 },
    { date: '2024-01-22', buckets: 11, files: 225, storage: 450 },
    { date: '2024-01-29', buckets: 12, files: 248, storage: 512 }
  ]

  const formatStorage = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="relative overflow-hidden" style={{ backgroundColor: '#050B0D' }}>

      {/* Header */}
      <header className="relative z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-dark-accent">
              AIveilix
            </h1>
            <span className="text-dark-text/70">
              Welcome, Sarah Mitchell
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Notification Icon (mock) */}
            <button
              className="p-2 rounded-lg transition-colors hover:bg-white/10 text-dark-text/70 relative"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] text-white flex items-center justify-center">
                3
              </span>
            </button>

            {/* Profile Icon (mock) */}
            <button
              className="p-2 rounded-lg transition-colors hover:bg-white/10 text-dark-text/70"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>

            {/* Theme Toggle (mock - sun icon) */}
            <button
              className="p-2 rounded-lg transition-colors hover:bg-white/10 text-dark-text/70"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"/>
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-8 pb-12">
        {/* Create Bucket Button */}
        <div className="flex justify-end mb-6">
          <button
            className="px-4 py-2 text-sm rounded-lg font-medium transition-all duration-200 bg-dark-accent text-dark-bg hover:opacity-90"
          >
            Create New Bucket
          </button>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="rounded-xl p-6 backdrop-blur-xl border border-white/10 bg-white/5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-dark-text/70">Total Buckets</h3>
              <svg className="w-6 h-6 text-dark-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-dark-text">{mockStats.total_buckets}</p>
          </div>
          <div className="rounded-xl p-6 backdrop-blur-xl border border-white/10 bg-white/5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-dark-text/70">Total Files</h3>
              <svg className="w-6 h-6 text-dark-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-dark-text">{mockStats.total_files}</p>
          </div>
          <div className="rounded-xl p-6 backdrop-blur-xl border border-white/10 bg-white/5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-dark-text/70">Total Storage</h3>
              <svg className="w-6 h-6 text-dark-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
            <p className="text-3xl font-bold text-dark-text">{formatStorage(mockStats.total_storage_bytes)}</p>
          </div>
        </div>

        {/* Graph */}
        <div className="mb-8">
          <DashboardGraph
            data={mockActivityData}
            onDateRangeChange={() => {}}
            startDate={null}
            endDate={null}
          />
        </div>

        {/* Buckets Table */}
        <div>
          <h2 className="text-xl font-semibold mb-4 text-dark-text">
            Your Buckets
          </h2>
          <BucketsTable
            buckets={mockBuckets}
            onDelete={() => {}}
            onBucketClick={() => {}}
          />
        </div>
      </main>
    </div>
  )
}

export default DashboardPreview
