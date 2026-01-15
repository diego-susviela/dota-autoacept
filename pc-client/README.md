# PC Client (Windows)

This folder contains the initial **Python/FastAPI** skeleton for the Dota 2 queue notifier and auto‑accept server. It does **not** read game memory; the detector is a placeholder awaiting pixel/OCR/audio logic.

## What’s Included

- **FastAPI server** with token-authenticated endpoints.
- **WebSocket** broadcast channel (`/ws`) for real‑time updates.
- **Stub detection loop** ready for pixel/OCR implementation.
- **Input automation stubs** (replace with `pyautogui`/AutoIT).

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
- `POST /toggle-auto-accept`
- `POST /start-queue`
- `POST /stop-queue`
- `POST /simulate-match-found` (temporary helper)
- `WS /ws`

All requests require `X-Auth-Token` with the value configured in `config.json`.

## Next Steps

- Implement detection using **screen capture + pixel/OCR**.
- Replace `InputController` stubs with real automation.
- Add calibration UI for capture regions.

