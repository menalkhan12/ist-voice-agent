# IST Calling Agent — Demo Checklist

Use this **right before your demo** so everything works.

---

## 1. Render dashboard

- [ ] **GROQ_API_KEY** is set: Render → your service → **Environment** → `GROQ_API_KEY` = (your Groq API key).
- [ ] Last deploy succeeded: **Events** or **Logs** show no errors.
- [ ] **Health check**: Open `https://<your-app>.onrender.com/health` in a browser. You should see `{"status":"ok"}`.

---

## 2. Avoid cold start (important on free tier)

- [ ] **5–10 minutes before the demo**: Open your app URL in a browser and tap **Call** once. Let the greeting play, then say "no more query" to end. This wakes the server.
- [ ] Right before presenting: Reload the page and do the real demo. The first request after long idle can take 30–60 seconds on free tier; a recent request avoids that.

---

## 3. Device and browser

- [ ] **Chrome or Edge** (best support for mic and playback). Safari on iPhone can block mic until you allow it.
- [ ] **Microphone**: When you tap **Call**, choose **Allow** when the browser asks for microphone.
- [ ] **Volume**: Device volume up so you hear the greeting and replies.
- [ ] **HTTPS**: Use the full Render URL (e.g. `https://ist-voice-agent.onrender.com`). Mic often does not work on `http://`.

---

## 4. During the demo

- [ ] Tap **Call** → allow mic → wait for greeting.
- [ ] Speak clearly: e.g. "What programs does IST offer?", "What is the fee for computer science?", "When do admissions open?"
- [ ] After each reply, wait for **"Listening… Speak now."** then ask the next question.
- [ ] To **end**: Say **"no more query"** (or "that's all", "goodbye"). Metrics will show.

---

## 5. If something fails

| Problem | What to do |
|--------|------------|
| Greeting doesn't play | Check volume; allow sound for the site. Reload and try again. |
| "Mic blocked" | Allow microphone for this site (address bar → lock → Site settings → Microphone → Allow), then reload. |
| "Could not understand audio" | Speak again, a bit louder and clearer. Check GROQ_API_KEY in Render. |
| First tap very slow | Normal on free tier after idle. Do a test call 5–10 min before demo (see step 2). |
| "TTS failed" / no voice reply | Server may be under load. Try again in a few seconds. |

---

## Summary

- **Backend**: GROQ_API_KEY set, health returns OK, data folder is in the repo (IST knowledge loads).
- **Frontend**: Simple screen with "IST Calling Agent" and Call button; voice-only flow.
- **Reliability**: Wake the app with a test call before the demo; use Chrome/Edge and allow mic + sound.

If all checkboxes above are done, the demo is as reliable as we can make it.
