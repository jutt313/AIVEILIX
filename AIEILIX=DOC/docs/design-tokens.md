# Aiveilix — Design Tokens

> This document defines the complete color palette and design tokens for Aiveilix. Both dark and light modes share the same blue accent for a consistent brand feel across all surfaces.

---

## Brand Identity

Aiveilix uses a **deep navy dark mode** with a **glassy blue surface** feel. The primary accent is a deep, bold blue with a bright blue glow for highlights, hovers, and interactive elements. The overall vibe is premium, techy, and AI-native.

---

## Color Palette

### Core Tokens

| Token | Dark Mode | Light Mode | Usage |
|---|---|---|---|
| `--color-bg` | `#0A0F1E` | `#F0F4FF` | Page background |
| `--color-surface` | `#0F172A` | `#FFFFFF` | Cards, panels, modals |
| `--color-primary` | `#1D4ED8` | `#1D4ED8` | Buttons, links, primary actions |
| `--color-shine` | `#3B82F6` | `#3B82F6` | Hover states, glows, highlights, borders on focus |
| `--color-text` | `#F0F4FF` | `#0A0F1E` | Primary text |
| `--color-text-muted` | `#94A3B8` | `#64748B` | Secondary text, placeholders |
| `--color-border` | `#1E3A5F` | `#BFDBFE` | Card borders, dividers |
| `--color-error` | `#EF4444` | `#EF4444` | Error states, destructive actions |
| `--color-success` | `#22C55E` | `#22C55E` | Success states, completed actions |
| `--color-warning` | `#F59E0B` | `#F59E0B` | Warning states, alerts |

---

## Dark Mode Palette

```
Background:     #0A0F1E  — Very deep dark navy
Surface:        #0F172A  — Cards and panels (glassy with backdrop blur)
Primary Blue:   #1D4ED8  — Deep bold blue for buttons and actions
Shine/Glow:     #3B82F6  — Bright blue for hover, focus, and highlights
Text:           #F0F4FF  — Slightly blue-white primary text
Muted Text:     #94A3B8  — Secondary text and placeholders
Border:         #1E3A5F  — Subtle blue-dark borders
Error:          #EF4444  — Red for errors and destructive actions
Success:        #22C55E  — Green for success states
Warning:        #F59E0B  — Amber for warnings
```

### Visual Example (Dark Mode)
```
+————————————————————————————+
|  bg: #0A0F1E                |
|                             |
|  +————————————————————+    |
|  | surface: #0F172A   |    |
|  | border: #1E3A5F    |    |
|  |                    |    |
|  | text: #F0F4FF      |    |
|  | muted: #94A3B8     |    |
|  |                    |    |
|  | [ #1D4ED8 button ] |    |
|  |   hover: #3B82F6   |    |
|  +————————————————————+    |
+————————————————————————————+
```

---

## Light Mode Palette

```
Background:     #F0F4FF  — Very light blue-white
Surface:        #FFFFFF  — Clean white cards and panels
Primary Blue:   #1D4ED8  — Same deep blue (consistent brand)
Shine/Glow:     #3B82F6  — Same bright blue for hover and focus
Text:           #0A0F1E  — Deep navy text
Muted Text:     #64748B  — Secondary text and placeholders
Border:         #BFDBFE  — Soft light blue borders
Error:          #EF4444  — Red for errors
Success:        #22C55E  — Green for success
Warning:        #F59E0B  — Amber for warnings
```

### Visual Example (Light Mode)
```
+————————————————————————————+
|  bg: #F0F4FF                |
|                             |
|  +————————————————————+    |
|  | surface: #FFFFFF   |    |
|  | border: #BFDBFE    |    |
|  |                    |    |
|  | text: #0A0F1E      |    |
|  | muted: #64748B     |    |
|  |                    |    |
|  | [ #1D4ED8 button ] |    |
|  |   hover: #3B82F6   |    |
|  +————————————————————+    |
+————————————————————————————+
```

---

## Glassmorphism Effect (Dark Mode)

Cards and panels in dark mode use a glassy effect:

```css
.card {
  background: rgba(15, 23, 42, 0.8);   /* #0F172A with opacity */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid #1E3A5F;
  border-radius: 12px;
}
```

---

## Tailwind CSS Custom Colors

Add these to your `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        aiveilix: {
          bg: {
            dark: '#0A0F1E',
            light: '#F0F4FF',
          },
          surface: {
            dark: '#0F172A',
            light: '#FFFFFF',
          },
          primary: '#1D4ED8',
          shine: '#3B82F6',
          text: {
            dark: '#F0F4FF',
            light: '#0A0F1E',
          },
          muted: {
            dark: '#94A3B8',
            light: '#64748B',
          },
          border: {
            dark: '#1E3A5F',
            light: '#BFDBFE',
          },
          error: '#EF4444',
          success: '#22C55E',
          warning: '#F59E0B',
        }
      }
    }
  }
}
```

---

## CSS Variables

Add these to your global CSS file:

```css
/* Dark Mode (default) */
:root {
  --color-bg: #0A0F1E;
  --color-surface: #0F172A;
  --color-primary: #1D4ED8;
  --color-shine: #3B82F6;
  --color-text: #F0F4FF;
  --color-text-muted: #94A3B8;
  --color-border: #1E3A5F;
  --color-error: #EF4444;
  --color-success: #22C55E;
  --color-warning: #F59E0B;
}

/* Light Mode */
[data-theme="light"] {
  --color-bg: #F0F4FF;
  --color-surface: #FFFFFF;
  --color-primary: #1D4ED8;
  --color-shine: #3B82F6;
  --color-text: #0A0F1E;
  --color-text-muted: #64748B;
  --color-border: #BFDBFE;
  --color-error: #EF4444;
  --color-success: #22C55E;
  --color-warning: #F59E0B;
}
```

---

## Typography

| Token | Value | Usage |
|---|---|---|
| Font family | `Inter, sans-serif` | All text |
| Font size base | `16px` | Body text |
| Font size sm | `14px` | Secondary text |
| Font size lg | `18px` | Subheadings |
| Font size xl | `24px` | Headings |
| Font size 2xl | `32px` | Page titles |
| Font weight normal | `400` | Body |
| Font weight medium | `500` | Labels |
| Font weight semibold | `600` | Subheadings |
| Font weight bold | `700` | Headings |
| Line height | `1.6` | Body text |

---

## Border Radius

| Token | Value | Usage |
|---|---|---|
| `rounded-sm` | `6px` | Small elements (badges, tags) |
| `rounded-md` | `10px` | Buttons, inputs |
| `rounded-lg` | `12px` | Cards, panels |
| `rounded-xl` | `16px` | Modals, large cards |
| `rounded-full` | `9999px` | Avatars, pills |

---

## Shadows (Dark Mode)

```css
/* Card shadow */
box-shadow: 0 4px 24px rgba(29, 78, 216, 0.08);

/* Button glow on hover */
box-shadow: 0 0 16px rgba(59, 130, 246, 0.4);

/* Modal shadow */
box-shadow: 0 8px 40px rgba(0, 0, 0, 0.6);
```

---

*Document version: 1.0 — March 2026*
