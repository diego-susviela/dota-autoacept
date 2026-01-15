package com.example.dotaautoaccept

import android.Manifest
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Switch
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.json.JSONObject

class MainActivity : AppCompatActivity() {
    private val httpClient = OkHttpClient()
    private lateinit var ipField: EditText
    private lateinit var portField: EditText
    private lateinit var tokenField: EditText
    private lateinit var autoAcceptSwitch: Switch
    private lateinit var statusView: TextView

    private val notificationPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { }

    private val statusReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val payload = intent?.getStringExtra("payload") ?: return
            handleMessage(payload)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        ipField = findViewById(R.id.ipField)
        portField = findViewById(R.id.portField)
        tokenField = findViewById(R.id.tokenField)
        autoAcceptSwitch = findViewById(R.id.autoAcceptSwitch)
        statusView = findViewById(R.id.statusView)

        val connectButton = findViewById<Button>(R.id.connectButton)
        val startQueueButton = findViewById<Button>(R.id.startQueueButton)
        val stopQueueButton = findViewById<Button>(R.id.stopQueueButton)
        val loadQrButton = findViewById<Button>(R.id.loadQrButton)
        val qrPayloadField = findViewById<EditText>(R.id.qrPayloadField)

        loadSettings()
        requestNotificationPermission()

        connectButton.setOnClickListener {
            saveSettings()
            startQueueService()
        }

        loadQrButton.setOnClickListener {
            parseQrPayload(qrPayloadField.text.toString())
        }

        autoAcceptSwitch.setOnCheckedChangeListener { _, isChecked ->
            toggleAutoAccept(isChecked)
        }

        startQueueButton.setOnClickListener { sendCommand("/start-queue") }
        stopQueueButton.setOnClickListener { sendCommand("/stop-queue") }
    }

    override fun onStart() {
        super.onStart()
        registerReceiver(statusReceiver, IntentFilter("QUEUE_STATUS"))
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(statusReceiver)
    }

    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED
            ) {
                notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    private fun encryptedPrefs() = EncryptedSharedPreferences.create(
        this,
        "settings",
        MasterKey.Builder(this).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    private fun loadSettings() {
        val prefs = encryptedPrefs()
        ipField.setText(prefs.getString("ip", ""))
        portField.setText(prefs.getString("port", "8765"))
        tokenField.setText(prefs.getString("token", ""))
    }

    private fun saveSettings() {
        val prefs = encryptedPrefs()
        prefs.edit()
            .putString("ip", ipField.text.toString())
            .putString("port", portField.text.toString())
            .putString("token", tokenField.text.toString())
            .apply()
    }

    private fun parseQrPayload(payload: String) {
        try {
            val json = JSONObject(payload)
            ipField.setText(json.optString("host", ""))
            portField.setText(json.optString("port", "8765"))
            tokenField.setText(json.optString("token", ""))
        } catch (_: Exception) {
            statusView.text = "Status: invalid QR payload"
        }
    }

    private fun startQueueService() {
        val intent = Intent(this, QueueService::class.java)
        intent.putExtra("host", ipField.text.toString())
        intent.putExtra("port", portField.text.toString())
        intent.putExtra("token", tokenField.text.toString())
        ContextCompat.startForegroundService(this, intent)
        statusView.text = "Status: connecting"
    }

    private fun toggleAutoAccept(enabled: Boolean) {
        val payload = JSONObject().put("enabled", enabled).toString()
        postJson("/toggle-auto-accept", payload)
    }

    private fun sendCommand(path: String) {
        postJson(path, "{}")
    }

    private fun postJson(path: String, json: String) {
        val url = "http://${ipField.text}:${portField.text}$path"
        val request = Request.Builder()
            .url(url)
            .addHeader("X-Auth-Token", tokenField.text.toString())
            .post(json.toRequestBody("application/json".toMediaType()))
            .build()
        httpClient.newCall(request).enqueue(object : okhttp3.Callback {
            override fun onFailure(call: okhttp3.Call, e: java.io.IOException) {
                runOnUiThread { statusView.text = "Status: request failed" }
            }

            override fun onResponse(call: okhttp3.Call, response: Response) {
                response.close()
            }
        })
    }

    private fun handleMessage(text: String) {
        val json = JSONObject(text)
        val payload = json.optJSONObject("payload") ?: return
        val state = payload.optString("queue_state", "unknown")
        runOnUiThread { statusView.text = "Status: $state" }
    }
}
