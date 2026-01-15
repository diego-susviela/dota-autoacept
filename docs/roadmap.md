# Roadmap

This roadmap tracks the work required to move from scaffolding to a functional PC + Android solution.

## Phase 0 — Current State (Implemented)
- ✅ FastAPI server with status/config/toggle/queue control endpoints.
- ✅ WebSocket broadcast updates.
- ✅ Config validation and persistence.
- ✅ PC + Android documentation scaffolding.

## Phase 1 — PC Client MVP (Complete)

### 1.1 Configuration + Safety
- ✅ Config loader/validator with defaults.
- ✅ Safety timeout (`stop_after_match_found_s`).
- ✅ Rotating file logging.

### 1.2 Detection (Visible Cues Only)
- ✅ Screen capture for configurable region.
- ✅ Pixel sampling + color threshold detection.
- ✅ Optional OCR fallback for “ACCEPT”.
- ✅ Calibration utility to capture button coordinates.

### 1.3 Automation
- ✅ PyAutoGUI input automation.
- ✅ Human-like jitter + delay.
- ✅ Cooldown to avoid repeated clicking.

### 1.4 Server + Phone Integration
- ✅ Status timestamps + last match found metadata.
- ✅ Pairing QR code endpoint.
- ✅ Auth token enforcement + LAN-only filtering.

## Phase 2 — Android App MVP (Complete)

### 2.1 App Skeleton
- ✅ Android Studio project scaffold.
- ✅ Settings fields for IP/port/token.
- ✅ Status indicator UI.

### 2.2 Networking
- ✅ WebSocket client for updates.
- ✅ HTTP POST for toggles / queue control.
- ✅ Reconnect-ready foreground service.

### 2.3 Notifications
- ✅ Foreground service with queue status notifications.

## Phase 3 — UX + Calibration (In Progress)
- ✅ PC tray app for quick enable/disable.
- ⏳ In-app calibration flow for Accept button region.
- ⏳ Settings export/import.

## Phase 4 — Hardening + Docs (In Progress)
- ✅ Basic endpoint tests.
- ✅ Security review: token handling + IP filtering.
- ⏳ End-user docs (setup, troubleshooting).
