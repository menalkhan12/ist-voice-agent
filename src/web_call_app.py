"""
Web call UI for IST Voice Agent.
- Call button starts the call; AI greets by voice, user speaks, AI answers by voice (no text shown during call).
- Say "no more query" to end; then evaluation metrics are shown.

Run: uv run python src/web_call_app.py
- Same machine: http://localhost:5000
- Other devices on same WiFi: http://<this-PC-IP>:5000 (IP is printed at startup).
- Different WiFi/networks: use a tunnel (e.g. ngrok http 5000) then open the https URL ngrok gives.
"""
import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
import threading

from flask import Flask, jsonify, request, send_from_directory, url_for

# Import pipeline from CLI agent (same STT, LLM, TTS, log)
from cli_voice_agent import (
    CALL_LOG,
    CALL_LOG_PATH,
    GREETING_TEXT,
    IST_DOCS,
    LOG_AUDIO_DIR,
    apply_simple_vad,
    counselor_llm_response,
    is_meaningful_transcript,
    looks_like_phone_number,
    save_call_log,
    save_call_record,
    synthesize_with_tts,
    transcribe_audio,
    user_asked_to_end_call,
)
from ist_knowledge import get_data_dir_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_call_app")

# Startup checks: ensure deployment will work
if not os.getenv("GROQ_API_KEY"):
    logger.warning("GROQ_API_KEY is not set. Set it in Render dashboard (or .env.local) or voice and LLM will fail.")
if not IST_DOCS:
    logger.warning("No IST documents loaded. Ensure the 'data' folder is deployed with at least IST_FULL_WEBSITE_MANUAL.txt or other .txt files.")
else:
    logger.info("IST knowledge base ready: %d documents loaded. Agent will answer from KB.", len(IST_DOCS))

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB for audio upload

# session_id -> list of (transcript, reply) for conversation buffer
session_turns: dict[str, list[tuple[str, str]]] = {}
# session_id -> call start time (first turn)
session_start: dict[str, str] = {}
# session_id -> phone number (captured after escalation when user says their number)
session_phone: dict[str, str] = {}
# Lock so 4+ concurrent calls don't corrupt call log or double-write
_call_log_lock = threading.Lock()


def load_call_log() -> None:
    if CALL_LOG_PATH.exists():
        try:
            with open(CALL_LOG_PATH, encoding="utf-8") as f:
                log = json.load(f)
                CALL_LOG.clear()
                CALL_LOG.extend(log)
        except Exception:
            pass


@app.route("/")
def index():
    return send_from_directory(Path(__file__).resolve().parent, "web_call_index.html")


@app.route("/health")
def health():
    """Render and load balancers can hit this to confirm the app is up."""
    return jsonify({"status": "ok"})


@app.route("/api/debug")
def debug():
    """Check if knowledge base loaded (for Render: if docs_loaded=0, data folder may be missing)."""
    status = get_data_dir_status()
    return jsonify({
        "docs_loaded": len(IST_DOCS),
        "data_dir": status["data_dir"],
        "fee_structure_exists": status["fee_structure_exists"],
        "manual_exists": status["manual_exists"],
    })


@app.route("/audio/<path:filename>")
def serve_audio(filename):
    mimetype = "audio/mpeg" if filename.lower().endswith(".mp3") else "audio/wav"
    return send_from_directory(LOG_AUDIO_DIR, filename, mimetype=mimetype)


@app.route("/api/start_call", methods=["POST"])
def start_call():
    try:
        load_call_log()
        session_id = str(uuid.uuid4())
        session_turns[session_id] = []
        session_start[session_id] = datetime.now().isoformat()
        logger.info("New call started, session %s (total active: %d)", session_id[:8], len(session_turns))
        # Generate greeting audio (session_id in filename so 2+ devices can call at once without overwriting)
        path = synthesize_with_tts(GREETING_TEXT, language="english", session_id=session_id)
        if not path:
            return jsonify({"error": "TTS failed. Check console for details. On Windows ensure edge-tts or pyttsx3 works."}), 500
        filename = os.path.basename(path)
        return jsonify({
            "session_id": session_id,
            "greeting_url": url_for("serve_audio", filename=filename),
        })
    except Exception as e:
        logger.exception("start_call error: %s", e)
        return jsonify({"error": "Server error: " + str(e)}), 500


@app.route("/api/query", methods=["POST"])
def query():
    try:
        load_call_log()
        session_id = request.form.get("session_id")
        if not session_id or session_id not in session_turns:
            return jsonify({"error": "Invalid session. Start a new call."}), 400
        # Each device has its own session_id; we only touch this session's data (safe for 2+ devices at once)
        logger.info("Query from session %s (active sessions: %d)", session_id[:8], len(session_turns))
        file = request.files.get("audio")
        if not file or not file.filename:
            return jsonify({"error": "No audio received. Allow microphone and try again."}), 400

        # Save uploaded audio (browser may send webm; we need wav for Groq - try saving as-is and hope backend accepts, or convert)
        ext = Path(file.filename or "audio").suffix or ".wav"
        if ext.lower() not in (".wav", ".webm", ".ogg", ".mp3", ".mp4", ".m4a"):
            ext = ".webm"
        ts = int(time.time() * 1000)
        # Include session_id so 4 concurrent calls don't overwrite each other's uploads
        safe_sid = (session_id or "").replace("/", "_")[:36]
        upload_path = LOG_AUDIO_DIR / f"web_mic_{safe_sid}_{ts}{ext}"
        file.save(upload_path)

        # Convert to wav for Groq and VAD (browser often sends webm). Groq accepts webm too, so if conversion fails we still try with the original file.
        wav_path = LOG_AUDIO_DIR / f"web_mic_{safe_sid}_{ts}.wav"
        audio_path = str(upload_path)
        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(str(upload_path))
            seg.export(str(wav_path), format="wav")
            audio_path = str(wav_path)
        except Exception as e1:
            logger.warning("pydub convert failed: %s", e1)
            try:
                import soundfile as sf
                data, sr = sf.read(str(upload_path))
                sf.write(str(wav_path), data, sr)
                audio_path = str(wav_path)
            except Exception as e2:
                logger.warning("soundfile convert failed: %s", e2)
                # Groq Whisper accepts webm/mp4/m4a/etc. Use original file; VAD will skip (returns path unchanged if it can't read).
                if upload_path.suffix.lower() in (".wav", ".mp3", ".webm", ".ogg", ".mp4", ".m4a"):
                    audio_path = str(upload_path)
                else:
                    return jsonify({
                        "reply_url": None,
                        "end_call": False,
                        "session_id": session_id,
                        "error": "Unsupported audio format. Use Chrome, Edge, or Firefox and allow microphone.",
                    }), 200

        t_stt_start = time.perf_counter()
        vad_path = apply_simple_vad(audio_path)
        transcript = transcribe_audio(vad_path, language="english")
        t_stt_end = time.perf_counter()
        stt_latency_s = t_stt_end - t_stt_start

        if not transcript:
            return jsonify({
                "reply_url": None,
                "end_call": False,
                "session_id": session_id,
                "error": "Could not understand audio. Check GROQ_API_KEY in .env.local and internet.",
            })
        if not is_meaningful_transcript(transcript):
            return jsonify({
                "reply_url": None,
                "end_call": False,
                "session_id": session_id,
                "error": "Could not understand audio",
            })

        call_turns = session_turns[session_id]
        # If previous turn was escalation (asked for phone), capture phone from this message
        if call_turns and looks_like_phone_number(transcript):
            last_reply = call_turns[-1][1].lower()
            if "we will forward" in last_reply and "phone" in last_reply:
                session_phone[session_id] = transcript.strip()

        t_llm_start = time.perf_counter()
        reply = counselor_llm_response(transcript, recent_turns=call_turns, language="english")
        t_llm_end = time.perf_counter()
        llm_latency_s = t_llm_end - t_llm_start
        escalated = "we will forward" in reply.lower() or "phone number" in reply.lower()
        call_turns.append((transcript, reply))
        t_tts_start = time.perf_counter()
        reply_path = synthesize_with_tts(reply, language="english", session_id=session_id)
        t_tts_end = time.perf_counter()
        tts_latency_s = t_tts_end - t_tts_start if reply_path else 0.0
        e2e_s = t_tts_end - t_stt_start
        call_end_iso = datetime.now().isoformat()

        # Use session start time for first turn, else previous entry's call_start
        call_start_iso = session_start.get(session_id) or call_end_iso
        for e in reversed(CALL_LOG):
            if e.get("session_id") == session_id:
                call_start_iso = e["call_start"]
                break

        entry = {
            "call_start": call_start_iso,
            "call_end": call_end_iso,
            "stt_latency_s": round(stt_latency_s, 3),
            "llm_latency_s": round(llm_latency_s, 3),
            "tts_latency_s": round(tts_latency_s, 3),
            "e2e_s": round(e2e_s, 3),
            "transcript": transcript,
            "escalated": escalated,
            "session_id": session_id,
        }
        with _call_log_lock:
            load_call_log()
            CALL_LOG.append(entry)
            save_call_log()

        reply_url = None
        if reply_path:
            reply_url = url_for("serve_audio", filename=os.path.basename(reply_path))
        else:
            logger.warning("TTS returned no path for reply")
        end_call = user_asked_to_end_call(transcript)
        if end_call:
            turns = session_turns.get(session_id, [])
            start_time = session_start.get(session_id) or call_end_iso
            session_entries = [e for e in CALL_LOG if e.get("session_id") == session_id]
            any_escalated = any(e.get("escalated") for e in session_entries)
            phone = session_phone.pop(session_id, None)
            save_call_record(
                session_id, start_time, datetime.now().isoformat(),
                turns, any_escalated, phone,
            )
            session_turns.pop(session_id, None)
            session_start.pop(session_id, None)

        return jsonify({
            "reply_url": reply_url,
            "end_call": end_call,
            "session_id": session_id,
        })
    except Exception as e:
        logger.exception("query error: %s", e)
        return jsonify({"error": "Server error: " + str(e), "reply_url": None, "end_call": False}), 500


@app.route("/api/metrics")
def metrics():
    load_call_log()
    session_id = request.args.get("session_id")
    entries = [e for e in CALL_LOG if e.get("session_id") == session_id] if session_id else []
    if not entries and CALL_LOG:
        # Use last completed call (last session_id that appears in log)
        last = CALL_LOG[-1]
        sid = last.get("session_id")
        if sid:
            entries = [e for e in CALL_LOG if e.get("session_id") == sid]
        if not entries:
            entries = CALL_LOG[-10:]

    n = len(entries)
    if n == 0:
        return jsonify({
            "last_call": None,
            "overall": _overall_metrics(),
        })

    avg_stt = sum(e["stt_latency_s"] for e in entries) / n
    avg_llm = sum(e["llm_latency_s"] for e in entries) / n
    avg_tts = sum(e["tts_latency_s"] for e in entries) / n
    avg_e2e = sum(e["e2e_s"] for e in entries) / n
    last_call = {
        "call_start": entries[0]["call_start"],
        "call_end": entries[-1]["call_end"],
        "turns": n,
        "avg_stt_s": round(avg_stt, 3),
        "avg_llm_s": round(avg_llm, 3),
        "avg_tts_s": round(avg_tts, 3),
        "avg_e2e_s": round(avg_e2e, 3),
    }
    return jsonify({
        "last_call": last_call,
        "overall": _overall_metrics(),
    })


def _overall_metrics():
    if not CALL_LOG:
        return {"total_calls": 0, "avg_stt_s": 0, "avg_llm_s": 0, "avg_tts_s": 0, "avg_e2e_s": 0}
    recent = CALL_LOG[-20:]
    n = len(recent)
    return {
        "total_calls": n,
        "avg_stt_s": round(sum(e["stt_latency_s"] for e in recent) / n, 3),
        "avg_llm_s": round(sum(e["llm_latency_s"] for e in recent) / n, 3),
        "avg_tts_s": round(sum(e["tts_latency_s"] for e in recent) / n, 3),
        "avg_e2e_s": round(sum(e["e2e_s"] for e in recent) / n, 3),
    }


def _get_local_ips():
    """Get this machine's local IPs so other devices on the same network can connect."""
    import socket
    out = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("8.8.8.8", 80))
        out.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if not ip.startswith("127."):
                out.append(ip)
    except Exception:
        pass
    return list(dict.fromkeys(out))  # unique, order preserved


if __name__ == "__main__":
    load_call_log()
    port = 5000
    print("\n" + "=" * 60)
    print("IST Voice Agent — Web Call")
    print("=" * 60)
    print("On this machine open:  http://localhost:5000")
    for ip in _get_local_ips():
        print("On other devices (same WiFi):  http://%s:%s" % (ip, port))
    print("=" * 60)
    print("Make sure Windows Firewall allows Python on port %s if needed.\n" % port)
    app.run(host="0.0.0.0", port=port, debug=False)
