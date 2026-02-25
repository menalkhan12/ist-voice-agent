# IST Voice Assistant – Admin Dashboard

React admin dashboard for the AI-powered voice assistant (institutional use).  
Restricted to **@ist.edu.pk** emails. Default admin: **admin@ist.edu.pk** / **admin**.

## Run locally

```bash
cd admin-dashboard
npm install
npm run dev
```

Open http://localhost:3000. Log in with `admin@ist.edu.pk` / `admin`.

## Build

```bash
npm run build
```

Output is in `dist/`. Serve with any static host or mount under the main app.

## Features

- **Login**: Only emails ending in `@ist.edu.pk`; red validation message for invalid format. Token stored in localStorage; redirect to `/profile` on success. All other routes protected.
- **Layout**: Fixed top navbar (50px, navy), collapsible sidebar (220px / 70px), scrollable content. Hamburger toggles sidebar. Navbar shows email prefix and accent-yellow Logout.
- **User Profile**: Email and role card; Edit Profile, Change Password, View Login History. Change Password updates stored password.
- **Call Logs**: Table (Session ID, User Email, Duration, STT/LLM/TTS/E2E, Confidence, Timestamp). Search/filter. Click row for transcript and AI response.
- **Reports & Analytics**: Metric cards (Total Calls, Successful Responses, Low Confidence, AI Accuracy). Chart placeholder for STT/LLM/TTS/E2E trends.
- **Database (Knowledge Base)**: Add/edit documents, save, last updated and version. Ready for backend integration.
- **Settings**: Add/delete user, change user password (@ist.edu.pk only); Light/Dark mode; Backup / Restore placeholders. User management only for admin role.

## Backend integration (planned)

- Dashboard will call a central API for call logs and metrics; voice agent will send metrics to the same backend.
- Knowledge Base updates will persist to the central DB; the AI will load updated knowledge before answering.

## Design

- **Primary**: Navy (`#1e3a5f`) for navbar and headings.
- **Sidebar**: Dark (`#152a45`).
- **Accent**: Yellow (`#f0b429`) for Logout and key metrics.
- **Content**: Light gray (`#f5f7fa`); white cards, 10px radius, soft shadow.
