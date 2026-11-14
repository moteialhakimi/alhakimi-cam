#!/usr/bin/env python3
"""Alhakimi Cam: consent-first, local camera preview for Termux."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import webbrowser

HOST = "127.0.0.1"  # Local-only; deliberately not reachable from other devices.
PORT = int(os.environ.get("ALHAKIMI_CAM_PORT", "8765"))

PAGE = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark">
<title>الحكيمي كام | Alhakimi Cam</title>
<style>
:root{color-scheme:dark;--bg:#08111f;--card:#111e31;--mint:#65f0c1;--muted:#a8b8cc;--pink:#ff829e}*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 10% 5%,#18304c 0,transparent 42%),var(--bg);color:#f4f8ff;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;display:grid;place-items:center;padding:22px}main{width:min(780px,100%);background:linear-gradient(145deg,#14243aee,#0c1728ee);border:1px solid #ffffff19;border-radius:26px;padding:clamp(20px,5vw,42px);box-shadow:0 25px 80px #0008}.badge{display:inline-flex;gap:8px;align-items:center;color:var(--mint);border:1px solid #65f0c144;border-radius:99px;padding:7px 12px;font-size:.86rem}.dot{width:8px;height:8px;border-radius:50%;background:var(--mint);box-shadow:0 0 14px var(--mint)}h1{font-size:clamp(2rem,7vw,3.8rem);line-height:1.05;margin:22px 0 10px;letter-spacing:-.04em}h1 span{color:var(--mint)}p{color:var(--muted);line-height:1.8}.consent{padding:16px;border:1px solid #65f0c144;background:#65f0c10d;border-radius:14px;line-height:1.75;color:#e3edf6}.consent strong{color:var(--mint)}.preview{margin:20px 0 16px;aspect-ratio:16/9;background:#050a12;border:1px solid #ffffff20;border-radius:18px;overflow:hidden;display:grid;place-items:center;position:relative}video{width:100%;height:100%;object-fit:cover;display:none;transform:scaleX(-1)}.placeholder{text-align:center;padding:24px;color:var(--muted)}.camera-icon{font-size:3rem;margin-bottom:8px}.status{position:absolute;top:14px;right:14px;background:#07101dcc;border:1px solid #ffffff24;border-radius:99px;padding:7px 11px;font-size:.8rem}.controls{display:flex;flex-wrap:wrap;gap:10px}.btn{border:0;border-radius:12px;padding:12px 18px;font:inherit;font-weight:700;cursor:pointer;transition:transform .15s,opacity .15s}.btn:hover:not(:disabled){transform:translateY(-2px)}.btn:disabled{opacity:.45;cursor:not-allowed}.start{background:var(--mint);color:#062018}.secondary{background:#ffffff13;color:#fff;border:1px solid #ffffff24}.message{min-height:1.5em;color:var(--pink);font-size:.92rem;margin:10px 0}.result{display:none;margin-top:18px;padding:16px;background:#ffffff08;border:1px solid #ffffff18;border-radius:16px}.result img{display:block;max-width:100%;max-height:420px;margin:12px auto;border-radius:10px}.foot{font-size:.78rem;color:#8092a8;margin-top:22px}.small{font-size:.88rem}.divider{height:1px;background:#ffffff16;margin:18px 0}
</style></head>
<body><main>
<div class="badge"><span class="dot"></span> تحكم واضح وبموافقتك</div>
<h1>الحكيمي <span>كام</span></h1>
<p>أداة معاينة والتقاط صورة من كاميرتك أنت. لا تبدأ الكاميرا إلا بعد ضغطك على الزر وموافقتك في المتصفح.</p>
<div class="consent"><strong>قبل البدء:</strong> ستظهر معاينة الكاميرا ��لى جهازك. لا يُطلب إذن الميكروفون، ولا يوجد تسجيل أو رفع تلقائي. إذا التقطت صورة، ستبقى هنا حتى تختار حفظها أو مشاركة ملفها بنفسك من قائمة المشاركة في جهازك.</div>
<section class="preview" aria-label="معاينة الكاميرا"><div class="status" id="status">متوقفة</div><div class="placeholder" id="placeholder"><div class="camera-icon">📷</div><div>معاينة الكاميرا ستظهر هنا</div></div><video id="video" autoplay playsinline muted></video></section>
<div class="controls"><button class="btn start" id="start">▶ أوافق — تشغيل الكاميرا</button><button class="btn secondary" id="capture" disabled>📸 التقاط صورة</button><button class="btn secondary" id="stop" disabled>■ إيقاف الكاميرا</button></div>
<div class="message" id="message" role="status" aria-live="polite"></div>
<section class="result" id="result"><strong>الصورة على جهازك فقط</strong><img id="photo" alt="معاينة الصورة التي التقطتها"><div class="controls"><a class="btn start" id="save" download="alhakimi-cam.jpg">حفظ الصورة</a><button class="btn secondary" id="share">مشاركة يدوية…</button></div><p class="small">لن تُرسل الصورة تلقائياً. اختيار تطبيق أو مستلم يتم بواسطتك من نافذة Android.</p></section>
<div class="divider"></div><p class="small">يمكنك إيقاف الكاميرا في أي وقت. إغلاق الصفحة يوقف المسار أيضاً. لا تستخدم الأداة لتصوير أي شخص دون علمه وموافقته.</p>
<div class="foot">Alhakimi Cam · محلي على Termux · دون حسابات أو كلمات مرور أو رفع بيانات</div>
</main><script>
const video=document.getElementById('video'), start=document.getElementById('start'), stop=document.getElementById('stop'), capture=document.getElementById('capture'), statusEl=document.getElementById('status'), placeholder=document.getElementById('placeholder'), message=document.getElementById('message'), result=document.getElementById('result'), photo=document.getElementById('photo'), save=document.getElementById('save'), share=document.getElementById('share');let stream=null,photoBlob=null,photoUrl=null;
async function startCamera(){message.textContent='';if(!navigator.mediaDevices?.getUserMedia){message.textContent='المتصفح لا يدعم الكاميرا. افتح الصفحة في متصفح حديث.';return;}try{stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false});video.srcObject=stream;video.style.display='block';placeholder.style.display='none';statusEl.textContent='● تعمل بإذنك';start.disabled=true;capture.disabled=false;stop.disabled=false;}catch(e){const errors={NotAllowedError:'لم يُمنح إذن الكاميرا. لن تعمل إلا بعد موافقتك من نافذة المتصفح.',NotFoundError:'لم يتم العثور على كاميرا متاحة.',NotReadableError:'الكاميرا مشغولة بتطبيق آخر أو غير متاحة حالياً.'};message.textContent=errors[e.name]||'تعذر تشغيل الكاميرا. تحقق من الإذن وحاول مرة أخرى.';}}
function stopCamera(){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;}video.srcObject=null;video.style.display='none';placeholder.style.display='block';statusEl.textContent='متوقفة';start.disabled=false;capture.disabled=true;stop.disabled=true;}
function takePhoto(){if(!stream||!video.videoWidth){message.textContent='انتظر ظهور المعاينة ثم حاول مرة أخرى.';return;}const canvas=document.createElement('canvas');canvas.width=video.videoWidth;canvas.height=video.videoHeight;canvas.getContext('2d').drawImage(video,0,0);canvas.toBlob(blob=>{if(!blob){message.textContent='تعذر إنشاء الصورة؛ حاول مرة أخرى.';return;}photoBlob=blob;if(photoUrl)URL.revokeObjectURL(photoUrl);photoUrl=URL.createObjectURL(blob);photo.src=photoUrl;save.href=photoUrl;result.style.display='block';message.textContent='تم التقاط الصورة محلياً. اختر الحفظ أو المشاركة بنفسك.';},'image/jpeg',.92);}
async function sharePhoto(){if(!photoBlob){message.textContent='التقط صورة أولاً.';return;}const file=new File([photoBlob],'alhakimi-cam.jpg',{type:'image/jpeg'});if(navigator.canShare?.({files:[file]})&&navigator.share){try{await navigator.share({files:[file],title:'صورة من الحكيمي كام'});message.textContent='تم فتح قائمة المشاركة؛ اختر بنفسك التطبيق والمستلم.';}catch(e){if(e.name!=='AbortError')message.textContent='تعذرت المشاركة من المتصفح. استخدم زر حفظ الصورة ثم شاركها يدوياً.';}}else{message.textContent='المتصفح لا يدعم المشاركة المباشرة. احفظ الصورة ثم شاركها يدوياً.';}}
start.addEventListener('click',startCamera);stop.addEventListener('click',stopCamera);capture.addEventListener('click',takePhoto);share.addEventListener('click',sharePhoto);window.addEventListener('pagehide',()=>{stopCamera();if(photoUrl)URL.revokeObjectURL(photoUrl);});
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
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; media-src 'self' blob:; connect-src 'none'; img-src 'self' data: blob:")
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
│     معاينة والتقاط بموافقتك        │
╰────────────────────────────────────╯
""")
    print(f"الرابط المحلي: {url}")
    print("الكاميرا لا تعمل إلا بعد الموافقة. الصور لا تُرفع تلقائياً. Ctrl+C للإيقاف.\n")
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
