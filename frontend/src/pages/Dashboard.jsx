import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { bucketsAPI, filesAPI, teamAPI } from '../services/api'
import StatCard from '../components/StatCard'
import DashboardGraph from '../components/DashboardGraph'
import BucketsTable from '../components/BucketsTable'
import CreateBucketModal from '../components/CreateBucketModal'
import ProfileModal from '../components/ProfileModal'
import Button from '../components/Button'
import NotificationIcon from '../components/NotificationIcon'

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, isTeamMember } = useAuth()
  const { isDark, toggleTheme } = useTheme()
  
  const [stats, setStats] = useState({ total_buckets: 0, total_files: 0, total_storage_bytes: 0 })
  const [buckets, setBuckets] = useState([])
  const [activityData, setActivityData] = useState([])
  const [activityStartDate, setActivityStartDate] = useState(null)
  const [activityEndDate, setActivityEndDate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showProfileModal, setShowProfileModal] = useState(false)
  const [teamMemberCount, setTeamMemberCount] = useState(0)

  const loadData = async () => {
    try {
      setLoading(true)
      const [statsRes, bucketsRes, activityRes] = await Promise.all([
        bucketsAPI.getStats(),
        bucketsAPI.list(),
        bucketsAPI.getActivity(30).catch(() => ({ data: { data: [] } })) // Fallback if endpoint fails
      ])
      console.log('📊 Stats response:', statsRes.data)
      console.log('🪣 Buckets response:', bucketsRes.data)
      console.log('📈 Activity response:', activityRes.data)
      
      setStats(statsRes.data || { total_buckets: 0, total_files: 0, total_storage_bytes: 0 })
      const bucketsList = bucketsRes.data?.buckets || bucketsRes.data || []
      console.log('✅ Setting buckets:', bucketsList)
      setBuckets(bucketsList)
      setActivityData(activityRes.data?.data || [])
    } catch (error) {
      console.error('❌ Failed to load data:', error)
      console.error('Error details:', error.response?.data || error.message)
      // Set defaults on error
      setStats({ total_buckets: 0, total_files: 0, total_storage_bytes: 0 })
      setBuckets([])
      setActivityData([])
    } finally {
      setLoading(false)
    }
  }

  const handleActivityDateRangeChange = async (startDate, endDate) => {
    setActivityStartDate(startDate)
    setActivityEndDate(endDate)
    try {
      const activityRes = await bucketsAPI.getActivity(null, startDate, endDate)
      setActivityData(activityRes.data?.data || [])
    } catch (error) {
      console.error('Failed to load activity data:', error)
      setActivityData([])
    }
  }

  useEffect(() => {
    loadData()
    if (!isTeamMember) {
      teamAPI.listMembers().then(res => {
        const members = res.data?.members || res.data || []
        setTeamMemberCount(members.filter(m => m.is_active).length)
      }).catch(() => {})
    }
  }, [])

  const handleCreateBucket = async (name, description, files = []) => {
    try {
      // Create bucket and get the response with bucket ID
      const createResponse = await bucketsAPI.create(name, description)
      const bucketId = createResponse.data.id
      
      // Upload files if any were provided
      if (files.length > 0) {
        for (const file of files) {
          try {
            // Extract folder path from webkitRelativePath if available
            let folderPath = null
            if (file.webkitRelativePath) {
              const pathParts = file.webkitRelativePath.split('/')
              if (pathParts.length > 1) {
                folderPath = pathParts.slice(0, -1).join('/')
              }
            }
            await filesAPI.upload(bucketId, file, folderPath)
          } catch (error) {
            console.error(`Failed to upload ${file.name}:`, error)
            // Continue with other files even if one fails
          }
        }
      }
      
      await loadData()
    } catch (error) {
      console.error('Failed to create bucket:', error)
      throw error
    }
  }

  const handleDeleteBucket = async (bucketId) => {
    try {
      await bucketsAPI.delete(bucketId)
      await loadData()
    } catch (error) {
      console.error('Failed to delete bucket:', error)
      alert('Failed to delete bucket')
    }
  }

  const handleBucketClick = (bucketId) => {
    navigate(`/buckets/${bucketId}`)
  }

  const formatStorage = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const userName = user?.full_name || user?.email?.split('@')[0] || 'User'

  return (
    <div className={`min-h-screen relative overflow-hidden ${isDark ? 'dark' : ''}`}>
      {/* Fixed Background */}
      <div 
        className="fixed inset-0 -z-10"
        style={{
          backgroundColor: isDark ? '#050B0D' : '#E5F2ED'
        }}
      />

      {/* Header */}
      <header className="relative z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className={`text-2xl font-bold ${isDark ? 'text-dark-accent' : 'text-light-accent'}`}>
              AIveilix
            </h1>
            <span className={`${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
              Welcome, {userName}
            </span>
            {!isTeamMember && teamMemberCount > 0 && (
              <span className={`px-2 py-0.5 rounded-full text-xs ${isDark ? 'bg-dark-accent/20 text-dark-accent' : 'bg-light-accent/20 text-light-accent'}`}>
                {teamMemberCount} team member{teamMemberCount !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-3">
            {/* Notification Icon */}
            <NotificationIcon />

            {/* Profile Icon */}
            <button
              onClick={() => setShowProfileModal(true)}
              className={`p-2 rounded-lg transition-colors ${
                isDark 
                  ? 'hover:bg-white/10 text-dark-text/70' 
                  : 'hover:bg-black/10 text-light-text/70'
              }`}
              title="Profile"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </button>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className={`p-2 rounded-lg transition-colors ${
                isDark 
                  ? 'hover:bg-white/10 text-dark-text/70' 
                  : 'hover:bg-black/10 text-light-text/70'
              }`}
              title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"/>
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 py-8">
        {/* Team Member Banner */}
        {isTeamMember && (
          <div className={`mb-6 p-4 rounded-2xl border ${isDark ? 'bg-dark-accent/10 border-dark-accent/20' : 'bg-light-accent/10 border-light-accent/20'}`}>
            <div className="flex items-center gap-2">
              {user?.team_member_color && (
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: user.team_member_color }} />
              )}
              <span className={`text-sm ${isDark ? 'text-dark-text/70' : 'text-light-text/70'}`}>
                Team member workspace {user?.team_member_name ? `(${user.team_member_name})` : ''}
              </span>
            </div>
          </div>
        )}

        {/* Create Bucket Button - Top Right (owners only) */}
        {!isTeamMember && (
          <div className="flex justify-end mb-6">
            <Button
              variant="primary"
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 text-sm w-auto max-w-[200px]"
            >
              Create New Bucket
            </Button>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className={`animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 ${isDark ? 'border-dark-accent' : 'border-light-accent'}`}></div>
          </div>
        ) : (
          <>
            {/* Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <StatCard
                title="Total Buckets"
                value={stats.total_buckets}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                  </svg>
                }
              />
              <StatCard
                title="Total Files"
                value={stats.total_files}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                }
              />
              <StatCard
                title="Total Storage"
                value={formatStorage(stats.total_storage_bytes)}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                  </svg>
                }
              />
            </div>

            {/* Graph */}
            <div className="mb-8">
              <DashboardGraph 
                data={activityData} 
                onDateRangeChange={handleActivityDateRangeChange}
                startDate={activityStartDate}
                endDate={activityEndDate}
              />
            </div>

            {/* Buckets Table */}
            <div>
              <h2 className={`text-xl font-semibold mb-4 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                Your Buckets
              </h2>
              <BucketsTable
                buckets={buckets}
                onDelete={handleDeleteBucket}
                onBucketClick={handleBucketClick}
              />
            </div>
          </>
        )}
      </main>

      {/* Create Bucket Modal */}
      <CreateBucketModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateBucket}
      />

      {/* Profile Modal */}
      <ProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </div>
  )
}
