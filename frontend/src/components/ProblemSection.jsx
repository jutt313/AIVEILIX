import { useEffect, useMemo, useRef, useState } from 'react'

const ProblemSection = () => {
  const sectionRef = useRef(null)
  const [activeIndex, setActiveIndex] = useState(0)
  const [isFinal, setIsFinal] = useState(false)
  const [hoverIndex, setHoverIndex] = useState(null)

  const pairs = useMemo(() => ([
    {
      problem: {
        title: 'Endless Re-Uploading Cycle',
        metric: '15+ minutes per file',
        body: 'Every new tool means a fresh upload. Claude, Cursor, ChatGPT—same files, repeated work.'
      },
      solution: {
        title: 'Upload Once, Access Everywhere',
        metric: '1 upload = infinite access',
        body: 'AIveilix ingests files once and exposes them to every MCP-compatible AI tool instantly.'
      }
    },
    {
      problem: {
        title: 'Scattered Knowledge Fragments',
        metric: '5–10 tools daily',
        body: 'Docs, notes, and code live in different places. Finding the right file becomes a scavenger hunt.'
      },
      solution: {
        title: 'Centralized Knowledge Base',
        metric: '1 source of truth',
        body: 'Buckets keep everything organized and searchable across your entire library.'
      }
    },
    {
      problem: {
        title: 'Token Budget Hemorrhage',
        metric: '3x unnecessary costs',
        body: 'Each platform re-processes the same PDFs, charging you multiple times.'
      },
      solution: {
        title: 'Process Once, Reuse Forever',
        metric: '70% cost reduction',
        body: 'AIveilix indexes once, then every tool reuses the same processed context.'
      }
    },
    {
      problem: {
        title: 'Zero Context Persistence',
        metric: '100% context loss',
        body: 'Switch tools and your hard-earned context disappears. Conversations reset.'
      },
      solution: {
        title: 'Persistent Knowledge Context',
        metric: 'Context travels with you',
        body: 'The same citations and memory are available across every connected tool.'
      }
    },
    {
      problem: {
        title: 'Security Fragmentation',
        metric: 'Multiple exposure points',
        body: 'Each upload creates another copy of sensitive data across third parties.'
      },
      solution: {
        title: 'Single Secure Vault',
        metric: 'One encrypted hub',
        body: 'Centralize access and reduce surface area with a single secure endpoint.'
      }
    },
    {
      problem: {
        title: 'Slow Retrieval Loops',
        metric: 'Minutes per answer',
        body: 'Manually search, re-upload, re-explain, then wait for the AI to catch up.'
      },
      solution: {
        title: 'Instant Context Retrieval',
        metric: '<200ms search',
        body: 'Semantic retrieval delivers the most relevant chunks in milliseconds.'
      }
    }
  ]), [])

  useEffect(() => {
    const onScroll = () => {
      if (!sectionRef.current) return
      const rect = sectionRef.current.getBoundingClientRect()
      const viewportHeight = window.innerHeight
      const totalScroll = rect.height - viewportHeight
      const progress = Math.min(Math.max((viewportHeight - rect.top) / totalScroll, 0), 1)
      const index = Math.min(pairs.length - 1, Math.floor(progress * pairs.length))
      setActiveIndex(index)
      setIsFinal(progress >= 0.92)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [pairs.length])

  const renderCard = (type, item, idx) => {
    const isActive = idx === activeIndex
    const isHovered = hoverIndex === idx
    const baseOffset = isFinal ? idx * 10 : 0
    const fanOffset = isFinal ? (hoverIndex === null ? idx * 8 : idx * 14) : 0
    const translateY = isFinal ? baseOffset + fanOffset : 0
    const scale = isFinal ? (isHovered ? 1.03 : 0.98) : (isActive ? 1 : 0.94)
    const opacity = isFinal ? 1 : (isActive ? 1 : 0)
    const zIndex = isFinal ? (isHovered ? 30 : 10 + idx) : (isActive ? 20 : 0)

    const palette = type === 'problem'
      ? 'from-red-500/20 to-orange-500/10 border-red-500/30 text-red-200'
      : 'from-[#2DFFB7]/20 to-emerald-500/10 border-[#2DFFB7]/30 text-[#2DFFB7]'

    return (
      <div
        key={`${type}-${idx}`}
        onMouseEnter={() => isFinal && setHoverIndex(idx)}
        onMouseLeave={() => isFinal && setHoverIndex(null)}
        style={{ transform: `translateY(${translateY}px) scale(${scale})`, opacity, zIndex }}
        className={`absolute inset-0 transition-all duration-500 ${isFinal ? 'cursor-pointer' : ''}`}
      >
        <div className={`relative h-[340px] lg:h-[360px] rounded-2xl border backdrop-blur-xl bg-gradient-to-br ${palette}`}>
          <div className="absolute inset-0 rounded-2xl bg-[linear-gradient(140deg,rgba(255,255,255,0.08),transparent)] pointer-events-none" />
          <div className="p-6 h-full flex flex-col justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] opacity-70">
                {type === 'problem' ? `Problem 0${idx + 1}` : `Solution 0${idx + 1}`}
              </div>
              <h3 className="text-2xl font-semibold text-white mt-3">{item.title}</h3>
              <div className="inline-flex items-center px-3 py-1 mt-4 rounded-lg bg-black/30 text-xs text-white/80">
                {item.metric}
              </div>
              <p className="text-gray-200/80 text-sm leading-relaxed mt-4">{item.body}</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-white/60">
              <span className="h-1.5 w-1.5 rounded-full bg-white/60" />
              {type === 'problem' ? 'Current state' : 'AIveilix impact'}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <section
      ref={sectionRef}
      className="relative bg-[#050B0D] py-24"
      style={{ minHeight: '100vh' }}
    >
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1a1a1a_1px,transparent_1px),linear-gradient(to_bottom,#1a1a1a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_70%,transparent_100%)]" />
      <div className="relative max-w-7xl mx-auto px-6 lg:px-10">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 text-xs tracking-[0.3em] text-gray-300">
            PROBLEM VS SOLUTION
          </div>
          <h2 className="text-4xl lg:text-6xl font-bold text-white mt-5">
            From Chaos to <span className="text-[#2DFFB7]">Clarity</span>
          </h2>
          <p className="text-gray-400 text-lg lg:text-xl max-w-3xl mx-auto mt-4">
            Scroll to reveal each matched problem and solution. At the end, hover to revisit any card.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-10 sticky top-24">
          <div className="relative h-[320px] lg:h-[340px]">
            {pairs.map((pair, idx) => renderCard('problem', pair.problem, idx))}
          </div>
          <div className="relative h-[320px] lg:h-[340px]">
            {pairs.map((pair, idx) => renderCard('solution', pair.solution, idx))}
          </div>
        </div>
      </div>

      <div className="h-[0vh]" />
    </section>
  )
}

export default ProblemSection
