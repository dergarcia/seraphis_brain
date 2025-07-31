# seraphis_server.py
# Tiny HTTP wrapper around seraphis_api.py with logging to artifacts/server.log

from flask import Flask, request, jsonify
import subprocess, sys, shlex, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
API  = os.path.join(HERE, "seraphis_api.py")
LOG_DIR = os.path.join(HERE, "artifacts")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "server.log")

def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def run_py(args: list[str]) -> tuple[int,str,str]:
    proc = subprocess.run([sys.executable, API] + args,
                          capture_output=True, text=True)
    stdout, stderr = proc.stdout.strip(), proc.stderr.strip()
    log(f"RUN {' '.join(args)} | return={proc.returncode}")
    if stdout:
        log(f"STDOUT:\n{stdout}")
    if stderr:
        log(f"STDERR:\n{stderr}")
    return proc.returncode, stdout, stderr

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
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
    code,out,err = run_py(["learn","--query",query,"--category",category,"--score",score,"--chunk-id",chunk_id])
    return jsonify(ok=(code==0), stdout=out, stderr=err), (200 if code==0 else 500)

@app.get("/retrieve")
def retrieve():
    q = request.args.get("query","")
    topk = request.args.get("top_k","5")
    if not q:
        return jsonify(error="query is required"), 400
    code,out,err = run_py(["retrieve","--query",q,"--top-k",topk])
    return jsonify(ok=(code==0), stdout=out, stderr=err), (200 if code==0 else 500)

@app.post("/reason")
def reason():
    code,out,err = run_py(["reason"])
    return jsonify(ok=(code==0), stdout=out, stderr=err), (200 if code==0 else 500)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057)
