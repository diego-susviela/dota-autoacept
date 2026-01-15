# Android App

This directory contains the Android client built with Kotlin.

## Features

- Connects to the PC server over WebSocket via a **foreground service**.
- Toggle auto‑accept and start/stop queue via HTTP.
- Local notifications for match found / accepted.
- Stores IP/port/token in **encrypted preferences**.
- Supports pasting a QR payload JSON from `/pairing-qr`.

## Build

Open `android-app/` in Android Studio and run the app on a device/emulator.

## Configuration

Use the UI to enter:
- PC IP address
- PC port (default 8765)
- Auth token (matches `pc-client/config.json`)

