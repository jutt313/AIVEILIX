import React, { useEffect, useState } from 'react';
import BucketAccessModal from './BucketAccessModal';
import { useTeamContext } from './useTeamContext';
import { teamApi } from '../../api/team';
import { useAppTheme } from './theme';

const MAX_FACES = 3;

// Per-bucket member bubble for the dashboard "Actions" column. Mirrors the
// header TeamFacepile: shows the members who have access to this bucket and an
// inline "+" to add new ones. Owner-only. Opens the bucket access modal.
export default function BucketMembers({ bucketId, bucketName }) {
  const { isOwner } = useTeamContext();
  const { theme } = useAppTheme();
  const isDark = theme === 'dark';

  const [members, setMembers] = useState([]);
  const [open, setOpen] = useState(false);

  const load = async () => {
    if (!bucketId) return;
    try {
      const data = await teamApi.listBucketAccess(bucketId);
      setMembers(data.members || []);
    } catch (_) {
      setMembers([]);
    }
  };

  useEffect(() => {
    if (isOwner) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOwner, bucketId]);

  if (!isOwner) return null;

  // Ring color blends each face into the table row background.
  const ring = isDark ? 'ring-[#0b1220]' : 'ring-[#f8fafc]';
  const shown = members.slice(0, MAX_FACES);
  const overflow = members.length - shown.length;
  const hasMembers = members.length > 0;
  const names = members.map((m) => m.display_name || m.invite_email || 'Member').join(', ');

  return (
    <>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault();
          setOpen(true);
        }}
        title={hasMembers ? `Shared with ${names}` : 'Share with team'}
        aria-label={hasMembers ? 'Bucket members — view and add' : 'Add team members to bucket'}
        className="group inline-flex shrink-0 items-center transition hover:opacity-95"
      >
        <div className="flex items-center -space-x-2">
          {shown.map((m) => (
            <div
              key={m.team_member_id}
              className={`flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-semibold text-white ring-2 ${ring} transition group-hover:translate-y-[-1px]`}
              style={{ backgroundColor: m.display_color || '#64748b' }}
            >
              {(m.display_name || m.invite_email || '?').charAt(0).toUpperCase()}
            </div>
          ))}
          {overflow > 0 && (
            <div
              className={`flex h-7 w-7 items-center justify-center rounded-full text-[10px] font-semibold ring-2 ${ring} ${
                isDark ? 'bg-white/[0.08] text-white/80' : 'bg-slate-200 text-slate-600'
              }`}
            >
              +{overflow}
            </div>
          )}
          {/* Add-member affordance — same bubble as current members */}
          <div
            className={`relative z-10 flex h-7 w-7 items-center justify-center rounded-full ring-2 ${ring} transition group-hover:translate-y-[-1px] ${
              isDark
                ? 'bg-white/[0.08] text-white/75 group-hover:bg-white/[0.16] group-hover:text-white'
                : 'bg-slate-200 text-slate-600 group-hover:bg-slate-300 group-hover:text-slate-900'
            }`}
          >
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </div>
        </div>
      </button>
      <BucketAccessModal
        open={open}
        bucketId={bucketId}
        bucketName={bucketName}
        onClose={() => { setOpen(false); load(); }}
      />
    </>
  );
}
