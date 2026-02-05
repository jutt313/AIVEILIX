import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import ConversationsSidebar from '../components/ConversationsSidebar'
import FilesCard from '../components/FilesCard'

export default function BucketUploadGif() {
  const { isDark } = useTheme()
  const [showMenu, setShowMenu] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [files, setFiles] = useState([
    { id: 'f1', name: 'research-plan.pdf', size_bytes: 1829376, folder_path: 'plans' }
  ])

  const bucket = {
    name: 'Research Papers',
    description: 'Academic research and scientific papers'
  }

  useEffect(() => {
    const animate = async () => {
      setShowMenu(false)
      setUploading(false)
      setProgress(0)
      await new Promise(r => setTimeout(r, 700))

      setShowMenu(true)
      await new Promise(r => setTimeout(r, 900))

      setShowMenu(false)
      setUploading(true)
      for (let p = 0; p <= 100; p += 10) {
        setProgress(p)
        await new Promise(r => setTimeout(r, 120))
      }

      setUploading(false)
      setFiles(prev => [
        ...prev,
        { id: `f${prev.length + 1}`, name: 'model-comparison.pdf', size_bytes: 2457600, folder_path: 'papers/2024' }
      ])

      await new Promise(r => setTimeout(r, 1600))
      setFiles([{ id: 'f1', name: 'research-plan.pdf', size_bytes: 1829376, folder_path: 'plans' }])
    }

    animate()
    const interval = setInterval(animate, 8000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative w-full">
      <div className={`relative h-[640px] w-[1200px] max-w-[95vw] overflow-hidden rounded-3xl mx-auto ${isDark ? 'bg-[#050B0D]' : 'bg-[#E5F2ED]'}`}>
        <div className="absolute inset-0 px-4 py-[7px]">
          <div className="relative h-full flex gap-4">
            <div className="flex-shrink-0">
              <ConversationsSidebar
                bucket={bucket}
                bucketId="preview-bucket"
                currentConversationId={null}
                onConversationSelect={() => {}}
                onNewChat={() => {}}
              />
            </div>

            <div className="flex-1 flex flex-col">
              <div className="flex flex-col h-full rounded-2xl backdrop-blur-xl border border-white/5 bg-white/5 p-4 overflow-hidden">
                <div className="flex-1 flex items-center justify-center text-center">
                  <div>
                    <p className="text-sm opacity-70">Start a conversation</p>
                    <p className="text-xs opacity-50">Upload files to begin</p>
                  </div>
                </div>

                <div className="relative pt-3 border-t border-white/10">
                  <div className={`transition-all duration-200 ease-in-out border rounded-3xl flex items-center py-2 ${isDark
                    ? 'bg-white/5 border-white/10'
                    : 'bg-white/50 border-[#1FE0A5]/30'
                    }`}>
                    <div className="relative pl-2 flex-shrink-0">
                      <button
                        type="button"
                        className="p-1.5 rounded-full hover:bg-white/10 transition-colors cursor-pointer"
                        title="Upload files"
                      >
                        {uploading ? (
                          <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-dark-accent"></div>
                        ) : (
                          <svg className={`w-5 h-5 ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                        )}
                      </button>

                      <AnimatePresence>
                        {showMenu && !uploading && (
                          <motion.div
                            initial={{ opacity: 0, y: 6 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 6 }}
                            className={`absolute bottom-full left-0 mb-2 w-48 rounded-lg backdrop-blur-xl border shadow-lg py-2 z-50 ${isDark ? 'bg-black/20 border-white/10' : 'bg-white/90 border-[#1FE0A5]/20'
                              }`}
                          >
                            <div className={`w-full px-4 py-2 text-left text-sm flex items-center gap-2 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                              Upload File
                            </div>
                            <div className={`w-full px-4 py-2 text-left text-sm flex items-center gap-2 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                              Upload Folder
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    <div className="flex-1 min-w-0 px-3 text-sm opacity-60">
                      Ask about your documents...
                    </div>
                    <div className="flex-shrink-0 w-8 h-8 mr-2 rounded-full bg-dark-accent/70" />
                  </div>

                  {uploading && (
                    <div className="mt-3">
                      <div className="h-2 w-full rounded-full bg-white/10 overflow-hidden">
                        <div
                          className="h-full bg-dark-accent transition-all"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                      <div className="mt-1 text-xs opacity-60">Uploading model-comparison.pdf</div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex-shrink-0">
              <FilesCard
                bucketId="preview-bucket"
                files={files}
                onFilesUpdate={() => {}}
                selectedFiles={[]}
                onFileSelect={() => {}}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
