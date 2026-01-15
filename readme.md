# Dota 2 Queue Notifier + Auto-Accept (PC + Android)

> **Legal/Ethical Disclaimer:** Valve/Steam have warned that third‑party software that reads data from the Dota 2 client can lead to permanent bans. This project **must not** read memory or hidden data. It should rely only on **visible cues** (screen pixels, OCR on captured regions, or system audio) and **must be turned off once a match starts**. Use at your own risk.

This repository provides a **PC + Android** solution to monitor Dota 2 queue status, auto-accept matches, and send status updates to a phone.

---

## 1) Responsibilities

### PC Client (Windows)
- Detect queue state changes using **visible cues only**.
- Auto‑accept matches by simulating a **human click** on the “Accept” button.
- Expose HTTP + WebSocket endpoints for status, controls, and pairing.
- Remain LAN‑only by default and require a shared auth token.

### Android App
- Connect to the PC client via HTTP/WebSocket.
- Display queue status updates and notifications.
- Toggle auto‑accept and optionally start/stop queue.
- Store the token securely using encrypted preferences.

---

## 2) Ethics + Security

- **No memory reads, no injection, no hidden data.**
- Only use what a human can see or hear on screen.
- **Stop the automation once a match starts.**
- Enforce **token-based authentication** and **LAN-only** subnet access.

---

## 3) Workflow Overview

1. Launch the PC client and enable auto‑accept.
2. Use the pairing QR code to load host/port/token in the Android app.
3. Start queue in Dota 2.
4. PC client detects searching → match found and notifies the phone.
5. Auto‑accept fires and updates the status feed.
6. After match start, the PC client stops monitoring.

---

## 4) Current Gaps / MVP Status

**Roadmap:** See `docs/roadmap.md` for phased milestones and completion status.

**MVP status:**
- ✅ PC client is functional (detection, automation, auth, logging, calibration).
- ✅ Android app scaffold + networking + notifications are in place.
- ⏳ Remaining gaps are mostly **UX polish** (in‑app calibration flow, settings export).

---

## 5) Repository Structure

```
/dota-autoaccept
  /pc-client
    /src
    config.json
    README.md

  /android-app
    /app
    README.md

  /docs
    roadmap.md
```

---

## 6) Roadmap

See `docs/roadmap.md` for the detailed plan and completed milestones.
