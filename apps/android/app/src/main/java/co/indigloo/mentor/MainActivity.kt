package co.indigloo.mentor

import android.app.ActivityManager
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.os.StatFs
import android.provider.OpenableColumns
import android.speech.tts.TextToSpeech
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.exifinterface.media.ExifInterface
import androidx.webkit.WebViewAssetLoader
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import com.google.mlkit.vision.text.devanagari.DevanagariTextRecognizerOptions
import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.Engine
import com.google.ai.edge.litertlm.EngineConfig
import com.google.ai.edge.litertlm.Message
import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.io.File
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

/** Local-only host. Remote pages and requests cannot reach the native bridge. */
class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener {
    private lateinit var web: WebView
    private lateinit var vault: Vault
    private var tts: TextToSpeech? = null
    private var speechReady = false
    private val worker = Executors.newSingleThreadExecutor()
    private val timer = Executors.newSingleThreadScheduledExecutor()
    private var engine: Engine? = null
    private var pending: Pair<String, String>? = null
    private var scanLang = "en"
    private val modelFile get() = File(filesDir, "mentor.litertlm")
    private val picker = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        val request = pending ?: return@registerForActivityResult
        pending = null
        if (uri == null) { reply(request.first, true, ""); return@registerForActivityResult }
        if (request.second == "scan") scan(request.first, uri) else importModel(request.first, uri)
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        vault = Vault(this)
        web = WebView(this)
        setContentView(web)
        ViewCompat.setOnApplyWindowInsetsListener(web) { v, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.ime())
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this)).build()
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = false
            allowContentAccess = false
            mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
            setSupportMultipleWindows(false)
            javaScriptCanOpenWindowsAutomatically = false
        }
        WebView.setWebContentsDebuggingEnabled(false)
        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? =
                loader.shouldInterceptRequest(request.url) ?: WebResourceResponse(
                    "text/plain", "UTF-8", 403, "Blocked", emptyMap(), ByteArrayInputStream(byteArrayOf()))
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                request.url.scheme != "https" || request.url.host != "appassets.androidplatform.net" ||
                    !request.url.path.orEmpty().startsWith("/assets/www/")
        }
        web.addJavascriptInterface(Bridge(), "MentorNative")
        web.loadUrl("https://appassets.androidplatform.net/assets/www/index.html")
        tts = TextToSpeech(this, this)
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() { if (web.canGoBack()) web.goBack() else finish() }
        })
    }
    override fun onInit(status: Int) { speechReady = status == TextToSpeech.SUCCESS }
    private fun reply(id: String, ok: Boolean, value: String) {
        runOnUiThread {
            if (!isDestroyed) web.evaluateJavascript(
                "window.mentorNativeResult(${JSONObject.quote(id)},$ok,${JSONObject.quote(value)});", null)
        }
    }
    private fun task(id: String, block: () -> String) {
        worker.execute {
            try { reply(id, true, block()) }
            catch (e: Exception) { reply(id, false, e.message ?: "Action failed") }
            catch (_: LinkageError) { reply(id, false, "This device cannot load the local AI runtime. Use guided lessons.") }
        }
    }
    inner class Bridge {
        @JavascriptInterface fun request(raw: String) {
            if (raw.length > 1_100_000) return
            try {
                val r = JSONObject(raw)
                val id = r.getString("id")
                if (!id.matches(Regex("[a-zA-Z0-9-]{1,64}"))) return
                val p = r.optJSONObject("payload") ?: JSONObject()
                when (r.getString("action")) {
                    "load" -> task(id) { vault.read() }
                    "save" -> task(id) { vault.write(p.getString("data")); "" }
                    "erase" -> task(id) {
                        engine?.close(); engine = null
                        modelFile.delete(); File(filesDir, "model.tmp").delete()
                        cacheDir.deleteRecursively(); vault.erase(); ""
                    }
                    "scan", "importModel" -> runOnUiThread {
                        if (pending != null) reply(id, false, "Finish selecting the current file first.")
                        else {
                            val action = r.getString("action")
                            pending = id to action
                            scanLang = if (p.optString("lang") == "hi") "hi" else "en"
                            try { picker.launch(if (action == "scan") arrayOf("image/*") else arrayOf("*/*")) }
                            catch (_: Exception) { pending = null; reply(id, false, "No document picker is available.") }
                        }
                    }
                    "loadModel" -> task(id) {
                        val memory = ActivityManager.MemoryInfo()
                        (getSystemService(ACTIVITY_SERVICE) as ActivityManager).getMemoryInfo(memory)
                        require(memory.totalMem >= 3L * 1024 * 1024 * 1024) { "This phone has limited memory. Use guided lessons." }
                        require(modelFile.exists()) { "Import a compatible Android CPU .litertlm model first." }
                        engine?.close(); engine = null
                        cacheDir.mkdirs()
                        val next = Engine(EngineConfig(modelPath = modelFile.absolutePath,
                            backend = Backend.CPU, maxNumTokens = 1024, cacheDir = cacheDir.absolutePath))
                        try { next.initialize(); engine = next }
                        catch (e: Exception) { next.close(); throw e }
                        "Local AI loaded. Answers run on this device."
                    }
                    "unloadModel" -> task(id) { engine?.close(); engine = null; "Guided tutor active. AI memory released." }
                    "generate" -> task(id) {
                        if (Build.VERSION.SDK_INT >= 29) require(
                            (getSystemService(POWER_SERVICE) as PowerManager).currentThermalStatus < PowerManager.THERMAL_STATUS_SEVERE
                        ) { "The phone is hot. Let it cool before using AI." }
                        val prompt = p.getString("prompt")
                        require(prompt.toByteArray().size <= 1800) { "Question exceeds the model prompt budget." }
                        val active = engine ?: error("Load a local model first.")
                        active.createConversation().use { conversation ->
                            val timeout = timer.schedule({ try { conversation.cancelProcess() } catch (_: Exception) {} }, 60, TimeUnit.SECONDS)
                            try { conversation.sendMessage(Message.of(prompt)).toString().take(6000) }
                            finally { timeout.cancel(false) }
                        }
                    }
                    "speak" -> runOnUiThread {
                        if (!speechReady) { reply(id, false, "Read-aloud is not ready."); return@runOnUiThread }
                        val lang = if (p.optString("lang") == "hi") "hi" else "en"
                        val voice = tts?.voices?.firstOrNull { !it.isNetworkConnectionRequired && it.locale.language == lang }
                        if (voice == null) { reply(id, false, "Install an offline $lang voice in Android text-to-speech settings."); return@runOnUiThread }
                        tts?.voice = voice
                        val result = tts?.speak(p.optString("text").take(8000), TextToSpeech.QUEUE_FLUSH, null, id)
                        reply(id, result == TextToSpeech.SUCCESS, if (result == TextToSpeech.SUCCESS) "" else "Read-aloud could not start.")
                    }
                    else -> reply(id, false, "Unsupported action")
                }
            } catch (_: Exception) { /* Malformed bridge request. */ }
        }
    }
    private fun importModel(id: String, uri: Uri) = task(id) {
        var name = ""
        var size = -1L
        contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE), null, null, null)?.use { c ->
            if (c.moveToFirst()) { name = c.getString(0).orEmpty(); if (!c.isNull(1)) size = c.getLong(1) }
        }
        require(name.endsWith(".litertlm", true)) { "Choose a .litertlm model file." }
        val limit = minOf(3L * 1024 * 1024 * 1024, StatFs(filesDir.absolutePath).availableBytes - 256L * 1024 * 1024)
        require(limit > 0 && (size < 0 || size <= limit)) { "Not enough free storage for this model." }
        engine?.close(); engine = null
        val temp = File(filesDir, "model.tmp")
        try {
            contentResolver.openInputStream(uri)?.use { input ->
                temp.outputStream().use { output ->
                    val buffer = ByteArray(65536)
                    var total = 0L
                    while (true) {
                        val n = input.read(buffer)
                        if (n < 0) break
                        total += n
                        require(total <= limit) { "Model is too large for available storage." }
                        output.write(buffer, 0, n)
                    }
                    require(total > 0) { "The selected model is empty." }
                }
            } ?: error("Cannot read selected file.")
            require(temp.renameTo(modelFile)) { "Could not save imported model." }
        } finally { temp.delete() }
        "Model imported. Tap Load imported model to start it."
    }
    private fun scan(id: String, uri: Uri) {
        val lang = scanLang
        worker.execute {
            try {
                val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
                contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds) }
                require(bounds.outWidth > 0 && bounds.outHeight > 0) { "Choose a readable image." }
                var sample = 1
                while (maxOf(bounds.outWidth, bounds.outHeight) / sample > 2048) sample *= 2
                val bitmap = contentResolver.openInputStream(uri)?.use {
                    BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply { inSampleSize = sample })
                } ?: error("Cannot decode image.")
                val rotation = contentResolver.openInputStream(uri)?.use {
                    try { ExifInterface(it).rotationDegrees } catch (_: Exception) { 0 }
                } ?: 0
                val recognizer = if (lang == "hi") TextRecognition.getClient(DevanagariTextRecognizerOptions.Builder().build())
                    else TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
                recognizer.process(InputImage.fromBitmap(bitmap, rotation))
                    .addOnSuccessListener { result ->
                        if (result.text.isBlank()) reply(id, false, "No readable text found. Try a sharper, well-lit photo.")
                        else reply(id, true, result.text.take(4000))
                    }
                    .addOnFailureListener { e -> reply(id, false, e.message ?: "Could not read the image.") }
                    .addOnCompleteListener { recognizer.close(); bitmap.recycle() }
            } catch (e: Exception) { reply(id, false, e.message ?: "Could not open photo.") }
        }
    }
    override fun onDestroy() {
        tts?.stop(); tts?.shutdown()
        web.removeJavascriptInterface("MentorNative"); web.destroy()
        worker.execute { engine?.close(); engine = null }
        worker.shutdown(); timer.shutdown()
        super.onDestroy()
    }
}
