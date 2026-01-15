package com.example.dotaautoaccept

import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject

class QueueSocketClient(
    private val host: String,
    private val port: Int,
    private val token: String,
    private val onStatus: (String) -> Unit
) {
    private val client = OkHttpClient()
    private var socket: WebSocket? = null

    fun connect() {
        val request = Request.Builder()
            .url("ws://$host:$port/ws?token=$token")
            .build()
        socket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val status = parseStatus(text)
                if (status != null) {
                    onStatus(status)
                }
            }
        })
    }

    fun close() {
        socket?.close(1000, "Closing")
    }

    private fun parseStatus(text: String): String? {
        return try {
            val json = JSONObject(text)
            val payload = json.optJSONObject("payload") ?: return null
            val state = payload.optString("queue_state", "unknown")
            "Queue: $state"
        } catch (ex: Exception) {
            null
        }
    }
}
