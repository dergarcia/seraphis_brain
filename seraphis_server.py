# seraphis_server.py
# HTTP wrapper around seraphis_api.py so other apps can call /learn, /retrieve, /reason.
from flask import Flask, request, jsonify
import subprocess, sys, shlex, os, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
API  = HERE / "seraphis_api.py"
ART  = HERE / "artifacts"
ART.mkdir(exist_ok=True)

LOG_FILE = ART / "server.log"

def log(line: str) -> None:
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%fZ")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {line}\n")

def run_py(args: list[str], timeout_sec: int = 120) -> tuple[int, str, str]:
    env = os.environ.copy()
    # Ensure UTF-8 so Windows cp1252 never bites us
    env["PYTHONIOENCODING"] = "utf-8"
    cmd = [sys.executable, str(API), *args]
    log(f"RUN: {cmd}")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout_sec,
        )
        if proc.stdout:
            log(f"STDOUT: {proc.stdout.strip()[:2000]}")
        if proc.stderr:
            log(f"STDERR: {proc.stderr.strip()[:2000]}")
        log(f"RC: {proc.returncode}")
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as te:
        log(f"TIMEOUT after {timeout_sec}s: {cmd}")
        return 124, "", f"Timeout after {timeout_sec}s"
    except Exception as e:
        log(f"EXC: {e!r}")
        return 125, "", repr(e)

app = Flask(__name__)

@app.get("/ping")
def ping():
    return jsonify(ok=True)

@app.post("/learn")
def learn():
    data = request.get_json(force=True, silent=True) or {}
    query     = (data.get("query") or "").strip()
    category  = (data.get("category") or "system_planning").strip()
    score     = str(data.get("score", 8.5))
    chunk_id  = str(data.get("chunk_id", 2))
    if not query:
        return jsonify(error="query is required"), 400
    code, out, err = run_py(["learn",
                             "--query", query,
                             "--category", category,
                             "--score", score,
                             "--chunk-id", chunk_id])
    return jsonify(ok=(code == 0), stdout=out, stderr=err), (200 if code == 0 else 500)

@app.get("/retrieve")
def retrieve():
    q    = (request.args.get("query") or "").strip()
    topk = (request.args.get("top_k") or "5").strip()
    if not q:
        return jsonify(error="query is required"), 400
    code, out, err = run_py(["retrieve", "--query", q, "--top-k", topk])
    return jsonify(ok=(code == 0), stdout=out, stderr=err), (200 if code == 0 else 500)

@app.post("/reason")
def reason():
    code, out, err = run_py(["reason"])
    return jsonify(ok=(code == 0), stdout=out, stderr=err), (200 if code == 0 else 500)

if __name__ == "__main__":
    # Run on localhost:5057
    app.run(host="127.0.0.1", port=5057)
