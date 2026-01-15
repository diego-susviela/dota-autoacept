# Android App

This module contains the Android client for the Dota queue notifier.

## Features

- IP/port/token fields with QR payload paste.
- Connect button launches a foreground service to keep the WebSocket alive.
- Queue controls (start/stop) and auto-accept toggle via HTTP.
- Encrypted preferences using `EncryptedSharedPreferences`.

## Setup

1. Open `android-app/` in Android Studio.
2. Sync Gradle and run on a device (requires Android 8.0+ for the foreground service).
3. Paste the QR payload from the PC client or manually enter host/port/token.

## Notes

- The PC client must be running on the same network.
- WebSocket updates are shown through a persistent notification.
