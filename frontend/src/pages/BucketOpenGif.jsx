import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import ConversationsSidebar from '../components/ConversationsSidebar'
import FilesCard from '../components/FilesCard'

export default function BucketOpenGif() {
  const { isDark } = useTheme()
  const [selectedFiles, setSelectedFiles] = useState([])
  const [pulse, setPulse] = useState(false)
  const [visibleCount, setVisibleCount] = useState(0)

  const bucket = {
    name: 'Research Papers',
    description: 'Academic research and scientific papers'
  }

  const files = [
    { id: 'f1', name: 'model-comparison.pdf', size_bytes: 2457600, folder_path: 'papers/2024' },
    { id: 'f2', name: 'experiment-notes.md', size_bytes: 98304, folder_path: 'notes' },
    { id: 'f3', name: 'results.csv', size_bytes: 412876, folder_path: '' }
  ]

  useEffect(() => {
    const animate = async () => {
      setPulse(true)
      await new Promise(r => setTimeout(r, 900))
      setPulse(false)
      await new Promise(r => setTimeout(r, 1100))
    }

    animate()
    const interval = setInterval(animate, 4000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const sequence = async () => {
      const steps = 6
      for (let i = 1; i <= steps; i++) {
        setVisibleCount(i)
        await new Promise(r => setTimeout(r, 800))
      }
      await new Promise(r => setTimeout(r, 1400))
      setVisibleCount(0)
    }
    sequence()
    const interval = setInterval(sequence, 7600)
    return () => clearInterval(interval)
  }, [])

  const messages = [
    { role: 'user', content: 'Summarize the key findings in model-comparison.pdf.' },
    { role: 'assistant', content: 'Searching “AIveilix model comparison” and local documents…', isSearch: true },
    { role: 'assistant', content: 'Top results: Model A leads on accuracy, Model B on latency, Model C on cost. Your paper favors Model A for research workflows.' },
    { role: 'user', content: 'Any notes about limitations or bias?' },
    { role: 'assistant', content: 'Yes. The study notes dataset bias toward academic corpora and limited multilingual evaluation. It recommends follow‑up tests on production logs.' }
  ]

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
              <div className="flex-1 overflow-y-auto space-y-4 pr-2">
                <AnimatePresence>
                  {messages.slice(0, visibleCount).map((msg, idx) => (
                    <motion.div
                      key={`${msg.role}-${idx}`}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 text-sm ${
                          msg.role === 'user'
                            ? 'bg-[#0B3C49] text-white'
                            : isDark ? 'text-dark-text' : 'text-light-text'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.content}</p>
                        {msg.isSearch && (
                          <div className="mt-2 text-xs opacity-70">Searching web and local docs…</div>
                        )}
                        {msg.role === 'assistant' && !msg.isSearch && (
                          <div className="mt-2 pt-2 border-t border-white/10 text-xs opacity-70">
                            Sources: model-comparison.pdf · aiveilix.com
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
              <div className="pt-3 border-t border-white/10">
                <div className="flex items-center gap-2 text-xs opacity-60">
                  <div className="w-2 h-2 rounded-full bg-[#2DFFB7]" />
                  Asking about selected files
                </div>
              </div>
            </div>
          </div>

          <div className="flex-shrink-0">
            <FilesCard
              bucketId="preview-bucket"
              files={files}
              onFilesUpdate={() => {}}
              selectedFiles={selectedFiles}
              onFileSelect={(file) => {
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

        <motion.div
          animate={pulse ? { opacity: [0, 0.6, 0], scale: [0.98, 1.02, 1.04] } : { opacity: 0 }}
          transition={{ duration: 1, ease: 'easeInOut' }}
          className="pointer-events-none absolute left-5 top-5 w-[260px] h-[90px] rounded-2xl border border-[#2DFFB7]/50 shadow-[0_0_30px_rgba(45,255,183,0.25)]"
        />
      </div>
    </div>
  )
}
