#!/usr/bin/env python3
"""Full-page screenshot via CDP on existing tab. Usage: shot.py <url> <out.png> [width] [height]
Opens/attaches a tab, scrolls to trigger reveals, captures full-page."""
import json, urllib.request, time, base64, sys
import websocket

CDP = "http://127.0.0.1:9222"

def http_json(path):
    with urllib.request.urlopen(CDP + path, timeout=5) as r:
        return json.loads(r.read())

def http_json2(path):
    req = urllib.request.Request(CDP + path, method="PUT")
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read())

def ws_send(ws, method, params=None):
    ws.send(json.dumps({"id": 1, "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == 1:
            return msg

url = sys.argv[1]
out = sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1440

# Close any existing tabs already pointing at this url (stale renders)
for t in http_json("/json"):
    if t.get("type") == "page" and t.get("url", "").startswith(url.split("?")[0]):
        try:
            urllib.request.urlopen(urllib.request.Request(CDP + "/json/close/" + t["id"], method="PUT"), timeout=3)
        except Exception:
            pass
time.sleep(0.5)

# Create fresh tab with cache-buster to avoid stale render
import time as _t
buster = "?cb=%d" % int(_t.time())
full = url + buster
tab = http_json2("/json/new?" + full.replace(":", "%3A").replace("/", "%2F").replace("?", "%3F").replace("=", "%3D").replace("&", "%26"))
time.sleep(1.6)

ws = websocket.create_connection(tab["webSocketDebuggerUrl"], timeout=60, origin="*")
ws_send(ws, "Page.enable")
ws_send(ws, "Runtime.enable")
ws_send(ws, "Emulation.setDeviceMetricsOverride", {"width": width, "height": 900, "deviceScaleFactor": 2, "mobile": False})
time.sleep(1.5)

# Force trigger all reveal animations: scroll through whole doc
js = """(async () => {
  const delay = ms => new Promise(r => setTimeout(r, ms));
  const doc = document.documentElement;
  const step = Math.max(400, Math.floor(window.innerHeight * 0.7));
  let y = 0;
  while (y < doc.scrollHeight) {
    window.scrollTo(0, y);
    await delay(90);
    y += step;
  }
  window.scrollTo(0, 0);
  await delay(500);
  // Also call any manual reveal reset just in case
  if (window.__forceReveal) window.__forceReveal();
  return { h: doc.scrollHeight };
})()"""
ws_send(ws, "Runtime.evaluate", {"expression": js, "awaitPromise": True, "returnByValue": True})
time.sleep(0.8)

# Emulate full page height for capture
ws_send(ws, "Emulation.setDeviceMetricsOverride", {"width": width, "height": 14000, "deviceScaleFactor": 2, "mobile": False})
time.sleep(0.6)
res = ws_send(ws, "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True, "fromSurface": True})
data = res["result"]["data"]
raw = base64.b64decode(data)
with open(out, "wb") as f:
    f.write(raw)
ws.close()

# cleanup tab? leave it.
print(f"saved {out} ({len(raw)//1024} KB)")