# Accessing the Web Call from Other Laptops

## Same WiFi (same network)

1. On the **PC running the app**, start the server:
   ```bash
   cd my-agent
   uv run python src/web_call_app.py
   ```
2. In the terminal you’ll see something like:
   ```
   On this machine open:  http://localhost:5000
   On other devices (same WiFi):  http://192.168.1.100:5000
   ```
3. On **another laptop** connected to the **same WiFi**, open a browser and go to:
   ```
   http://192.168.1.100:5000
   ```
   (Use the IP your terminal printed, not necessarily 192.168.1.100.)

**If it doesn’t load from the other laptop:**

- **Windows:** Allow Python through the firewall for port 5000, or when the firewall prompt appears, click “Allow”.
- Or temporarily turn off the firewall to test, then re-enable and add a rule for port 5000.

---

## Different WiFi / different networks (e.g. home vs office)

`localhost` and your local IP only work on the **same network**. To use the app from a **different network** (any WiFi, any laptop), use the built-in tunnel — **no need to install ngrok manually**.

### One command (Python tunnel)

1. Install dependencies once (if you haven’t):
   ```bash
   cd my-agent
   uv sync
   ```
2. Run the app with a public tunnel:
   ```bash
   uv run python src/run_web_with_tunnel.py
   ```
3. On first run, pyngrok may download the tunnel binary (one-time).
4. The terminal will print a public URL, e.g. `https://abc123.ngrok-free.app`.
5. Open that URL on **any laptop** (any WiFi). The app works the same.

**Optional (recommended):** For a stable URL, get a free auth token from [ngrok signup](https://dashboard.ngrok.com/signup), then add to `my-agent/.env.local`:
```env
NGROK_AUTH_TOKEN=your_token_here
```

---

## Summary

| Situation              | What to do / open                    |
|------------------------|--------------------------------------|
| Same PC                | `uv run python src/web_call_app.py` → http://localhost:5000 |
| Other device, same WiFi| Same as above → http://\<this-PC-IP\>:5000 |
| Any network (any laptop)| `uv run python src/run_web_with_tunnel.py` → open the printed https URL |
