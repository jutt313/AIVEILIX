import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import FilesCard from '../components/FilesCard'

export default function FilesCardGif() {
  const { isDark } = useTheme()
  const [selectedFiles, setSelectedFiles] = useState([])
  const [pulse, setPulse] = useState(false)
  const [files, setFiles] = useState([
    { id: 'f1', name: 'project/docs/readme.md', size_bytes: 4096, folder_path: 'project/docs' },
    { id: 'f2', name: 'project/src/main.py', size_bytes: 23890, folder_path: 'project/src' },
    { id: 'f3', name: 'project/src/utils.py', size_bytes: 15360, folder_path: 'project/src' },
    { id: 'f4', name: 'notes.txt', size_bytes: 2048, folder_path: '' }
  ])

  useEffect(() => {
    const animate = async () => {
      setPulse(true)
      await new Promise(r => setTimeout(r, 900))
      setPulse(false)
      await new Promise(r => setTimeout(r, 600))
    }
    animate()
    const interval = setInterval(animate, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`relative w-[420px] max-w-full rounded-3xl overflow-hidden border ${isDark ? 'border-white/10 bg-black/40' : 'border-black/10 bg-white/70'}`}>
      <div className="relative">
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
        <motion.div
          animate={pulse ? { opacity: [0, 0.6, 0], scale: [0.98, 1.02, 1.04] } : { opacity: 0 }}
          transition={{ duration: 1, ease: 'easeInOut' }}
          className="pointer-events-none absolute right-4 top-4 w-[140px] h-[34px] rounded-xl border border-[#2DFFB7]/50 shadow-[0_0_20px_rgba(45,255,183,0.25)]"
        />
      </div>
    </div>
  )
}
