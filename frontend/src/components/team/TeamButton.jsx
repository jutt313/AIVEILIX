import React, { useState } from 'react';
import TeamManageModal from './TeamManageModal';
import { useTeamContext } from './useTeamContext';

// Matches the existing dashboard `iconBtn` shape: rounded full button, slate
// hover. `className` from the parent already carries those tokens — we just
// add the SVG and label.
export default function TeamButton({ className = '' }) {
  const { isOwner } = useTeamContext();
  const [open, setOpen] = useState(false);

  if (!isOwner) return null;

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        type="button"
        title="Team members"
        aria-label="Team members"
        className={className}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
          <path d="M16 3.13a4 4 0 0 1 0 7.75" />
        </svg>
      </button>
      <TeamManageModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
