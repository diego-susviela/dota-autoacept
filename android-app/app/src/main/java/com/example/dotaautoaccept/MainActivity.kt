package com.example.dotaautoaccept

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class MainActivity : AppCompatActivity() {
    private val client = OkHttpClient()
    private lateinit var statusText: TextView
    private lateinit var hostInput: EditText
    private lateinit var portInput: EditText
    private lateinit var tokenInput: EditText
    private lateinit var qrPayloadInput: EditText
    private var autoAcceptEnabled = true

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        hostInput = findViewById(R.id.hostInput)
        portInput = findViewById(R.id.portInput)
        tokenInput = findViewById(R.id.tokenInput)
        qrPayloadInput = findViewById(R.id.qrPayloadInput)

        val masterKey = MasterKey.Builder(this)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        val sharedPrefs = EncryptedSharedPreferences.create(
            this,
            "dota_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        hostInput.setText(sharedPrefs.getString("host", ""))
        portInput.setText(sharedPrefs.getString("port", ""))
        tokenInput.setText(sharedPrefs.getString("token", ""))

        findViewById<Button>(R.id.connectButton).setOnClickListener {
            val info = readConnection(sharedPrefs)
            if (info != null) {
                sharedPrefs.edit()
                    .putString("host", info.host)
                    .putString("port", info.port.toString())
                    .putString("token", info.token)
                    .apply()
                startService(Intent(this, QueueService::class.java).apply {
                    putExtra("host", info.host)
                    putExtra("port", info.port)
                    putExtra("token", info.token)
                })
                statusText.text = "Status: Connected"
            }
        }

        findViewById<Button>(R.id.toggleButton).setOnClickListener {
            val info = readConnection(sharedPrefs) ?: return@setOnClickListener
            autoAcceptEnabled = !autoAcceptEnabled
            sendPost(info, "/toggle-auto-accept", JSONObject().put("enabled", autoAcceptEnabled))
        }

        findViewById<Button>(R.id.startQueueButton).setOnClickListener {
            val info = readConnection(sharedPrefs) ?: return@setOnClickListener
            sendPost(info, "/start-queue", null)
        }

        findViewById<Button>(R.id.stopQueueButton).setOnClickListener {
            val info = readConnection(sharedPrefs) ?: return@setOnClickListener
            sendPost(info, "/stop-queue", null)
        }
    }

    private fun readConnection(sharedPrefs: android.content.SharedPreferences): ConnectionInfo? {
        val payload = qrPayloadInput.text.toString().trim()
        if (payload.isNotEmpty()) {
            val parsed = parseQrPayload(payload)
            if (parsed != null) {
                hostInput.setText(parsed.host)
                portInput.setText(parsed.port.toString())
                tokenInput.setText(parsed.token)
                return parsed
            }
        }
        val host = hostInput.text.toString().trim()
        val port = portInput.text.toString().trim().toIntOrNull() ?: return null
        val token = tokenInput.text.toString().trim()
        return ConnectionInfo(host, port, token)
    }

    private fun parseQrPayload(payload: String): ConnectionInfo? {
        return try {
            val json = JSONObject(payload)
            ConnectionInfo(
                json.getString("host"),
                json.getInt("port"),
                json.getString("token")
            )
        } catch (ex: Exception) {
            null
        }
    }

    private fun sendPost(info: ConnectionInfo, path: String, body: JSONObject?) {
        val url = "http://${info.host}:${info.port}$path"
        val mediaType = "application/json".toMediaType()
        val requestBody = body?.toString()?.toRequestBody(mediaType) ?: "".toRequestBody(mediaType)
        val request = Request.Builder()
            .url(url)
            .addHeader("X-Auth-Token", info.token)
            .post(requestBody)
            .build()
        Thread {
            client.newCall(request).execute().close()
        }.start()
    }
}

data class ConnectionInfo(val host: String, val port: Int, val token: String)
