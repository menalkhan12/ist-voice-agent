# IST Voice Agent — Deployment Guide

This document ensures the IST Admissions Voice Agent is deployment-ready and lists all query types it answers.

---

## Prerequisites (must be correct for 100% accuracy)

1. **GROQ_API_KEY**  
   - Required for speech-to-text (Whisper) and LLM (Llama).  
   - Get a key from [console.groq.com](https://console.groq.com).  
   - Set in Render: **Dashboard → your service → Environment** → add `GROQ_API_KEY` = your key.  
   - For local runs: put `GROQ_API_KEY=...` in `my-agent/.env.local`.

2. **Data folder**  
   - The repo must include the `data/` folder with at least one of:
     - `IST_FULL_WEBSITE_MANUAL.txt` (recommended — full IST reference)
     - Other `.txt` files: `MERIT_CRITERIA_AND_AGGREGATE.txt`, `FEE_STRUCTURE.txt`, `ADMISSION_FAQS_COMPLETE.txt`, `CLOSING_MERIT_HISTORY.txt`, etc.
   - If `99_MASTER_JSON.json` is missing, the agent still loads all `data/*.txt` files and works from the manual and FAQs.

3. **SKIP_VECTOR_INDEX** (optional, for Render free tier)  
   - Set to `1` in Render to skip ChromaDB/sentence-transformers and use keyword search only.  
   - Already set in `render.yaml`. Keeps startup fast and avoids OOM.

---

## Deploy to Render (recommended)

1. Push the repo to GitHub (include the `data/` folder and `src/`).
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service**.
3. Connect the GitHub repo. Render will use `render.yaml`:
   - **Build:** `pip install -e .`
   - **Start:** `cd src && gunicorn -w 1 -b 0.0.0.0:$PORT --timeout 120 web_call_app:app`
4. In the service **Environment** tab, add:
   - **GROQ_API_KEY** = (your Groq API key)  
   - **SKIP_VECTOR_INDEX** = `1` (optional; already in `render.yaml`).
5. Deploy. After success, your app is at:  
   **https://&lt;your-service-name&gt;.onrender.com**

### Enable automatic deployment on every push

- **Option A (Render built-in):** If you connected the repo in step 2, Render already deploys on every push to `main`. No extra setup.
- **Option B (GitHub Actions + Deploy Hook):** To trigger deploys from the Actions tab or have a visible deploy step:
  1. In Render: open your service → **Settings** → **Deploy Hook** → copy the URL.
  2. In GitHub: repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret** → name `RENDER_DEPLOY_HOOK_URL`, value = the Deploy Hook URL.
  3. Every push to `main` will run the **Deploy to Render** workflow and trigger a new deploy. You can also run it manually from **Actions** → **Deploy to Render** → **Run workflow**.

6. Open your app URL on any device (phone/laptop), allow microphone when prompted, tap **Call**, and speak your question.

---

## Deploy with Docker

From the repo root:

```bash
docker build -f Dockerfile.web -t ist-voice-agent .
docker run -p 8080:8080 -e GROQ_API_KEY=your_key -e SKIP_VECTOR_INDEX=1 ist-voice-agent
```

Then open **http://localhost:8080** (or your server’s host:8080).

---

## What the agent answers (query types)

The agent answers **only** from the loaded IST knowledge (website manual, FAQs, merit/fee docs). It does not repeat your question; it gives a short, direct answer. If the answer is not in the knowledge base, it escalates and asks for your phone number.

### 1. Programs and degrees
- What programs are offered at IST  
- BS / MS / PhD programs list  
- Aerospace, Electrical, Mechanical, Avionics, Materials, Computer Science, Software Engineering, AI, Data Science, Space Science, Mathematics, Physics, Biotechnology  
- Departments (Aeronautics, Avionics, Electrical, Materials, Mechanical, Space Science, Computing, Applied Math, Humanities)  
- KICSIT campus programs (BSCE, BSCS)

### 2. Fees and cost
- Fee structure, tuition, cost per semester  
- Fee for specific programs (e.g. Computer Engineering, Software Engineering — about 1 lakh 26 thousand per semester)  
- Hostel fee (e.g. Rs. 45,000–60,000 per semester excluding mess)  
- Application fee (e.g. about Rs. 3,000)  
- Installments, challan, refund policy

### 3. Merit and aggregate
- How merit is calculated (engineering: Matric 10% + FSC 40% + Entry Test 50%; non-engineering: Matric 50% + FSC 50%)  
- “Will I get admission?” — agent asks for Matric/FSC/Entry Test marks and computes aggregate  
- Estimated aggregate from your marks (engineering vs non-engineering)  
- Closing merit / last year merit / merit trend (from CLOSING_MERIT_HISTORY when available)  
- Will merit increase or decrease this year (trend from data; current year when merit list is out)  
- Merit list, cutoff, number of merit lists

### 4. Admissions process
- When admissions open (e.g. March/April for Fall)  
- Last date to apply (e.g. late June / early July)  
- How to apply (online only, IST Admission Portal — ugadmission.ist.edu.pk)  
- Application Reference Number (ARN), track application  
- Eligibility (FSc Pre-Engineering, ICS, DAE, A-Level with IBCC, Pre-Medical with maths course)  
- Entry test accepted: NAT (NTS), HAT, NET, ECAT, ETEA, SAT/ACT; minimum 33%; validity one year  
- Documents required (Matric, FSc, CNIC, domicile, photos, character certificate, migration)  
- Multiple programs in one application, change of major in first two semesters  
- Edit application after submit, supply in FSc, FSc Part-II pending, age limit  
- No interview for BS engineering

### 5. Transport, hostel, campus life
- Transport / buses (e.g. pick-and-drop routes; contact e.g. 03000544707)  
- Hostels (boys/girls, boarding, fee, mess, laundry)  
- Campus facilities (cafeteria, dining timings, Wi-Fi, sports, gym)  
- Laundry, attendant, health (MI Room, first aid, ambulance, fire safety)

### 6. Scholarships and financial aid
- Scholarships, financial assistance (from transport/hostel/FAQs and manual when available)

### 7. Research and institutes
- Research areas (aerospace, space science, materials, computing)  
- ICUBE-Q, lunar mission, Chang’e-6  
- Al Khwarizmi Institute, NCGSA, NCRS&GI, NCFA  
- Astronomy Resource Center, observatory, LISA consortium  
- Journal of Space Technology (JST), innovation, commercialization

### 8. General IST info
- About IST (established 2002, SUPARCO link, location — Islamabad Highway near DHA Phase-II)  
- Contact (e.g. +92-51-9075100, ist.edu.pk)  
- Visiting campus, harassment complaint cell  
- Accreditation (PEC, NCEAC, HEC)  
- Quality Enhancement Cell (QEC)  
- Student societies, Career Development Center, job fair  
- KICSIT campus (Kahuta, Rawalpindi–Kahuta Road, BSCE/BSCS, PEC/NCEAC)

### 9. Ending the call
- “No more query”, “end call”, “goodbye”, “that’s all”, “bye” (and similar) end the call and show metrics.

---

## Escalation (when the agent does not answer)

If the question is **not** in the knowledge base or needs human judgment, the agent says:

*“We will forward this query to our admissions team. Please tell me your phone number so we can call you back.”*

After that, if the user speaks a phone number, it is captured and stored in the call record.

---

## After deployment

- **Health check:** `GET https://<your-url>/health` → `{"status":"ok"}`.  
- **Logs:** On Render, check **Logs** for “Loaded N IST documents total” and any “GROQ_API_KEY is not set” / “No IST documents loaded” warnings.  
- **New content:** If you edit `IST_FULL_WEBSITE_MANUAL.txt` or other data files, redeploy (or restart the app) so the agent reloads the knowledge base.
