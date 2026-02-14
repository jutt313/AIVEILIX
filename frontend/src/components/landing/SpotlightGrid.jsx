import { createContext, useContext, useRef, useState, useCallback } from 'react';

const SpotlightContext = createContext({ x: 0, y: 0, isActive: false });

export const SpotlightGrid = ({ children, className = '' }) => {
  const containerRef = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0, isActive: false });

  const handleMouseMove = useCallback((e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setPosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      isActive: true,
    });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setPosition((prev) => ({ ...prev, isActive: false }));
  }, []);

  return (
    <SpotlightContext.Provider value={position}>
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className={className}
        style={{ position: 'relative' }}
      >
        {children}
      </div>
    </SpotlightContext.Provider>
  );
};

export const SpotlightCard = ({ children, className = '' }) => {
  const cardRef = useRef(null);
  const { x, y, isActive } = useContext(SpotlightContext);
  const [localPos, setLocalPos] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleLocalMove = useCallback((e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setLocalPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  }, []);

  // Calculate border glow position relative to this card
  const getBorderGlow = () => {
    if (!isActive || !cardRef.current) return {};
    const rect = cardRef.current.getBoundingClientRect();
    const parent = cardRef.current.parentElement?.parentElement;
    if (!parent) return {};
    const parentRect = parent.getBoundingClientRect();
    const relX = x - (rect.left - parentRect.left);
    const relY = y - (rect.top - parentRect.top);
    return {
      background: `radial-gradient(250px circle at ${relX}px ${relY}px, rgba(45,255,183,0.12), transparent 70%)`,
    };
  };

  return (
    <div
      ref={cardRef}
      className={`spotlight-card ${className}`}
      onMouseMove={handleLocalMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ position: 'relative', overflow: 'hidden' }}
    >
      {/* Border proximity glow */}
      <div
        className="spotlight-border-glow"
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 'inherit',
          pointerEvents: 'none',
          zIndex: 0,
          opacity: isActive ? 1 : 0,
          transition: 'opacity 0.3s ease',
          ...getBorderGlow(),
        }}
      />
      {/* Inner hover glow */}
      <div
        className="spotlight-inner-glow"
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: 'inherit',
          pointerEvents: 'none',
          zIndex: 0,
          opacity: isHovered ? 1 : 0,
          transition: 'opacity 0.3s ease',
          background: `radial-gradient(300px circle at ${localPos.x}px ${localPos.y}px, rgba(45,255,183,0.08), transparent 60%)`,
        }}
      />
      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {children}
      </div>
    </div>
  );
};
