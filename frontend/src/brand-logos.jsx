/* Inline brand SVG logos — clean, recognizable, brand-colored.
   Approximations of official marks; safe to ship without licensing concerns.
*/
import React from 'react';

export function ClaudeLogo({ className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <rect width="24" height="24" rx="6" fill="#D97757" />
      <path d="M9.4 7.5L6.2 16.5h2.1l.6-1.9h3.4l.6 1.9h2.1L11.8 7.5H9.4Zm.05 5.3l1.05-3.4 1.05 3.4H9.45Zm6.3-5.3l-3.2 9h2.1l.6-1.9h3.4l.6 1.9h2.1L18.1 7.5h-2.35Zm.05 5.3l1.05-3.4 1.05 3.4h-2.1Z" fill="#FFFFFF" />
    </svg>
  );
}

export function ChatGPTLogo({ className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <rect width="24" height="24" rx="6" fill="#10A37F" />
      <path
        d="M17.9 10.6a3.7 3.7 0 0 0-.32-3.07 3.78 3.78 0 0 0-4.07-1.82 3.74 3.74 0 0 0-2.83-1.26 3.78 3.78 0 0 0-3.6 2.6 3.74 3.74 0 0 0-2.5 1.81 3.78 3.78 0 0 0 .47 4.43 3.7 3.7 0 0 0 .32 3.08 3.78 3.78 0 0 0 4.07 1.81 3.74 3.74 0 0 0 2.83 1.27 3.78 3.78 0 0 0 3.6-2.61 3.74 3.74 0 0 0 2.5-1.81 3.78 3.78 0 0 0-.47-4.43Zm-5.62 7.86a2.8 2.8 0 0 1-1.8-.65l.09-.05 2.99-1.73a.49.49 0 0 0 .25-.43v-4.22l1.27.73a.05.05 0 0 1 .02.04v3.49a2.81 2.81 0 0 1-2.82 2.82Zm-6.06-2.59a2.8 2.8 0 0 1-.33-1.88v-.06l3 1.73a.49.49 0 0 0 .49 0l3.66-2.11v1.46a.05.05 0 0 1-.02.04l-3.03 1.75a2.82 2.82 0 0 1-3.77-.93Zm-.79-6.55a2.8 2.8 0 0 1 1.47-1.24v3.55a.49.49 0 0 0 .24.42l3.65 2.11-1.26.73a.05.05 0 0 1-.04 0L6.46 13.16a2.82 2.82 0 0 1-1.03-3.85Zm10.4 2.42L12.17 9.6 13.43 8.88a.05.05 0 0 1 .04 0l3.03 1.75a2.82 2.82 0 0 1-.43 5.08v-3.55a.48.48 0 0 0-.25-.42Zm1.26-1.9-.09-.05L14.04 8a.49.49 0 0 0-.49 0l-3.66 2.11V8.65a.05.05 0 0 1 .02-.04l3.03-1.75a2.82 2.82 0 0 1 4.18 2.92Zm-7.92 2.6-1.27-.73a.05.05 0 0 1-.02-.04V8.18a2.82 2.82 0 0 1 4.62-2.17l-.08.05L9.45 7.79a.49.49 0 0 0-.25.43Zm.68-1.48 1.63-.94 1.63.94v1.88l-1.63.94-1.63-.94Z"
        fill="#FFFFFF"
      />
    </svg>
  );
}

export function ClaudeDesktopLogo({ className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <rect width="24" height="24" rx="6" fill="#D97757" />
      {/* monitor frame */}
      <rect x="4" y="6" width="16" height="10" rx="1.2" fill="none" stroke="#FFFFFF" strokeWidth="1.5" />
      <path d="M9 19h6M12 16v3" stroke="#FFFFFF" strokeWidth="1.5" strokeLinecap="round" />
      {/* Claude A mark inside */}
      <path d="M10.7 9L9.4 13h.95l.27-.85h1.5l.28.85h.95L12.05 9h-1.35Zm.05 2.4l.45-1.5.45 1.5h-.9Z" fill="#FFFFFF" />
    </svg>
  );
}

export function GenericMcpLogo({ className = 'h-6 w-6' }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <rect width="24" height="24" rx="6" fill="url(#mcp-grad)" />
      <circle cx="6" cy="12" r="1.8" fill="#FFFFFF" />
      <circle cx="18" cy="12" r="1.8" fill="#FFFFFF" />
      <circle cx="12" cy="6" r="1.8" fill="#FFFFFF" />
      <circle cx="12" cy="18" r="1.8" fill="#FFFFFF" />
      <path d="M6 12L12 6M12 6L18 12M18 12L12 18M12 18L6 12" stroke="#FFFFFF" strokeWidth="1.2" strokeOpacity="0.5" />
      <defs>
        <linearGradient id="mcp-grad" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
          <stop stopColor="#3B82F6" />
          <stop offset="1" stopColor="#A855F7" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export function CursorLogo({ className = 'h-6 w-6' }) {
  /* kept for the trust strip if needed; not surfaced here */
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <rect width="24" height="24" rx="6" fill="#000000" />
      <path d="M7 5l10 7-10 7V5z" fill="#FFFFFF" />
    </svg>
  );
}

export const TOOLS = [
  { id: 'claude',         label: 'Claude',           Logo: ClaudeLogo,        brand: '#D97757' },
  { id: 'chatgpt',        label: 'ChatGPT',          Logo: ChatGPTLogo,       brand: '#10A37F' },
  { id: 'claude-desktop', label: 'Claude Desktop',   Logo: ClaudeDesktopLogo, brand: '#D97757' },
  { id: 'mcp',            label: 'Any MCP AI',       Logo: GenericMcpLogo,    brand: '#6366F1' },
];
