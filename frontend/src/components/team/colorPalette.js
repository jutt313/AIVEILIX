// Twelve-color palette used for team member chat bubbles.
export const TEAM_COLOR_PALETTE = [
  '#3B82F6', // blue
  '#10B981', // emerald
  '#8B5CF6', // violet
  '#EC4899', // pink
  '#F59E0B', // amber
  '#14B8A6', // teal
  '#EF4444', // red
  '#6366F1', // indigo
  '#EAB308', // yellow
  '#06B6D4', // cyan
  '#F43F5E', // rose
  '#84CC16', // lime
];

// White if dark color, dark if light color — picked by luminance.
export function pickContrastingText(hex) {
  if (!hex || typeof hex !== 'string') return '#ffffff';
  const h = hex.replace('#', '');
  const expanded = h.length === 3
    ? h.split('').map((c) => c + c).join('')
    : h;
  const r = parseInt(expanded.slice(0, 2), 16);
  const g = parseInt(expanded.slice(2, 4), 16);
  const b = parseInt(expanded.slice(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.6 ? '#111827' : '#ffffff';
}
