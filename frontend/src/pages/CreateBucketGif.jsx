import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useTheme } from '../context/ThemeContext'
import Button from '../components/Button'
import Input from '../components/Input'

export default function CreateBucketGif() {
  const { isDark } = useTheme()
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({ name: '', description: '' })
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)

  const fullName = 'Research Library'
  const fullDescription = 'Papers, notes, and key findings for Q1.'

  useEffect(() => {
    const animate = async () => {
      await new Promise(r => setTimeout(r, 800))

      setStep(1)
      for (let i = 0; i <= fullName.length; i++) {
        setFormData(prev => ({ ...prev, name: fullName.slice(0, i) }))
        await new Promise(r => setTimeout(r, 90))
      }

      await new Promise(r => setTimeout(r, 350))

      setStep(2)
      for (let i = 0; i <= fullDescription.length; i++) {
        setFormData(prev => ({ ...prev, description: fullDescription.slice(0, i) }))
        await new Promise(r => setTimeout(r, 60))
      }

      await new Promise(r => setTimeout(r, 400))

      setStep(3)
      setFiles([
        { name: 'research-summary.pdf', size: 2.5 * 1024 * 1024 },
        { name: 'project/docs/readme.md', size: 1.2 * 1024, webkitRelativePath: 'project/docs/readme.md' }
      ])

      await new Promise(r => setTimeout(r, 600))

      setStep(4)
      setLoading(true)
      await new Promise(r => setTimeout(r, 1500))
      setLoading(false)

      await new Promise(r => setTimeout(r, 1200))

      setFormData({ name: '', description: '' })
      setFiles([])
      setStep(0)
    }

    animate()
    const interval = setInterval(animate, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`relative p-4 ${isDark ? 'bg-black/40' : 'bg-white/70'}`}>
      <div className={`w-full rounded-3xl backdrop-blur-xl border p-8 ${isDark
        ? 'border-white/10 bg-white/5'
        : 'border-[#1FE0A5]/20 bg-[#F6FFFC]'
        }`}
      >
        <div className="mb-6">
          <h2 className={`text-2xl font-bold ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
            Create New Bucket
          </h2>
        </div>

        <form onSubmit={(e) => e.preventDefault()}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Side - Name & Description */}
            <div className="space-y-4">
              <h3 className={`text-lg font-semibold mb-4 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                Bucket Details
              </h3>

              <motion.div
                animate={step >= 1 ? { scale: [1, 1.02, 1] } : {}}
                transition={{ duration: 0.3 }}
              >
                <Input
                  label="Bucket Name"
                  placeholder="My Knowledge Bucket"
                  value={formData.name}
                  onChange={() => {}}
                  required
                />
              </motion.div>

              <motion.div
                animate={step >= 2 ? { scale: [1, 1.02, 1] } : {}}
                transition={{ duration: 0.3 }}
                className="mb-4"
              >
                <label className={`block text-sm font-medium mb-2 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                  Description (optional)
                </label>
                <textarea
                  placeholder="What's in this bucket?"
                  value={formData.description}
                  onChange={() => {}}
                  rows={4}
                  className={`w-full px-4 py-3 rounded-xl border resize-none focus:outline-none focus:ring-2 transition-all duration-200 ${isDark
                    ? 'bg-black/20 border-white/10 text-dark-text placeholder:text-dark-text/40 focus:ring-dark-accent/50'
                    : 'bg-white/50 border-[#1FE0A5]/20 text-light-text placeholder:text-light-text/40 focus:ring-light-accent/50'
                    }`}
                />
              </motion.div>

              <div className="pt-4">
                <motion.div
                  animate={step >= 4 ? { scale: [1, 0.98, 1] } : {}}
                  transition={{ duration: 0.2 }}
                >
                  <Button type="submit" loading={loading} className="w-full">
                    Create Bucket
                  </Button>
                </motion.div>
              </div>
            </div>

            {/* Right Side - Upload Section */}
            <div className="space-y-4">
              <h3 className={`text-lg font-semibold mb-4 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                Upload Files (Optional)
              </h3>

              <motion.div
                animate={step >= 3 ? { borderColor: isDark ? '#2DFFB7' : '#1FE0A5' } : {}}
                transition={{ duration: 0.4 }}
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors min-h-[300px] flex flex-col justify-center ${isDark
                  ? 'border-white/10'
                  : 'border-[#1FE0A5]/30'
                  }`}
              >
                <div className="flex flex-col items-center gap-4">
                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 mb-4 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className={`font-medium mb-2 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                      Click to upload files
                    </p>
                    <p className={`text-sm ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                      Any file type
                    </p>
                  </div>

                  <div className="flex items-center gap-2 my-2 w-full">
                    <div className={`flex-1 h-px ${isDark ? 'bg-white/10' : 'bg-[#1FE0A5]/20'}`}></div>
                    <span className={`text-xs ${isDark ? 'text-dark-text/40' : 'text-[#062A33]/40'}`}>OR</span>
                    <div className={`flex-1 h-px ${isDark ? 'bg-white/10' : 'bg-[#1FE0A5]/20'}`}></div>
                  </div>

                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 mb-4 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    <p className={`font-medium mb-2 ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                      Click to upload folder
                    </p>
                    <p className={`text-sm ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                      Upload entire folder with all files
                    </p>
                  </div>

                  <p className={`text-xs mt-4 ${isDark ? 'text-dark-text/40' : 'text-[#062A33]/40'}`}>
                    You can upload files later
                  </p>
                </div>
              </motion.div>

              {files.length > 0 && (
                <div className="mt-4 space-y-2 max-h-64 overflow-y-auto">
                  <p className={`text-sm font-medium mb-2 ${isDark ? 'text-dark-text/70' : 'text-[#062A33]/70'}`}>
                    Selected Files ({files.length})
                  </p>
                  {files.map((file, index) => {
                    const relativePath = file.webkitRelativePath || file.name
                    const pathParts = relativePath.split('/')
                    const fileName = pathParts[pathParts.length - 1]
                    const folderPath = pathParts.length > 1 ? pathParts.slice(0, -1).join('/') : null

                    return (
                      <div
                        key={index}
                        className={`flex items-center justify-between p-3 rounded-lg border ${isDark
                          ? 'bg-white/5 border-white/10'
                          : 'bg-white/50 border-[#1FE0A5]/20'
                          }`}
                      >
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                          {folderPath ? (
                            <svg className="w-5 h-5 flex-shrink-0 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5 flex-shrink-0 dark:text-dark-accent text-light-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          )}
                          <div className="flex-1 min-w-0">
                            <span className={`text-sm block truncate ${isDark ? 'text-dark-text' : 'text-[#062A33]'}`}>
                              {fileName}
                            </span>
                            {folderPath && (
                              <span className={`text-xs block truncate ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                                {folderPath}
                              </span>
                            )}
                          </div>
                          <span className={`text-xs flex-shrink-0 ml-2 ${isDark ? 'text-dark-text/50' : 'text-[#062A33]/50'}`}>
                            {(file.size / 1024).toFixed(1)} KB
                          </span>
                        </div>
                        <button
                          type="button"
                          className="p-1 rounded hover:bg-red-500/10 text-red-400 transition-colors ml-2"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </form>
      </div>

    </div>
  )
}
