# Voice Agent Terminal Commands

## 🚀 Quick Start

### 1. Improved Voice Agent (Terminal)
```bash
uv run python improved_voice_agent.py
```

### 2. Phone Call System (Auto-Answer)
```bash
uv run python phone_call_system.py
```

### 3. Quick Phone Setup
```bash
uv run python quick_phone_setup.py
```

### 4. Original CLI Voice Agent
```bash
uv run python src/cli_voice_agent.py
```

### 5. LiveKit Agent (Console Mode)
```bash
uv run python src/agent.py console
```

### 6. Interactive Menu Runner
```bash
uv run python run_voice_agent.py
```

## 🌐 Deploy (Render) – No "Application Loading" screen

To avoid the cold-start loading screen and run on **laptop, web, and phone (iOS/Android)** see **DEPLOY.md**. Short version: ping `https://<your-app>.onrender.com/health` every 5–10 min with [UptimeRobot](https://uptimerobot.com) or [cron-job.org](https://cron-job.org).

---

## 📊 Admin Dashboard (Node.js)

Requires **Node.js** installed. Run the React admin dashboard:

```bash
cd admin-dashboard
npm install
npm run dev
```

Then open **http://localhost:3000** in your browser.

- **Login:** `admin@ist.edu.pk` / `admin` (only @ist.edu.pk emails allowed)
- **Features:** Call logs, Reports & Analytics, Knowledge Base, Settings, User management

To **build for production:**
```bash
cd admin-dashboard
npm run build
```
Serves from `admin-dashboard/dist/`.

---

## 📞 Phone System Setup

### Auto-Answer Phone System:
```bash
uv run python phone_call_system.py
```

### Quick Phone Setup & Test:
```bash
uv run python quick_phone_setup.py
```

### Phone Configuration Guide:
See `sip_config_guide.md` for complete setup instructions

## 🔧 Diagnostics

### Run System Diagnostics:
```bash
uv run python diagnose_stt_tts.py
```

### Install Dependencies:
```bash
uv sync
```

## � Phone Call System Features

### Auto-Answer System:
- 📞 Automatically answers incoming calls
- 🤖 Professional IST voice agent responds
- �📊 Call logging and monitoring
- 🔄 Multiple concurrent call support
- 🎛️ SIP integration ready

### How Phone System Works:
1. **Incoming Call** → SIP provider receives call
2. **Route to LiveKit** → Provider forwards to your system
3. **Auto-Answer** → System automatically accepts call
4. **Voice Agent** → IST agent greets and assists
5. **Call Management** → System logs and monitors calls

## 📊 Features

### Improved Voice Agent Features:
- ✅ Continuous conversation until "end call"
- ✅ Enhanced STT accuracy with retry logic
- ✅ Better voice activity detection
- ✅ Improved TTS voice quality
- ✅ Comprehensive evaluation metrics
- ✅ Performance ratings (⭐ system)
- ✅ Detailed call logging
- ✅ Summary reports

### Phone System Features:
- ✅ Automatic call answering
- ✅ Professional phone etiquette
- ✅ Call monitoring and logging
- ✅ Multiple concurrent calls
- ✅ SIP provider integration
- ✅ Real-time call status

### Metrics Tracked:
- 🗣️ STT Latency (Speech-to-Text)
- 🧠 LLM Latency (Response Generation)
- 🔊 TTS Latency (Text-to-Speech)
- 🔄 End-to-End Round-trip Time
- 📊 Average Response Delay
- 🎯 STT Accuracy Score
- ✅ Success Rate
- 📞 Call Duration and Count

## 💡 Usage Tips

### For Phone System:
1. **Configure SIP provider** to route calls to LiveKit
2. **Set up phone number** with SIP trunk
3. **Run phone system** using commands above
4. **Monitor calls** in terminal output
5. **Test with real phone** to verify auto-answer

### During Phone Calls:
- 📞 Call is automatically answered
- 🤖 Agent greets professionally
- 🗣️ Speak clearly for best STT accuracy
- 📊 System logs all call metrics
- 🛑 Call ends when caller hangs up

### For Terminal Agent:
- 🎤 Speak clearly and at moderate pace
- 📝 Say "end call", "goodbye", or "that's all" to end call
- 📊 Agent handles multiple queries in one session
- 📈 Type 's' after calls for summary report

## 📁 Log Files

Metrics are saved to:
- `logs/metrics/call_metrics.json` - Detailed call data
- `logs/metrics/call_metrics_summary.csv` - Summary statistics
- `logs/audio/` - Audio recordings

## 🔍 Troubleshooting

### Phone System Issues:
1. **Check SIP configuration** in provider dashboard
2. **Verify LiveKit SIP settings**
3. **Check environment variables**
4. **Run quick setup** to verify configuration

### If STT is not working:
1. Check GROQ_API_KEY in .env.local
2. Run diagnostics: `uv run python diagnose_stt_tts.py`
3. Check internet connection

### If TTS is not working:
1. Check audio output device
2. Run diagnostics to test TTS voices
3. Check system audio settings

### If agent is slow:
1. Check internet connection speed
2. Monitor API response times in metrics
3. Consider reducing audio quality settings

## 📞 SIP Provider Setup

### Recommended Providers:
- **Twilio** - Easy setup, good documentation
- **Vonage** - Reliable, good pricing  
- **Plivo** - Simple API, affordable
- **Telnyx** - Advanced features

### Quick Setup Steps:
1. **Sign up** with SIP provider
2. **Get phone number** for your IST line
3. **Configure SIP trunk** to point to LiveKit
4. **Test with phone system** using commands above

See `sip_config_guide.md` for detailed setup instructions.
