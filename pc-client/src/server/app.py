from __future__ import annotations

import asyncio
import base64
import io
import json
from typing import Any, Dict, List

import qrcode
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from automation.input_controller import InputController
from detection.detector import QueueDetector
from server.auth import enforce_subnet, enforce_subnet_ws, require_token
from server.config import AppConfig, load_config, save_config
from server.logging_config import setup_logging
from server.state import AppState, QueueState

app = FastAPI(title="Dota Auto-Accept Server")
state = AppState()
connected_clients: List[WebSocket] = []
match_found_timeout_task: asyncio.Task | None = None


class ToggleRequest(BaseModel):
    enabled: bool


class StatusResponse(BaseModel):
    queue_state: str
    auto_accept_enabled: bool
    last_event: str | None
    last_state_change_at: str | None
    last_match_found_at: str | None


class ConfigUpdateRequest(BaseModel):
    auto_accept_enabled: bool | None = None
    accept_delay_min_s: float | None = None
    accept_delay_max_s: float | None = None
    accept_click_jitter_px: int | None = None
    accept_click_cooldown_s: float | None = None
    stop_after_match_found_s: float | None = None
    accept_region: Dict[str, int] | None = None
    queue_region: Dict[str, int] | None = None
    accept_pixel_probe: Dict[str, int] | None = None


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
    global match_found_timeout_task
    state.set_state(new_state, f"state_changed:{new_state.value}")
    if new_state == QueueState.match_found:
        if match_found_timeout_task:
            match_found_timeout_task.cancel()
        match_found_timeout_task = asyncio.create_task(handle_match_found_timeout())
        if state.auto_accept_enabled:
            app.state.input_controller.click_accept(get_config().accept_region)
            state.set_state(QueueState.accepted, "auto_accept:clicked")
    await broadcast({"type": "state", "payload": state.as_dict()})


@app.on_event("startup")
async def startup() -> None:
    config = load_config()
    setup_logging(config.log_file)
    state.auto_accept_enabled = config.auto_accept_enabled
    app.state.config = config
    detector = QueueDetector(config, handle_state_change)
    app.state.detector = detector
    app.state.detector_task = asyncio.create_task(detector.run())
    app.state.input_controller = InputController(
        config.accept_delay_min_s,
        config.accept_delay_max_s,
        config.accept_click_jitter_px,
        config.accept_click_cooldown_s,
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    detector = app.state.detector
    detector.stop()
    task = app.state.detector_task
    task.cancel()


@app.get("/status", response_model=StatusResponse)
async def get_status(request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    return state.as_dict()


@app.post("/toggle-auto-accept")
async def toggle_auto_accept(payload: ToggleRequest, request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    state.auto_accept_enabled = payload.enabled
    config.auto_accept_enabled = payload.enabled
    save_config(config)
    await broadcast({"type": "auto_accept", "payload": state.as_dict()})
    return {"auto_accept_enabled": state.auto_accept_enabled}


@app.post("/start-queue")
async def start_queue(request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    app.state.input_controller.start_queue(config.queue_region)
    await handle_state_change(QueueState.searching)
    return state.as_dict()


@app.post("/stop-queue")
async def stop_queue(request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    app.state.input_controller.stop_queue(config.queue_region)
    await handle_state_change(QueueState.idle)
    return state.as_dict()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    config = get_config()
    if not enforce_subnet_ws(websocket.client.host if websocket.client else None, config.allowed_subnets):
        await websocket.close(code=1008)
        return
    token = websocket.query_params.get("token")
    if not token or token != config.auth_token:
        await websocket.close(code=1008)
        return
    await websocket.accept()
    connected_clients.append(websocket)
    await websocket.send_json({"type": "state", "payload": state.as_dict()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.get("/config")
async def get_config_endpoint(request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    return config.model_dump()


@app.post("/config")
async def update_config(payload: ConfigUpdateRequest, request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    data = config.model_dump()
    for key, value in payload.model_dump(exclude_none=True).items():
        data[key] = value
    updated = AppConfig.model_validate(data)
    save_config(updated)
    app.state.config = updated
    app.state.input_controller = InputController(
        updated.accept_delay_min_s,
        updated.accept_delay_max_s,
        updated.accept_click_jitter_px,
        updated.accept_click_cooldown_s,
    )
    return updated.model_dump()


@app.get("/pairing-qr")
async def pairing_qr(request: Request) -> Dict[str, Any]:
    config = get_config()
    enforce_subnet(request, config.allowed_subnets)
    require_token(request, config.auth_token)
    payload = json.dumps(
        {
            "host": config.bind_host,
            "port": config.bind_port,
            "token": config.auth_token,
        }
    )
    qr = qrcode.make(payload)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {"payload": payload, "qr_base64": encoded}


def get_config() -> AppConfig:
    return app.state.config


async def handle_match_found_timeout() -> None:
    config = get_config()
    if config.stop_after_match_found_s <= 0:
        return
    await asyncio.sleep(config.stop_after_match_found_s)
    if state.queue_state == QueueState.match_found:
        state.auto_accept_enabled = False
        state.set_state(QueueState.idle, "timeout:auto_accept_disabled")
        await broadcast({"type": "timeout", "payload": state.as_dict()})
