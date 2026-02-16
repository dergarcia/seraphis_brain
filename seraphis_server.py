from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import urllib.parse
import os
from datetime import datetime
import logging

PORT = 8000
ARTIFACTS_DIR = "artifacts"
LOG_FILE = os.path.join(ARTIFACTS_DIR, "server.log")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_request(handler, body=""):
    logging.info(f"{handler.command} {handler.path} from {handler.client_address[0]}")
    if body:
        logging.info(f"Payload: {body.strip()}")

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def _read_json(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length).decode("utf-8") if length else ""

    def do_GET(self):
        if self.path.startswith("/retrieve"):
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            query = query_params.get("query", [""])[0]
            top_k = query_params.get("top_k", ["5"])[0]

            log_request(self)

            try:
                result = subprocess.run(
                    ["python", "retrieve_relevant_memory.py", "--query", query, "--top_k", top_k],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                self._set_headers()
                self.wfile.write(result.stdout.encode())
            except Exception as e:
                self._set_headers(502)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                logging.error(f"Error: {e}")

    def do_POST(self):
        if self.path in ["/learn", "/reason"]:
            script = {
                "/learn": "auto_write_loop.py",
                "/reason": "reasoning_module.py"
            }[self.path]

            body = self._read_json()
            log_request(self, body)

            try:
                result = subprocess.run(
                    ["python", script],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                self._set_headers()
                self.wfile.write(result.stdout.encode())
            except Exception as e:
                self._set_headers(502)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                logging.error(f"Error: {e}")

if __name__ == "__main__":
    server = HTTPServer(("", PORT), SimpleHandler)
    print(f"Server running on port {PORT}")
    logging.info("=== Server Started ===")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        logging.info("=== Server Stopped ===")
