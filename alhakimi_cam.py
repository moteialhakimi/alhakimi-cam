#!/usr/bin/env python3
"""الحكيمي كام: خادم محلي لمعاينة كاميرا المستخدم بموافقته."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
import shutil
import subprocess
import webbrowser

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
PAGE_PATH = Path(__file__).resolve().parent / "web" / "index.html"


def configured_port(value: str | None = None) -> int:
    """اقرأ منفذ التشغيل وتحقق من أنه منفذ TCP صالح غير صفري."""
    raw_value = os.environ.get("ALHAKIMI_CAM_PORT", str(DEFAULT_PORT)) if value is None else value
    try:
        port = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("قيمة المنفذ يجب أن تكون رقماً صحيحاً بين 1 و65535.") from exc
    if not 1 <= port <= 65535:
        raise ValueError("المنفذ يجب أن يكون بين 1 و65535.")
    return port


def make_handler(page_path: Path = PAGE_PATH) -> type[BaseHTTPRequestHandler]:
    """أنشئ معالجاً يخدم صفحة التطبيق فقط، دون تسجيل بيانات الطلبات."""
    class LocalCameraHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path not in ("/", "/index.html"):
                self.send_error(404, "المسار غير موجود")
                return
            try:
                body = page_path.read_bytes()
            except OSError:
                self.send_error(503, "تعذر تحميل صفحة التطبيق. تحقق من وجود web/index.html.")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                "img-src blob: data:; media-src blob:; connect-src 'none'; base-uri 'none'; form-action 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _format: str, *_args: object) -> None:
            # لا نسجل عناوين IP أو مسارات الطلب أو بيانات قد تكون حساسة.
            return

    return LocalCameraHandler


def create_server(port: int) -> HTTPServer:
    """أنشئ خادماً مربوطاً حصراً بالواجهة المحلية."""
    if not 0 <= port <= 65535:
        raise ValueError("المنفذ خارج النطاق المسموح.")
    return HTTPServer((HOST, port), make_handler())


def open_local_page(url: str) -> None:
    """حاول فتح رابط localhost في متصفح Termux، دون استخدام shell."""
    termux_opener = shutil.which("termux-open-url")
    if os.environ.get("TERMUX_VERSION") and termux_opener:
        try:
            subprocess.Popen([termux_opener, url], close_fds=True)
            return
        except OSError:
            pass
    try:
        webbrowser.open(url)
    except Exception:
        # يظل الخادم متاحاً؛ يمكن للمستخدم فتح الرابط يدوياً.
        pass


def main() -> None:
    try:
        port = configured_port()
        server = create_server(port)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"تعذر بدء الحكيمي كام: {exc}") from exc

    url = f"http://{HOST}:{port}/"
    print("""
╭────────────────────────────────────╮
│      📷 الحكيمي كام | ALHAKIMI CAM │
│       معاينة محلية بموافقتك         │
╰────────────────────────────────────╯
""")
    print(f"افتح هذا الرابط على الجهاز نفسه: {url}")
    print("لا يوجد تسجيل أو رفع للصور. أوقف الخادم باستخدام Ctrl+C.\n")
    open_local_page(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nإيقاف الحكيمي كام...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
