import React, { useState } from 'react';
import BucketAccessModal from './BucketAccessModal';
import { useTeamContext } from './useTeamContext';
import { useAppTheme } from './theme';

export default function BucketShareButton({ bucketId, bucketName, className = '' }) {
  const { isOwner } = useTeamContext();
  const { theme } = useAppTheme();
  const [open, setOpen] = useState(false);

  if (!isOwner) return null;

  const baseCls = theme === 'dark'
    ? 'text-slate-400 hover:text-blue-400 hover:bg-white/[0.04]'
    : 'text-slate-500 hover:text-blue-600 hover:bg-slate-100';

  return (
    <>
      <button
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
          setOpen(true);
        }}
        type="button"
        title="Share with team"
        aria-label="Share with team"
        className={`inline-flex items-center justify-center rounded-full p-1.5 transition ${baseCls} ${className}`}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="18" cy="5" r="3" />
          <circle cx="6" cy="12" r="3" />
          <circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
          <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
      </button>
      <BucketAccessModal
        open={open}
        bucketId={bucketId}
        bucketName={bucketName}
        onClose={() => setOpen(false)}
      />
    </>
  );
}
