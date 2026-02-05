import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import FilesCard from '../components/FilesCard'

export default function FileSelectionGif() {
  const { isDark } = useTheme()
  const [selectedFiles, setSelectedFiles] = useState([])
  const [step, setStep] = useState(0)

  const files = [
    { id: 'f1', name: 'architecture.pdf', size_bytes: 2457600, folder_path: 'docs' },
    { id: 'f2', name: 'api-spec.md', size_bytes: 98304, folder_path: 'docs' },
    { id: 'f3', name: 'release-notes.txt', size_bytes: 2048, folder_path: '' }
  ]

  useEffect(() => {
    const animate = async () => {
      setSelectedFiles([])
      setStep(0)
      await new Promise(r => setTimeout(r, 600))

      setSelectedFiles([files[0]])
      setStep(1)
      await new Promise(r => setTimeout(r, 800))

      setSelectedFiles([files[0], files[1]])
      setStep(2)
      await new Promise(r => setTimeout(r, 1200))

      setSelectedFiles([files[1]])
      setStep(3)
      await new Promise(r => setTimeout(r, 800))

      setSelectedFiles([])
      setStep(0)
    }
    animate()
    const interval = setInterval(animate, 6000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`relative w-full rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'}`}>
      <div className="grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6 p-6">
        <div className="relative">
          <FilesCard
            bucketId="preview-bucket"
            files={files}
            onFilesUpdate={() => {}}
            selectedFiles={selectedFiles}
            onFileSelect={() => {}}
          />
          <motion.div
            animate={step >= 1 ? { opacity: [0, 0.6, 0], scale: [0.98, 1.02, 1.04] } : { opacity: 0 }}
            transition={{ duration: 1, ease: 'easeInOut' }}
            className="pointer-events-none absolute right-4 top-4 w-[140px] h-[34px] rounded-xl border border-[#2DFFB7]/50 shadow-[0_0_20px_rgba(45,255,183,0.25)]"
          />
        </div>

        <div className={`rounded-2xl border p-4 ${isDark ? 'border-white/10 bg-white/5' : 'border-black/10 bg-white/60'}`}>
          <div className="text-sm font-semibold mb-3">Selected for chat</div>
          <div className="flex flex-wrap gap-2">
            <AnimatePresence>
              {selectedFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  className={`px-3 py-1.5 rounded-full text-xs border ${
                    isDark ? 'border-dark-accent/40 bg-dark-accent/20 text-dark-accent' : 'border-[#1FE0A5]/40 bg-[#1FE0A5]/20 text-[#0B3C49]'
                  }`}
                >
                  @{file.name}
                </motion.div>
              ))}
            </AnimatePresence>
            {selectedFiles.length === 0 && (
              <div className="text-xs opacity-50">Click files to add context</div>
            )}
          </div>

          <div className="mt-6 text-xs opacity-60">
            The AI will focus only on selected files for faster, more precise answers.
          </div>
        </div>
      </div>
    </div>
  )
}
