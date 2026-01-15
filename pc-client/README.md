# PC Client (Windows)

This folder contains the **Python/FastAPI** implementation for the Dota 2 queue notifier and auto‑accept server. It does **not** read game memory; detection uses **visible cues** only.

## What’s Included

- **FastAPI server** with token-authenticated endpoints.
- **WebSocket** broadcast channel (`/ws`) for real‑time updates.
- **Screen capture detection** (pixel sampling + optional OCR).
- **Input automation** via `pyautogui`.
- **Calibration utility** to store Accept and Queue button coordinates.
- **Pairing QR** endpoint to share IP/port/token.
- **Tray helper** to toggle auto‑accept.

## Quick Start

```bash
cd pc-client
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

## Calibration

```bash
python tools/calibrate.py
```

This records the Accept and Queue button regions to `config.json`.

## Tray Helper

```bash
python -m src.tray
```

## Endpoints

- `GET /status`
- `GET /config`
- `GET /export-config`
- `POST /import-config`
- `GET /pairing-qr`
- `POST /toggle-auto-accept`
- `POST /set-accept-region`
- `POST /set-queue-region`
- `POST /set-accept-color`
- `POST /start-queue`
- `POST /stop-queue`
- `POST /simulate-match-found` (testing)
- `WS /ws?token=...`

All requests require `X-Auth-Token` with the value configured in `config.json`.

## Notes

- Update `accept_color` in `config.json` to match the Accept button color.
- `queue_region` is used by start/stop queue commands.
- `allowed_subnets` controls which IP ranges can call the API.
- Auto-accept stops after a match is accepted (and will also stop after a delay if auto-accept is off).

