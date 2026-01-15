from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
from typing import Any, Dict, List

import qrcode
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from automation.input_controller import ClickRegion, InputController
from config import AppConfig, ConfigError, load_config, save_config, update_config
from detection.detector import DetectorConfig, QueueDetector
from logging_config import configure_logging
from server.auth import require_token
from server.state import AppState, QueueState

logger = logging.getLogger(__name__)

app = FastAPI(title="Dota Auto-Accept Server")
state = AppState()
connected_clients: List[WebSocket] = []


class ToggleRequest(BaseModel):
    enabled: bool


class StatusResponse(BaseModel):
    queue_state: str
    auto_accept_enabled: bool
    last_event: str | None
    last_updated: str | None
    last_match_found: str | None


class RegionRequest(BaseModel):
    x: int
    y: int
    width: int
    height: int


class ColorRequest(BaseModel):
    r: int
    g: int
    b: int
    tolerance: int


class ConfigResponse(BaseModel):
    bind_host: str
    bind_port: int
    auto_accept_enabled: bool
    accept_delay_min_s: float
    accept_delay_max_s: float
    poll_interval_s: float
    enable_ocr: bool
    stop_after_match_found_s: float


class ConfigImportRequest(BaseModel):
    config: AppConfig


def _accept_region(config: AppConfig) -> ClickRegion:
    region = config.accept_region
    return ClickRegion(region.x, region.y, region.width, region.height)


def _queue_region(config: AppConfig) -> ClickRegion:
    region = config.queue_region
    return ClickRegion(region.x, region.y, region.width, region.height)


def _restart_detector(config: AppConfig) -> None:
    app.state.detector.stop()
    app.state.detector = QueueDetector(
        DetectorConfig(
            poll_interval_s=config.poll_interval_s,
            region=(
                config.accept_region.x,
                config.accept_region.y,
                config.accept_region.width,
                config.accept_region.height,
            ),
            target_color=(config.accept_color.r, config.accept_color.g, config.accept_color.b),
            tolerance=config.accept_color.tolerance,
            enable_ocr=config.enable_ocr,
            ocr_text=config.ocr_text,
        ),
        handle_state_change,
    )
    app.state.detector_task = asyncio.create_task(app.state.detector.run())


async def _stop_after_delay(delay: float) -> None:
    await asyncio.sleep(delay)
    app.state.detector.stop()


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
    if new_state == state.queue_state and new_state != QueueState.match_found:
        return
    state.queue_state = new_state
    state.mark_event(f"state_changed:{new_state.value}")
    await broadcast({"type": "state", "payload": state.as_dict()})

    if new_state == QueueState.match_found and state.auto_accept_enabled:
        controller: InputController = app.state.input_controller
        region = _accept_region(app.state.config)
        controller.click_accept(region)
        await handle_state_change(QueueState.accepted)
    elif new_state == QueueState.match_found:
        delay = app.state.config.stop_after_match_found_s
        if delay > 0:
            asyncio.create_task(_stop_after_delay(delay))

    if new_state == QueueState.accepted:
        app.state.detector.stop()


@app.on_event("startup")
async def startup() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        raise RuntimeError(f"Invalid configuration: {exc}") from exc

    configure_logging(config.log_path, config.log_level)
    logger.info("Starting PC client server.")
    if config.bind_host not in {"127.0.0.1", "localhost"}:
        logger.warning("Server is bound to a non-localhost interface.")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    state.auto_accept_enabled = config.auto_accept_enabled
    detector = QueueDetector(
        DetectorConfig(
            poll_interval_s=config.poll_interval_s,
            region=(
                config.accept_region.x,
                config.accept_region.y,
                config.accept_region.width,
                config.accept_region.height,
            ),
            target_color=(config.accept_color.r, config.accept_color.g, config.accept_color.b),
            tolerance=config.accept_color.tolerance,
            enable_ocr=config.enable_ocr,
            ocr_text=config.ocr_text,
        ),
        handle_state_change,
    )
    app.state.config = config
    app.state.detector = detector
    app.state.detector_task = asyncio.create_task(detector.run())
    app.state.input_controller = InputController(
        config.accept_delay_min_s,
        config.accept_delay_max_s,
        config.click_cooldown_s,
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    detector = app.state.detector
    detector.stop()
    task = app.state.detector_task
    task.cancel()


@app.get("/status", response_model=StatusResponse)
async def get_status(request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    return state.as_dict()


@app.get("/config", response_model=ConfigResponse)
async def get_config(request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    config = load_config()
    return config.model_dump(include={
        "bind_host",
        "bind_port",
        "auto_accept_enabled",
        "accept_delay_min_s",
        "accept_delay_max_s",
        "poll_interval_s",
        "enable_ocr",
        "stop_after_match_found_s",
    })


@app.get("/export-config")
async def export_config(request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    config = load_config()
    return {"config": config.model_dump()}


@app.post("/import-config")
async def import_config(payload: ConfigImportRequest, request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    save_config(payload.config)
    app.state.config = load_config()
    _restart_detector(app.state.config)
    return {"status": "ok"}


@app.get("/pairing-qr")
async def pairing_qr(request: Request) -> Dict[str, str]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    payload = json.dumps(
        {
            "host": app.state.config.bind_host,
            "port": app.state.config.bind_port,
            "token": app.state.config.auth_token,
        }
    )
    qr = qrcode.make(payload)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {"image_base64": encoded}


@app.post("/toggle-auto-accept")
async def toggle_auto_accept(payload: ToggleRequest, request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    updated = update_config({"auto_accept_enabled": payload.enabled})
    state.auto_accept_enabled = updated.auto_accept_enabled
    app.state.config = updated
    await broadcast({"type": "auto_accept", "payload": state.as_dict()})
    return {"auto_accept_enabled": state.auto_accept_enabled}


@app.post("/set-accept-region")
async def set_accept_region(payload: RegionRequest, request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    updated = update_config({"accept_region": payload.model_dump()})
    app.state.config = updated
    _restart_detector(updated)
    return {"accept_region": updated.accept_region.model_dump()}


@app.post("/set-queue-region")
async def set_queue_region(payload: RegionRequest, request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    updated = update_config({"queue_region": payload.model_dump()})
    app.state.config = updated
    return {"queue_region": updated.queue_region.model_dump()}


@app.post("/set-accept-color")
async def set_accept_color(payload: ColorRequest, request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    updated = update_config({"accept_color": payload.model_dump()})
    app.state.config = updated
    _restart_detector(updated)
    return {"accept_color": updated.accept_color.model_dump()}


@app.post("/start-queue")
async def start_queue(request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    app.state.input_controller.start_queue(_queue_region(app.state.config))
    await handle_state_change(QueueState.searching)
    return state.as_dict()


@app.post("/stop-queue")
async def stop_queue(request: Request) -> Dict[str, Any]:
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    app.state.input_controller.stop_queue(_queue_region(app.state.config))
    await handle_state_change(QueueState.idle)
    return state.as_dict()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if token != app.state.config.auth_token:
        await websocket.close(code=4401)
        return
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
    require_token(request, app.state.config.auth_token, app.state.config.allowed_subnets)
    await handle_state_change(QueueState.match_found)
    return state.as_dict()
