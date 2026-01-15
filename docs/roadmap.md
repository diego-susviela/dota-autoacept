# Roadmap

This roadmap tracks the work required to move from scaffolding to a functional PC + Android solution.

## Phase 0 — Current State (Scaffolding)
- ✅ FastAPI server skeleton, auth, WebSocket broadcast.
- ✅ Placeholder detection loop.
- ✅ Placeholder input automation.
- ✅ Initial documentation and project structure.

## Phase 1 — Make the PC Client Functional (MVP)

### 1.1 Configuration + Safety
- ✅ Add a **config loader/validator** with defaults and validation errors.
- ✅ Add a **shutdown guard** that stops detection when a match is accepted or a match loads.
- ✅ Add **structured logging** (rotating file logs).

### 1.2 Detection (Visible Cues Only)
- ✅ Implement **screen capture** for a configurable region (Accept button area).
- ✅ Add **pixel sampling** + color threshold detection.
- ✅ Add optional **OCR fallback** for “ACCEPT”.
- ✅ Add **calibration utility** to capture button coordinates.

### 1.3 Automation
- ✅ Replace stub `InputController` with **pyautogui** clicks.
- ✅ Add optional **human-like jitter** (small random offset) to click coords.
- ✅ Add **rate limit / cooldown** to avoid repeated clicking.

### 1.4 Server + Phone Integration
- ✅ Persist auto-accept state in config.
- ✅ Add **status change events** with timestamps.
- ✅ Add a **pairing QR code** endpoint.
- ✅ Add **CORS** middleware for HTTP clients.
- ✅ Add **IP filtering** for allowed subnets.
- ✅ Add **WebSocket token auth**.

## Phase 2 — Android App MVP

### 2.1 App Skeleton
- ✅ Scaffold Android Studio project in `android-app/`.
- ✅ Add **settings screen** for IP/port/token.
- ✅ Add **status screen** for queue state.

### 2.2 Networking
- ✅ Implement **WebSocket client** for updates (foreground service).
- ✅ Implement **HTTP POST** for toggles / queue control.
- ✅ Add **reconnect logic** and error handling (basic reconnect on service restart).

### 2.3 Notifications
- ✅ Add **foreground service** to keep socket alive.
- ✅ Implement **match found** and **accepted** notifications.

## Phase 3 — UX + Calibration
- ✅ PC tray app for enable/disable + quick config.
- ✅ In-app calibration flow for Accept button region (PC tool).
- ✅ Settings export/import.
- ✅ Encrypted preferences for Android credentials.

## Phase 4 — Hardening + Docs
- ✅ Automated tests for server endpoints.
- ✅ Security review: token handling + IP filtering.
- ✅ End-user docs (setup, troubleshooting).

