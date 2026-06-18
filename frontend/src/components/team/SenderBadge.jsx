import React from 'react';
import { pickContrastingText } from './colorPalette';

function isTeamMemberSender(sender) {
  return (
    sender &&
    (sender.kind === 'team_member' || sender.kind === 'team_member_hidden')
  );
}

/**
 * Small "Name" pill rendered above a team member's chat bubble so the viewer
 * knows who sent it. Renders nothing for the assistant or for the viewer's
 * own (owner) messages — those keep their default look.
 */
export default function SenderBadge({ sender, align = 'right' }) {
  if (!isTeamMemberSender(sender)) return null;
  const name = sender.display_name || 'Team member';
  const bg = sender.display_color || '#64748b';
  const fg = pickContrastingText(bg);
  return (
    <div className={`mb-1 flex ${align === 'right' ? 'justify-end' : 'justify-start'}`}>
      <span
        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-semibold tracking-wide"
        style={{ backgroundColor: bg, color: fg }}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{ backgroundColor: fg, opacity: 0.85 }}
        />
        {name}
      </span>
    </div>
  );
}

/**
 * Inline style for the bubble background when the message was sent by a team
 * member. Returns null for owner / assistant / unknown — so the caller keeps
 * its default styling (e.g. existing blue-600 bubble).
 */
export function bubbleStyleForSender(sender) {
  if (!isTeamMemberSender(sender)) return null;
  const bg = sender.display_color || '#64748b';
  return {
    backgroundColor: bg,
    color: pickContrastingText(bg),
  };
}
