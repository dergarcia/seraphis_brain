# seraphis_server.py
# Tiny HTTP wrapper around seraphis_api.py so other apps can call /learn, /retrieve, /reason.
from flask import Flask, request, jsonify
import subprocess, sys, shlex, os

HERE = os.path.dirname(os.path.abspath(__file__))
API  = os.path.join(HERE, "seraphis_api.py")

# Keep external calls from hanging forever
SUBPROC_TIMEOUT = 25  # seconds; adjust as needed

def run_py(args: list[str]) -> tuple[int,str,str,str]:
    """Run seraphis_api.py with a hard timeout and return (code, stdout, stderr, summary)."""
    cmd = [sys.executable, API] + args
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SUBPROC_TIMEOUT,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        summary = f"exit={proc.returncode} len(out)={len(proc.stdout)} len(err)={len(proc.stderr)}"
        return proc.returncode, proc.stdout, proc.stderr, summary
    except subprocess.TimeoutExpired as te:
        # Best effort kill and report
        return 124, te.stdout or "", te.stderr or "", f"timeout after {SUBPROC_TIMEOUT}s"

app = Flask(__name__)

@app.get("/ping")
def ping():
    return jsonify(ok=True)

@app.post("/learn")
def learn():
    data = request.get_json(force=True, silent=True) or {}
    query     = data.get("query", "")
    category  = data.get("category", "system_planning")
    score     = str(data.get("score", 8.5))
    chunk_id  = str(data.get("chunk_id", 2))
    if not query:
        return jsonify(error="query is required"), 400
    code,out,err,summary = run_py(["learn","--query",query,"--category",category,"--score",score,"--chunk-id",chunk_id])
    return jsonify(ok=(code==0), summary=summary, stdout=out, stderr=err), (200 if code==0 else 500)

@app.get("/retrieve")
def retrieve():
    q = request.args.get("query","")
    topk = request.args.get("top_k","5")
    if not q:
        return jsonify(error="query is required"), 400
    code,out,err,summary = run_py(["retrieve","--query",q,"--top-k",topk])
    return jsonify(ok=(code==0), summary=summary, stdout=out, stderr=err), (200 if code==0 else 500)

@app.post("/reason")
def reason():
    code,out,err,summary = run_py(["reason"])
    return jsonify(ok=(code==0), summary=summary, stdout=out, stderr=err), (200 if code==0 else 500)

if __name__ == "__main__":
    # Run on localhost:5057
    app.run(host="127.0.0.1", port=5057)
