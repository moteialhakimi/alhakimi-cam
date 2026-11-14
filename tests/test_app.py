from __future__ import annotations

from http.client import HTTPConnection
from pathlib import Path
import threading
import unittest

from alhakimi_cam import configured_port, create_server


class PortValidationTests(unittest.TestCase):
    def test_valid_port(self) -> None:
        self.assertEqual(configured_port("8765"), 8765)

    def test_rejects_non_numeric_and_out_of_range_ports(self) -> None:
        for value in ("abc", "0", "65536", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                configured_port(value)


class LocalHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = create_server(0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, path: str) -> tuple[int, dict[str, str], bytes]:
        connection = HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request("GET", path)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_homepage_serves_camera_consent_page(self) -> None:
        status, headers, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn("127.0.0.1", self.server.server_address[0])
        self.assertIn("text/html; charset=utf-8", headers["Content-Type"])
        self.assertIn("أوافق — تشغيل الكاميرا".encode(), body)
        self.assertIn(b"audio: false", body)
        self.assertIn("connect-src 'none'".encode(), headers["Content-Security-Policy"].encode())

    def test_unknown_paths_return_not_found(self) -> None:
        status, _headers, _body = self.request("/not-found")
        self.assertEqual(status, 404)

    def test_query_or_traversal_paths_are_not_served(self) -> None:
        for path in ("/../README.md", "/?anything=1"):
            with self.subTest(path=path):
                status, _headers, _body = self.request(path)
                self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
