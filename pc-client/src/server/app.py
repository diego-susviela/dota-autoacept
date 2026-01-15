from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from automation.input_controller import InputController
from detection.detector import DetectorConfig, QueueDetector
from server.auth import require_token
from server.state import AppState, QueueState

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"

app = FastAPI(title="Dota Auto-Accept Server")
state = AppState()
connected_clients: List[WebSocket] = []


class ToggleRequest(BaseModel):
    enabled: bool


class StatusResponse(BaseModel):
    queue_state: str
    auto_accept_enabled: bool
    last_event: str | None


def load_config() -> Dict[str, Any]:
    data = json.loads(CONFIG_PATH.read_text())
    state.auto_accept_enabled = bool(data.get("auto_accept_enabled", True))
    return data


async def broadcast(message: Dict[str, Any]) -> None:
    if not connected_clients:
        return
    disconnected: List[WebSocket] = []
    for client in connected_clients:
        try:
            await client.send_json(message)
        except WebSocketDisconnect:
            disconnected.append(client)
    for client in disconnected:
        connected_clients.remove(client)


async def handle_state_change(new_state: QueueState) -> None:
    state.queue_state = new_state
    state.last_event = f"state_changed:{new_state.value}"
    await broadcast({"type": "state", "payload": state.as_dict()})


@app.on_event("startup")
async def startup() -> None:
    config = load_config()
    detector = QueueDetector(DetectorConfig(), handle_state_change)
    app.state.detector = detector
    app.state.detector_task = asyncio.create_task(detector.run())
    app.state.input_controller = InputController(
        config["accept_delay_min_s"],
        config["accept_delay_max_s"],
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    detector = app.state.detector
    detector.stop()
    task = app.state.detector_task
    task.cancel()


@app.get("/status", response_model=StatusResponse)
async def get_status(request: Request) -> Dict[str, Any]:
    config = load_config()
    require_token(request, config["auth_token"])
    return state.as_dict()


@app.post("/toggle-auto-accept")
async def toggle_auto_accept(payload: ToggleRequest, request: Request) -> Dict[str, Any]:
    config = load_config()
    require_token(request, config["auth_token"])
    state.auto_accept_enabled = payload.enabled
    await broadcast({"type": "auto_accept", "payload": state.as_dict()})
    return {"auto_accept_enabled": state.auto_accept_enabled}


@app.post("/start-queue")
async def start_queue(request: Request) -> Dict[str, Any]:
    config = load_config()
    require_token(request, config["auth_token"])
    app.state.input_controller.start_queue()
    await handle_state_change(QueueState.searching)
    return state.as_dict()


@app.post("/stop-queue")
async def stop_queue(request: Request) -> Dict[str, Any]:
    config = load_config()
    require_token(request, config["auth_token"])
    app.state.input_controller.stop_queue()
    await handle_state_change(QueueState.idle)
    return state.as_dict()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    connected_clients.append(websocket)
    await websocket.send_json({"type": "state", "payload": state.as_dict()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.post("/simulate-match-found")
async def simulate_match_found(request: Request) -> Dict[str, Any]:
    """
    Temporary helper for testing notifications. Remove once detection is implemented.
    """
    config = load_config()
    require_token(request, config["auth_token"])
    await handle_state_change(QueueState.match_found)
    if state.auto_accept_enabled:
        app.state.input_controller.click_accept()
        await handle_state_change(QueueState.accepted)
    return state.as_dict()
