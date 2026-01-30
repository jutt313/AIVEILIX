import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import { bucketsAPI, filesAPI } from '../services/api'
import ChatPanel from '../components/ChatPanel'
import FilesCard from '../components/FilesCard'
import ConversationsSidebar from '../components/ConversationsSidebar'

export default function Bucket() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isDark } = useTheme()
  
  const [bucket, setBucket] = useState(null)
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedFiles, setSelectedFiles] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)

  useEffect(() => {
    loadData()
  }, [id])

  // Poll for file status updates when there are pending/processing files
  useEffect(() => {
    const hasPendingFiles = files.some(f => f.status === 'pending' || f.status === 'processing')

    if (!hasPendingFiles) return

    const pollInterval = setInterval(() => {
      filesAPI.list(id).then(res => {
        setFiles(res.data.files || [])
      }).catch(err => {
        console.error('Polling error:', err)
      })
    }, 3000) // Poll every 3 seconds

    return () => clearInterval(pollInterval)
  }, [id, files])

  const loadData = async () => {
    try {
      setLoading(true)
      const [bucketRes, filesRes] = await Promise.all([
        bucketsAPI.get(id),
        filesAPI.list(id)
      ])
      setBucket(bucketRes.data)
      setFiles(filesRes.data.files || [])
    } catch (error) {
      console.error('Failed to load data:', error)
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={`min-h-screen relative overflow-hidden ${isDark ? 'dark' : ''}`}>
        {/* Fixed Background */}
        <div 
          className="fixed inset-0 -z-10"
          style={{
            backgroundColor: isDark ? '#050B0D' : '#E5F2ED'
          }}
        />
        <div className="relative flex items-center justify-center min-h-screen">
          <div className={`animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 ${isDark ? 'border-dark-accent' : 'border-light-accent'}`}></div>
        </div>
      </div>
    )
  }

  if (!bucket) {
    return null
  }

  return (
    <div className={`min-h-screen relative overflow-hidden ${isDark ? 'dark' : ''}`}>
      {/* Fixed Background */}
      <div 
        className="fixed inset-0 -z-10"
        style={{
          backgroundColor: isDark ? '#050B0D' : '#E5F2ED'
        }}
      />
      
      {/* Main Content */}
      <div className="relative h-screen flex gap-4 p-4">
      {/* Conversations Sidebar - Left (includes bucket info, new chat, conversations) */}
      <div className="flex-shrink-0">
        <ConversationsSidebar
          bucket={bucket}
          bucketId={id}
          currentConversationId={currentConversationId}
          onConversationSelect={(convId) => setCurrentConversationId(convId)}
          onNewChat={() => setCurrentConversationId(null)}
        />
      </div>

      {/* Chat Panel - Center */}
      <div className="flex-1 flex flex-col">
        <ChatPanel 
          bucketId={id} 
          conversationId={currentConversationId}
          onConversationCreated={(convId) => setCurrentConversationId(convId)}
          onFilesUpdate={loadData}
          selectedFiles={selectedFiles}
          onSelectedFilesChange={setSelectedFiles}
        />
      </div>

      {/* Files Card - Right */}
      <div className="flex-shrink-0">
        <FilesCard 
          bucketId={id}
          files={files}
          onFilesUpdate={loadData}
          selectedFiles={selectedFiles}
          onFileSelect={(file) => {
            // Toggle file selection
            if (selectedFiles.some(f => f.id === file.id)) {
              setSelectedFiles(selectedFiles.filter(f => f.id !== file.id))
            } else {
              setSelectedFiles([...selectedFiles, file])
            }
          }}
        />
      </div>
      </div>
    </div>
  )
}
