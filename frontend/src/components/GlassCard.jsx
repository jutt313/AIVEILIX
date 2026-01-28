export default function GlassCard({ children, className = '' }) {
  return (
    <div className="relative group w-full">
      {/* Glow effect around card on hover */}
      <div 
        className="absolute -inset-2 rounded-4xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 blur-xl pointer-events-none"
        style={{
          background: 'radial-gradient(circle, rgba(45, 255, 183, 0.3) 0%, transparent 70%)',
          boxShadow: '0 0 40px rgba(45, 255, 183, 0.2)'
        }}
      />

      {/* Main card */}
      <div
        className={`
          relative w-full max-w-md mx-auto p-8 rounded-4xl
          backdrop-blur-xl
          border border-white/10
          dark:bg-white/5
          bg-black/5
          transition-all duration-300
          group-hover:border-dark-accent/50
          group-hover:shadow-[0_0_20px_rgba(45,255,183,0.3),0_0_40px_rgba(45,255,183,0.15)]
          ${className}
        `}
        style={{
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)'
        }}
      >
        <div className="relative z-10">
          {children}
        </div>
      </div>
    </div>
  )
}
