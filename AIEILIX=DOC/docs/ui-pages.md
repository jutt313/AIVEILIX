# Aiveilix — UI Pages

> This document describes every page in the Aiveilix frontend. Each page will be updated with full component details, layouts, and interactions as the product develops.

---

## Tech

- **Framework:** React
- **Styling:** Tailwind CSS
- **Routing:** React Router
- **Themes:** Light and dark mode (saved to user profile)

---

## Pages List

| # | Page | Route | Notes |
|---|---|---|---|
| 1 | Landing Page | `/` | Includes pricing section |
| 2 | Signup Page | `/signup` | Email, Google, GitHub |
| 3 | Login Page | `/login` | Email, Google, GitHub |
| 4 | Forgot Password Page | `/forgot-password` | Sends reset email |
| 5 | Reset Password Page | `/reset-password` | Token from email |
| 6 | Email Verification Page | `/verify-email` | Token from email |
| 7 | Onboarding Flow | `/onboarding` | Multi-step, first login only |
| 8 | Dashboard | `/dashboard` | Main home screen |
| 9 | Bucket Page | `/dashboard/buckets/{bucket_id}` | Files + chat |
| 10 | Doc Page | `/dashboard/buckets/{bucket_id}/files/{file_id}` | File details + summary |
| 11 | Privacy Policy Page | `/privacy` | Legal |
| 12 | Terms of Service Page | `/terms` | Legal |
| 13 | Tokushoho Page | `/tokushoho` | Required in Japan for Stripe |
| 14 | 404 Page | `*` | Page not found |

---

## Notes

- Profile, settings, billing, and notifications are **not separate pages**
- They live inside the Dashboard as popups and dropdowns
- Each page above will be updated with full component breakdowns, layouts, and interactions

---

*Document version: 1.0 — March 2026 — To be updated*
