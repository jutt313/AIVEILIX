import React, { useEffect, useRef, useState } from 'react';
import { TEAM_COLOR_PALETTE } from './colorPalette';
import { useAppTheme } from './theme';

function isPresetColor(value) {
  if (!value) return false;
  return TEAM_COLOR_PALETTE.some((c) => c.toLowerCase() === value.toLowerCase());
}

export default function ColorPicker({ value, onChange, palette = TEAM_COLOR_PALETTE }) {
  const { theme } = useAppTheme();
  const isDark = theme === 'dark';
  const ringOffset = isDark ? 'ring-offset-[#0b1220]' : 'ring-offset-white';
  const fileInputRef = useRef(null);

  const [customOpen, setCustomOpen] = useState(false);
  const [draftHex, setDraftHex] = useState(value || '#3B82F6');

  useEffect(() => {
    setDraftHex(value || '#3B82F6');
  }, [value]);

  const customActive = value && !isPresetColor(value);

  function commitCustomHex(next) {
    const trimmed = (next || '').trim();
    if (/^#?[0-9a-fA-F]{3}$|^#?[0-9a-fA-F]{6}$/.test(trimmed)) {
      const normalized = trimmed.startsWith('#') ? trimmed : `#${trimmed}`;
      onChange(normalized.toUpperCase());
    }
  }

  function applyCustomFromNativePicker(hex) {
    setDraftHex(hex);
    onChange(hex.toUpperCase());
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {palette.map((color) => {
          const selected = (value || '').toLowerCase() === color.toLowerCase();
          return (
            <button
              key={color}
              type="button"
              onClick={() => onChange(color)}
              aria-label={`Pick color ${color}`}
              className={`relative h-9 w-9 rounded-full transition-transform hover:scale-110 ${
                selected ? `ring-2 ring-offset-2 ${ringOffset} ring-blue-500` : ''
              }`}
              style={{ backgroundColor: color }}
            >
              {selected && (
                <svg
                  className="absolute inset-0 m-auto"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="white"
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              )}
            </button>
          );
        })}

        {/* Custom color tile */}
        <button
          type="button"
          onClick={() => {
            setCustomOpen((v) => !v);
            // Trigger native picker for fast path
            setTimeout(() => fileInputRef.current?.click(), 0);
          }}
          aria-label="Pick a custom color"
          className={`relative h-9 w-9 rounded-full transition-transform hover:scale-110 overflow-hidden ${
            customActive ? `ring-2 ring-offset-2 ${ringOffset} ring-blue-500` : ''
          }`}
          style={{
            background: customActive
              ? value
              : 'conic-gradient(from 180deg, #ef4444, #f59e0b, #eab308, #10b981, #06b6d4, #3b82f6, #8b5cf6, #ec4899, #ef4444)',
          }}
        >
          {customActive ? (
            <svg
              className="absolute inset-0 m-auto"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          ) : (
            <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white drop-shadow">
              +
            </span>
          )}
        </button>

        <input
          ref={fileInputRef}
          type="color"
          value={value && /^#[0-9a-fA-F]{6}$/.test(value) ? value : '#3B82F6'}
          onChange={(e) => applyCustomFromNativePicker(e.target.value)}
          className="sr-only"
        />
      </div>

      {customOpen && (
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-6 w-6 rounded-full"
            style={{ backgroundColor: draftHex }}
          />
          <input
            type="text"
            value={draftHex}
            onChange={(e) => setDraftHex(e.target.value)}
            onBlur={(e) => commitCustomHex(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                commitCustomHex(draftHex);
              }
            }}
            placeholder="#3B82F6"
            className={`w-28 rounded-lg px-2.5 py-1 text-xs font-mono outline-none transition focus:ring-2 ${
              isDark
                ? 'bg-white/[0.04] text-white placeholder:text-slate-500 focus:ring-blue-400/30'
                : 'bg-slate-100 text-slate-900 placeholder:text-slate-400 focus:ring-blue-500/20'
            }`}
          />
          <button
            type="button"
            onClick={() => commitCustomHex(draftHex)}
            className={`rounded-lg px-3 py-1 text-xs font-medium ${
              isDark
                ? 'bg-blue-500 text-white hover:bg-blue-400'
                : 'bg-blue-600 text-white hover:bg-blue-500'
            }`}
          >
            Apply
          </button>
        </div>
      )}
    </div>
  );
}
