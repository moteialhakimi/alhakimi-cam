#!/usr/bin/env python3
"""Alhakimi Cam: local, consent-based camera preview for Termux."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import webbrowser

HOST = "127.0.0.1"  # Deliberately local-only; never expose the camera page to a network.
PORT = int(os.environ.get("ALHAKIMI_CAM_PORT", "8765"))

PAGE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>الحكيمي كام | Alhakimi Cam</title>
  <style>
    :root{color-scheme:dark;--bg:#08111f;--card:#111e31;--mint:#65f0c1;--muted:#a8b8cc;--pink:#ff7096}
    *{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 10% 5%,#18304c 0,transparent 42%),var(--bg);color:#f4f8ff;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;display:grid;place-items:center;padding:22px}
    main{width:min(760px,100%);background:linear-gradient(145deg,#14243aee,#0c1728ee);border:1px solid #ffffff19;border-radius:26px;padding:clamp(20px,5vw,42px);box-shadow:0 25px 80px #0008}
    .badge{display:inline-flex;gap:8px;align-items:center;color:var(--mint);border:1px solid #65f0c144;border-radius:99px;padding:7px 12px;font-size:.86rem}.dot{width:8px;height:8px;border-radius:50%;background:var(--mint);box-shadow:0 0 14px var(--mint)}
    h1{font-size:clamp(2rem,7vw,3.8rem);line-height:1.05;margin:22px 0 10px;letter-spacing:-.04em}h1 span{color:var(--mint)}p{color:var(--muted);line-height:1.8}
    .preview{margin:24px 0 18px;aspect-ratio:16/9;background:#050a12;border:1px solid #ffffff20;border-radius:18px;overflow:hidden;display:grid;place-items:center;position:relative}video{width:100%;height:100%;object-fit:cover;display:none;transform:scaleX(-1)}.placeholder{text-align:center;padding:24px;color:var(--muted)}.camera-icon{font-size:3rem;margin-bottom:8px}.status{position:absolute;top:14px;right:14px;background:#07101dcc;border:1px solid #ffffff24;border-radius:99px;padding:7px 11px;font-size:.8rem}
    .controls{display:flex;flex-wrap:wrap;gap:10px}.btn{border:0;border-radius:12px;padding:12px 18px;font:inherit;font-weight:700;cursor:pointer;transition:transform .15s,opacity .15s}.btn:hover{transform:translateY(-2px)}.start{background:var(--mint);color:#062018}.stop{background:#ffffff13;color:#fff;border:1px solid #ffffff24}.stop:disabled{opacity:.45;cursor:not-allowed;transform:none}.notice{margin-top:22px;padding:14px 16px;border-radius:12px;background:#65f0c10d;border:1px solid #65f0c128;color:#d4e5ef;font-size:.92rem}.notice strong{color:var(--mint)}#message{min-height:1.5em;color:var(--pink);font-size:.92rem;margin:10px 0 0}.foot{font-size:.78rem;color:#8092a8;margin-top:22px}
  </style>
</head>
<body><main>
  <div class="badge"><span class="dot"></span> معاينة محلية بموافقتك</div>
  <h1>الحكيمي <span>كام</span></h1>
  <p>اختبر كاميرا جهازك مباشرةً في هذا المتصفح. اضغط «تشغيل المعاينة» ثم وافق على طلب المتصفح إذا رغبت. لا يوجد تسجيل أو تصوير أو رفع للبيانات.</p>
  <section class="preview" aria-label="معاينة الكاميرا"><div class="status" id="status">متوقفة</div><div class="placeholder" id="placeholder"><div class="camera-icon">📷</div><div>معاينة الكاميرا ستظهر هنا</div></div><video id="video" autoplay playsinline muted></video></section>
  <div class="controls"><button class="btn start" id="start">▶ تشغيل المعاينة</button><button class="btn stop" id="stop" disabled>■ إيقاف</button></div>
  <div id="message" role="status" aria-live="polite"></div>
  <div class="notice"><strong>خصوصيتك أولاً:</strong> الصفحة تعمل على جهازك فقط، ولا تحفظ الصور أو الفيديو ولا ترسلهما إلى أي مكان. يمكنك إيقاف الكاميرا في أي وقت.</div>
  <div class="foot">Alhakimi Cam · يعمل محلياً على Termux · لا حسابات ولا كلمات مرور</div>
</main>
<script>
const video=document.getElementById('video'), start=document.getElementById('start'), stop=document.getElementById('stop'), statusEl=document.getElementById('status'), placeholder=document.getElementById('placeholder'), message=document.getElementById('message');
let stream=null;
async function startCamera(){message.textContent='';if(!navigator.mediaDevices?.getUserMedia){message.textContent='المتصفح لا يدعم الكاميرا هنا. افتح الرابط المحلي في متصفح حديث.';return;}try{stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false});video.srcObject=stream;video.style.display='block';placeholder.style.display='none';statusEl.textContent='● تعمل بإذنك';start.disabled=true;stop.disabled=false;}catch(e){const errors={NotAllowedError:'لم يُمنح إذن الكاميرا. يمكنك السماح من إعدادات الموقع ثم المحاولة مجدداً.',NotFoundError:'لم يتم العثور على كاميرا متاحة.',NotReadableError:'الكاميرا مشغولة بتطبيق آخر أو غير متاحة حالياً.'};message.textContent=errors[e.name]||'تعذر تشغيل الكاميرا. تحقق من الإذن وحاول مرة أخرى.';}}
function stopCamera(){if(stream){stream.getTracks().forEach(track=>track.stop());stream=null;}video.srcObject=null;video.style.display='none';placeholder.style.display='block';statusEl.textContent='متوقفة';start.disabled=false;stop.disabled=true;message.textContent='';}
start.addEventListener('click',startCamera);stop.addEventListener('click',stopCamera);window.addEventListener('pagehide',stopCamera);
</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; media-src 'self' blob:; connect-src 'none'; img-src 'self' data:")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[Alhakimi Cam] " + (fmt % args))


def main():
    try:
        server = HTTPServer((HOST, PORT), Handler)
    except OSError as exc:
        raise SystemExit(f"تعذر تشغيل الخادم على المنفذ {PORT}: {exc}\nجرّب: ALHAKIMI_CAM_PORT=8766 python alhakimi_cam.py")
    url = f"http://{HOST}:{PORT}/"
    print("""
╭────────────────────────────────────╮
│   📷  الحكيمي كام | ALHAKIMI CAM   │
│   معاينة كاميرا محلية بموافقتك     │
╰────────────────────────────────────╯
""")
    print(f"الرابط المحلي: {url}")
    print("لا يتم التسجيل أو رفع البيانات. أوقف الخادم بـ Ctrl+C.\n")
    try:
        if os.environ.get("TERMUX_VERSION") and os.system("command -v termux-open-url >/dev/null 2>&1") == 0:
            os.system(f"termux-open-url {url}")
        else:
            webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nإيقاف Alhakimi Cam...")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
