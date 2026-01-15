package com.example.dotaautoaccept

import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener

class QueueSocketClient(
    private val httpClient: OkHttpClient,
    private val url: String,
    private val onMessage: (String) -> Unit,
    private val onFailure: () -> Unit
) {
    private var webSocket: WebSocket? = null

    fun connect() {
        webSocket?.close(1000, "reconnect")
        val request = Request.Builder().url(url).build()
        webSocket = httpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                onMessage(text)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                onFailure()
            }
        })
    }

    fun close() {
        webSocket?.close(1000, "close")
    }
}
