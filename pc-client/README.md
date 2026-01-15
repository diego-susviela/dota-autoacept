# PC Client (Windows)

Python/FastAPI server that detects Dota 2 queue state via screen capture and can auto‑accept matches. It uses **visible cues only** (pixel sampling + optional OCR).

## Features

- FastAPI server with status, config, queue control, and pairing QR endpoints.
- WebSocket broadcast updates at `/ws?token=...`.
- Screen capture detection via `mss` + `Pillow` with optional OCR (`pytesseract`).
- Input automation via `pyautogui` with jitter and cooldowns.
- Config validation + persistence with safety timeout.
- LAN‑only subnet filtering + token authentication.
- Calibration tool and tray toggle helper.

## Quick Start

```bash
cd pc-client
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.main
```

## Endpoints

- `GET /status`
- `GET /config`
- `POST /config`
- `GET /pairing-qr`
- `POST /toggle-auto-accept`
- `POST /start-queue`
- `POST /stop-queue`
- `WS /ws?token=...`

All requests require `X-Auth-Token` (or `?token=` for WebSocket) matching the token in `config.json`.

## Calibration

```bash
python -m src.calibrate
```

Follow prompts to capture the Accept button and queue button regions.

## Tray Helper (Windows)

```bash
python -m src.tray_helper
```

Provides a tray icon to quickly toggle auto‑accept.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
