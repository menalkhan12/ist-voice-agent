"""
Run the web call app and expose it with a public URL (any network).
Uses pyngrok to open a tunnel — no need to install ngrok separately; pyngrok downloads it.
Optional: Add NGROK_AUTH_TOKEN to .env.local (get free token at https://dashboard.ngrok.com/signup).
Run: uv run python src/run_web_with_tunnel.py
"""
import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env.local")

PORT = 5000


def run_flask():
    from web_call_app import app, load_call_log, _get_local_ips
    load_call_log()
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def main():
    print("\nStarting Flask on port %s..." % PORT)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)

    print("Opening public tunnel (pyngrok may download ngrok on first run)...")
    try:
        from pyngrok import ngrok
        token = os.environ.get("NGROK_AUTH_TOKEN")
        if token:
            ngrok.set_auth_token(token)
        tunnel = ngrok.connect(PORT, "http")
        public_url = tunnel.public_url
        print("\n" + "=" * 60)
        print("IST Voice Agent — Web Call (public URL)")
        print("=" * 60)
        print("Open from any device / any network:")
        print("  %s" % public_url)
        print("=" * 60)
        print("(This URL changes each run. For one permanent URL, see DEPLOY.md.)")
        print("Leave this window open. Press Ctrl+C to stop.\n")
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopped.")
    except Exception as e:
        print("Tunnel error: %s" % e)
        print("You can still use: http://localhost:%s" % PORT)
        print("Or add NGROK_AUTH_TOKEN to .env.local (free at https://dashboard.ngrok.com/signup)")
        flask_thread.join(timeout=1)


if __name__ == "__main__":
    main()
