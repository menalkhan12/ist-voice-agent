# Easiest method: Put on GitHub → Deploy on Render (one permanent URL)

**Why not Vercel?**  
Vercel is for static sites and short serverless functions. This app is a **Flask server** with heavy Python (audio, ML, ChromaDB). Vercel has tight limits (e.g. 50MB, short timeouts) and isn’t meant for long-running Python backends. **Render** is free and built for this.

---

## Step 1: Put the project on GitHub

### 1.1 Initialize Git (if not already)

In PowerShell, from the project folder:

```powershell
cd c:\Users\minal\Desktop\livekit-projects\my-agent
git init
```

### 1.2 Add all files and commit

```powershell
git add .
git status
```

Check that **`.env.local`** does **not** appear (it’s in `.gitignore`). If it appears, do **not** add it — it contains your API keys.

```powershell
git commit -m "IST Voice Agent - web call app and deploy config"
```

### 1.3 Create a repo on GitHub and push

1. Open **https://github.com/new**
2. Repository name: e.g. **`ist-voice-agent`**
3. Choose **Public**. Do **not** add a README, .gitignore, or license (you already have them).
4. Click **Create repository**.

5. In PowerShell, run the commands GitHub shows (use your username and repo name):

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ist-voice-agent.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. If GitHub asks to log in, use the browser or a personal access token.

---

## Step 2: Deploy on Render (one permanent URL)

1. Go to **https://dashboard.render.com** and sign in (GitHub login is fine).

2. Click **New +** → **Web Service**.

3. Connect GitHub if asked, then select the repo **`ist-voice-agent`** (or whatever you named it).

4. **If Render shows "Go" or wrong settings**, set these manually:
   - **Language:** **Python** (not Go)
   - **Build Command:** `pip install -e .`
   - **Start Command:** `cd src && gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 web_call_app:app`
   - **Root Directory:** leave **empty**

5. **Important – set Python version** (so build doesn’t use 3.14):
   - Open **Environment** and add: **Key** `PYTHON_VERSION`, **Value** `3.12.7`
   - The repo also has a **`.python-version`** file (optional; Render reads this).

6. Add your API key in **Environment**:
   - **Key:** `GROQ_API_KEY`  
   - **Value:** your Groq API key (same as in `.env.local`).

7. Click **Create Web Service**. Render will build and deploy.

8. When it’s done, your **one permanent URL** will be something like:
   - **https://ist-voice-agent.onrender.com**

Share that link with anyone; it works on any device and any WiFi.

**Phone & laptop:** Use the **HTTPS** URL. On phone, allow microphone when prompted.

**Flow:** Greeting asks "Urdu or English?" → You say **Urdu** → Agent says *"Chalo Urdu mein bat karte hain. Apna sawal bataiye."* → You ask in Urdu → Agent replies in Urdu. Say **English** → Agent says *"Let's talk in English. Tell me what your query is."* → You ask → Agent answers in English. Recording stops when you **pause** (silence); say **"end call"** (or *khatam* / *bas*) to end the call.

---

## Final deployment checklist (one URL, phone + laptop)

| Step | Action |
|------|--------|
| 1 | Repo on GitHub, branch `main` |
| 2 | Render → Web Service → connect repo |
| 3 | **Build:** `pip install -e .` · **Start:** `cd src && gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 web_call_app:app` |
| 4 | **Environment:** `PYTHON_VERSION` = `3.12.7`, `SKIP_VECTOR_INDEX` = `1`, `GROQ_API_KEY` = your key |
| 5 | Deploy. Use the **HTTPS** URL on phone and laptop. |

---

## If the page never loads (stuck “loading” or same screen)

On free tier the app can crash at startup because it loads a heavy ML index. Add this so it starts quickly and uses keyword search only:

- In Render → your service → **Environment** → add **`SKIP_VECTOR_INDEX`** = **`1`**. Save, then **Manual Deploy**.

After deploy, the app should load within a minute. RAG still works using keyword search.

---

## If Render build still fails (Python version)

- In Render → your service → **Environment** → add **`PYTHON_VERSION`** = **`3.12.7`** (no spaces). Save and trigger **Manual Deploy**.
- **Alternative: use Docker on Render**  
  - New Web Service → connect same repo → set **Environment** to **Docker**.  
  - **Dockerfile path:** `Dockerfile.web`  
  - Add env var **GROQ_API_KEY**. Deploy. (Docker build uses Python 3.12.)

---

## Other free deploy option: Railway

1. Go to **https://railway.app** → Login with GitHub.
2. **New Project** → **Deploy from GitHub repo** → select **ist-voice-agent**.
3. Railway will detect the repo. Set **Root Directory** to blank. Under **Settings**, set **Dockerfile path** to **`Dockerfile.web`** (or leave auto; if it picks Python, add **Variable** `PYTHON_VERSION` = `3.12.7`).
4. Add variable **GROQ_API_KEY** = your key.
5. Deploy. You’ll get a URL like **https://ist-voice-agent-production.up.railway.app**.

(Railway gives a small free credit; after that it’s paid unless they have a free tier.)

---

## Summary

| Step | What to do |
|------|------------|
| 1 | `git init` → `git add .` → `git commit -m "..."` |
| 2 | Create a new repo on GitHub (no README/.gitignore) |
| 3 | `git remote add origin https://github.com/USER/REPO.git` → `git push -u origin main` |
| 4 | Render → New Web Service → connect repo → add `GROQ_API_KEY` → Deploy |
| 5 | Use the Render URL (e.g. `https://ist-voice-agent.onrender.com`) as your permanent link |

If you want, we can do the **git init, add, commit** and **remote** steps in your project next so you only need to create the repo on GitHub and push.

---

## Redeploy after code updates (Urdu/English, end call, etc.)

After you change the app (e.g. new phrases, TTS/STT), push to GitHub and Render will redeploy automatically:

```powershell
cd c:\Users\minal\Desktop\livekit-projects\my-agent
git add .
git commit -m "Updated Urdu/English phrases and end-call handling"
git push origin main
```

If auto-deploy is off, in Render go to your service → **Manual Deploy** → **Deploy latest commit**. Your URL (e.g. `https://ist-voice-agent.onrender.com`) stays the same.
