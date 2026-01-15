package com.example.dotaautoaccept

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MediaType.Companion.toMediaType
import org.json.JSONObject

class QueueService : Service() {
    private val httpClient = OkHttpClient()
    private var socketClient: QueueSocketClient? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val host = intent?.getStringExtra("host") ?: return START_NOT_STICKY
        val port = intent.getStringExtra("port") ?: "8765"
        val token = intent.getStringExtra("token") ?: ""
        startForeground(1, buildForegroundNotification())
        createNotificationChannel()

        val wsUrl = "ws://$host:$port/ws?token=$token"
        socketClient = QueueSocketClient(
            httpClient,
            wsUrl,
            onMessage = { message ->
                handleMessage(message)
                broadcastStatus(message)
            },
            onFailure = {
                broadcastStatus("{\"type\":\"state\",\"payload\":{\"queue_state\":\"disconnected\"}}")
            }
        )
        socketClient?.connect()
        return START_STICKY
    }

    override fun onDestroy() {
        socketClient?.close()
        super.onDestroy()
    }

    private fun broadcastStatus(message: String) {
        val intent = Intent("QUEUE_STATUS")
        intent.putExtra("payload", message)
        sendBroadcast(intent)
    }

    private fun handleMessage(text: String) {
        val json = JSONObject(text)
        val payload = json.optJSONObject("payload") ?: return
        val state = payload.optString("queue_state", "unknown")
        if (state == "match_found") {
            notifyUser("Match found", "Dota 2 match found")
        }
        if (state == "accepted") {
            notifyUser("Match accepted", "Auto-accept completed")
        }
    }

    fun postJson(host: String, port: String, token: String, path: String, json: String) {
        val url = "http://$host:$port$path"
        val request = Request.Builder()
            .url(url)
            .addHeader("X-Auth-Token", token)
            .post(json.toRequestBody("application/json".toMediaType()))
            .build()
        httpClient.newCall(request).enqueue(object : okhttp3.Callback {
            override fun onFailure(call: okhttp3.Call, e: java.io.IOException) {}
            override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                response.close()
            }
        })
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "queue_updates",
                "Queue Updates",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun notifyUser(title: String, message: String) {
        val notification = NotificationCompat.Builder(this, "queue_updates")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()
        NotificationManagerCompat.from(this).notify(title.hashCode(), notification)
    }

    private fun buildForegroundNotification(): Notification {
        return NotificationCompat.Builder(this, "queue_updates")
            .setContentTitle("Dota queue watcher")
            .setContentText("Listening for match updates")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()
    }
}
