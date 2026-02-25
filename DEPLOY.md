# One permanent URL (works on any device, any WiFi)

To get **one same URL** that you can share with anyone (your laptop, a friend’s laptop, different WiFi, any device):

1. **Deploy to Render (free)**  
   - Push this repo to **GitHub**.  
   - Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**.  
   - Connect your GitHub repo; Render will use `render.yaml`.  
   - In the service **Environment** tab, add: **GROQ_API_KEY** = your Groq API key.  
   - Deploy. You’ll get a URL like:  
     **`https://ist-voice-agent.onrender.com`**  
   - That URL stays the same every time and works for everyone. After code updates, push to `main` to redeploy (or use **Manual Deploy** in the dashboard).
   - Optional env: **PYTHON_VERSION** = `3.12.7`, **SKIP_VECTOR_INDEX** = `1` (see GITHUB_AND_DEPLOY.md if startup is slow).

2. **Optional: run locally with a temporary public URL**  
   - From project root: `uv run python src/run_web_with_tunnel.py`  
   - Use the printed ngrok URL from any device while the app is running.  
   - The URL changes each time you run the script. For a **fixed** URL, use step 1.

3. **Run locally on your laptop (test before deploy)**  
   - Open a terminal in the **project root** (`my-agent`), not inside `src`.  
   - Ensure **`.env.local`** exists with **`GROQ_API_KEY=your_key`** (get key from groq.com).  
   - Run: **`uv run python src/web_call_app.py`**  
   - In the browser open: **http://localhost:5000**  
   - Click **Call**, allow microphone when asked, wait for the greeting, then speak.  
   - If it doesn’t listen or respond, check the **terminal** for errors and the **on-page status** message (e.g. "TTS failed", "Could not understand audio", "Check GROQ_API_KEY").  
   - **Optional:** Install **ffmpeg** so the app can convert browser webm audio; without it, some browsers may still work with other formats.

---

## Call logs and escalated phone numbers

- **File (local):** **`logs/call_records.json`** (relative to project root).  
  Full path example: **`c:\Users\minal\Desktop\livekit-projects\my-agent\logs\call_records.json`**

- **Contents:** Each entry has `call_id`, `start_time`, `end_time`, `turns` (user/agent Q&A), `escalated` (true if forwarded to admin), and **`phone_number`** (filled only when escalated and user said their number).

- **On Render:** The same path is used, but the disk is ephemeral—logs are lost on restart/redeploy. For a permanent record you would need a database or external storage.
