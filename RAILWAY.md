# Deploy IST Voice Agent on Railway (~2–4 min)

The repo has **no root Dockerfile** so Railway uses **Nixpacks + Procfile** (same app as Render).  
The LiveKit agent Dockerfile is at `Dockerfile.livekit-agent` if you need it later. **Render is unchanged** (it uses render.yaml only).

**If Railway still uses Docker:** In your service → **Settings** → **Build** → set **Dockerfile path** to empty, or set it to `Dockerfile.web` to use the web-app-only image.

## 1. Create project

1. Go to **https://railway.app** → sign in with **GitHub**.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select **menalkhan12/ist-voice-agent** (or your fork). Branch: **main**.

## 2. Build & start (set in Settings if not auto-detected)

In the service → **Settings** → **Deploy**:

| Setting | Value |
|--------|--------|
| **Build Command** | `pip install -e .` |
| **Start Command** | `cd src && gunicorn -w 1 --threads 6 -b 0.0.0.0:$PORT --timeout 120 web_call_app:app` |
| **Root Directory** | *(leave empty)* |

The repo includes a **Procfile**; Railway may use it automatically.

## 3. Environment variables

In the service → **Variables** → **Add Variable**:

| Name | Value |
|------|--------|
| `GROQ_API_KEY` | Your Groq API key |
| `SKIP_VECTOR_INDEX` | `1` |

## 4. Public URL

1. Go to **Settings** → **Networking** → **Generate Domain**.
2. You get a URL like `ist-voice-agent-production-xxxx.up.railway.app`.
3. Use this URL for the demo (HTTPS).

## Quick copy-paste

**Build command:**
```
pip install -e .
```

**Start command:**
```
cd src && gunicorn -w 1 --threads 6 -b 0.0.0.0:$PORT --timeout 120 web_call_app:app
```

---

After deploy (2–4 min), open the URL → tap **Call** → allow mic → ask e.g. "What programs does IST offer?"
