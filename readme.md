# Dota 2 Queue Notifier + Auto-Accept (PC + Android)

> **Legal/Ethical Disclaimer:** Valve/Steam have warned that third‑party software that reads data from the Dota 2 client can lead to permanent bans. A February 2023 report noted bans for software accessing hidden data, and Valve’s statement emphasized that any application reading Dota client data can be bannable. This project **must not** read memory or hidden data. It should rely only on **visible cues** (screen pixels, OCR on captured regions, or system audio) and **must be turned off once a match starts**. Use at your own risk.

This repository defines the **specification** for a two‑part system:

1. **Windows PC client** that detects match state and optionally auto‑accepts the match.
2. **Android app** that receives notifications and can toggle auto‑accept (and optionally queue actions).

The goal: let a player step away while in queue, automatically accept the match, and receive a phone notification.

---

## 1) System Overview

**Core behaviors**
- Detect **queue state changes** (searching → match found → accepted) using **visible cues** only.
- If enabled, **auto‑accept** by simulating a human click on the “Accept” button.
- **Notify** the phone with status updates.
- Provide **remote controls** from the phone (toggle auto‑accept; optional start/stop queue).

**Security**
- Communication must be **authenticated** (shared token).
- Default scope is **local network only**.
- Optional port‑forwarding is user‑managed if remote access is desired.

**Ethics / risk**
- No memory reads, no game injection, no hidden data.
- Use only what a human could see or hear.
- **Turn the program off after the match starts**.

---

## 2) PC Client (Windows)

### 2.1 Responsibilities
- **Detect queue state** (searching, match found, accepted) from the Dota 2 client.
- **Auto‑accept** by simulating a mouse click on the “Accept” button.
- **Send notifications** to the Android app when state changes.
- **Expose control endpoints** for toggling auto‑accept and optional queue control.
- Run as a **tray app** or lightweight background service.

### 2.2 Implementation Guidance

**Language / framework options**
- **Python**: `pyautogui` for input automation; `mss`/`Pillow` for capture; `pytesseract` for OCR; `Flask` or `FastAPI` for HTTP.
- **Node.js**: `robotjs` (or AutoIT wrapper) for input; `express` or `ws` for server.
- **AutoIT** (optional) to reliably detect window focus and send clicks.

**Queue detection (safe)**
- Capture a **small screen region** where the Accept button appears.
- Use **pixel color thresholds** or OCR to detect “ACCEPT”.
- Optional fallback: detect the **match found audio** via system audio analysis.

**Auto‑accept**
- Once a match is found and auto‑accept is enabled:
  - Wait a random **0.2–0.5s** (human‑like delay)
  - Click the Accept button coordinates.

**Server endpoints (example)**
- `GET /status` → `{ searching, match_found, accepted, auto_accept_enabled }`
- `POST /toggle-auto-accept` → `{ enabled: true/false }`
- `POST /start-queue` → simulate “Find Match”
- `POST /stop-queue` → simulate “Cancel Search”

**Security**
- Require a shared **token** on each request (header or query param).
- Bind server to **LAN** by default, not public interfaces.

---

## 3) Android Application

### 3.1 Responsibilities
- Receive **status notifications** (searching / match found / accepted).
- Allow **toggle auto‑accept**.
- Optional: **start/stop queue**.
- Store server IP/port and token securely.

### 3.2 Implementation Guidance

**Language / framework**
- Kotlin or Java in Android Studio.
- Use **OkHttp** or **WebSocket** for persistent connection.

**Security**
- Store the token in encrypted preferences.
- Use **HTTPS** when possible, or local‑only HTTP over trusted LAN.

**User Experience**
- Minimal UI: status indicator, auto‑accept toggle, optional queue buttons.
- Notifications with **actions** (e.g., manual accept, dismiss).

---

## 4) Proposed Project Structure

```
/dota-autoaccept
  /pc-client
    /src
      detection/
      automation/
      server/
      tray-ui/
    config.json
    README.md

  /android-app
    /app
      /src
    README.md

  /docs
    setup.md
    pairing.md
    troubleshooting.md
```

---

## 5) Ethical + Practical Considerations

- **Risk of bans**: do not read memory or game internals.
- **UI changes**: game patches can break pixel detection; provide a calibration UI.
- **Security**: authenticated access only; local network by default.
- **Do not run in‑match**: auto‑accept should stop after game launch.

---

## 6) Deliverables

**PC Client**
- Windows executable or script
- Local server for phone integration
- Documentation (installation, configuration)

**Android App**
- Installable APK
- Background service for notifications
- Documentation for pairing and usage

**Documentation**
- Setup, configuration, troubleshooting
- Explicit ban risk warning

---

## 6.1 Roadmap + Current Gaps (What’s Missing for Functionality)

**Roadmap:** See `docs/roadmap.md` for a phased plan and milestones.

**Missing to reach a functional MVP:**
- ✅ **Screen capture + pixel detection** for the Accept button.
- ✅ **Input automation** (pyautogui) to click Accept and start/stop queue.
- ✅ **Calibration** flow to capture Accept and queue button coordinates.
- ✅ **Config persistence + validation** for auth token and settings.
- ✅ **Android app MVP** (UI, WebSocket client, notifications, and controls).

---

## 7) Example Workflow

1. User starts the PC client and enables auto‑accept.
2. PC app shows QR code with server IP + token.
3. Android app scans QR code and connects.
4. User starts queue in Dota 2.
5. PC detects “searching” and updates phone.
6. Match found → PC sends notification and auto‑accepts.
7. After match starts, the PC client stops monitoring.

---

## 8) Notes on Safe Detection

To avoid violating Valve’s policy, **do not**:
- Inject into the Dota process
- Read memory from the Dota client
- Scrape hidden data

Instead, use:
- **Pixel sampling**
- OCR from the visible screen
- **Audio cue** detection

---

## 9) Next Steps

- ✅ PC client skeleton (FastAPI server + stubs) lives in `pc-client/`.
- ⏳ Android app scaffolding to follow in `android-app/`.
- ⏳ Calibration UI for Accept button region.
- ⏳ Test on a secondary account if possible.
