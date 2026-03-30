"""
================================================
  run.py  —  Reliable launcher
  Starts FastAPI on :8000 + Streamlit on :8501
  Usage:  python run.py
  Stop :  Ctrl+C
================================================
"""
import subprocess, time, sys, os, socket, threading

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── helpers ───────────────────────────────────────────────────────────────────
def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0

def kill_port(port):
    if os.name == "nt":
        subprocess.call(
            f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port}\') '
            f'do taskkill /F /PID %a',
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    else:
        subprocess.call(f"fuser -k {port}/tcp", shell=True,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

def pip_install(pkg):
    subprocess.call([sys.executable, "-m", "pip", "install", pkg, "-q"])

# ── pre-flight checks ─────────────────────────────────────────────────────────
def preflight():
    print("\n── Pre-flight checks ────────────────────────────────────")

    # Ensure uvicorn is installed
    try:
        import uvicorn
    except ImportError:
        print("  uvicorn not found — installing...")
        pip_install("uvicorn[standard]")

    # Ensure streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("  streamlit not found — installing...")
        pip_install("streamlit")

    # Ensure mysql-connector is installed
    try:
        import mysql.connector
    except ImportError:
        print("  mysql-connector-python not found — installing...")
        pip_install("mysql-connector-python")

    # Check files
    for fname in ["main.py", "app.py"]:
        fpath = os.path.join(PROJECT_DIR, fname)
        if not os.path.exists(fpath):
            print(f"\n  ERROR: {fname} not found in {PROJECT_DIR}")
            print("  Make sure you are running from the correct folder.")
            input("Press Enter to exit...")
            sys.exit(1)

    pkl = os.path.join(PROJECT_DIR, "pipeline.pkl")
    if not os.path.exists(pkl):
        print(f"\n  WARNING: pipeline.pkl not found!")
        print(f"  Copy pipeline.pkl to: {PROJECT_DIR}")
        print("  (App will start but predictions will fail)\n")
    else:
        print(f"  pipeline.pkl found  ({os.path.getsize(pkl):,} bytes)")

    print("  All checks passed.\n")

# ── start FastAPI ─────────────────────────────────────────────────────────────
def start_api():
    print("── Starting FastAPI (port 8000) ─────────────────────────")

    if not port_free(8000):
        print("  Port 8000 in use — freeing it...")
        kill_port(8000)

    # Build command — use full python path so Windows finds it
    cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--reload",
        "--log-level", "info",
    ]
    print(f"  CMD: {' '.join(cmd)}")
    print(f"  CWD: {PROJECT_DIR}\n")

    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ, "PYTHONPATH": PROJECT_DIR},
    )

    # Stream logs + wait for ready signal
    ready = threading.Event()
    log_lines = []

    def reader():
        for line in proc.stdout:
            log_lines.append(line)
            print(f"  [API] {line}", end="")
            if "Application startup complete" in line or "Uvicorn running" in line:
                ready.set()

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    # Wait max 15s for startup
    if ready.wait(timeout=15):
        print("\n  FastAPI is READY!\n")
    else:
        if proc.poll() is not None:
            print(f"\n  FastAPI CRASHED (exit {proc.returncode})")
            print("  Check errors above. Common fixes:")
            print("  1. pip install -r requirements.txt")
            print("  2. Make sure main.py is in the same folder as run.py")
            input("\nPress Enter to exit...")
            sys.exit(1)
        else:
            print("\n  FastAPI starting (slow machine)...\n")

    return proc

# ── start Streamlit ───────────────────────────────────────────────────────────
def start_ui():
    print("── Starting Streamlit (port 8501) ───────────────────────")

    if not port_free(8501):
        print("  Port 8501 in use — freeing it...")
        kill_port(8501)

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join(PROJECT_DIR, "app.py"),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false",
    ]

    proc = subprocess.Popen(cmd, cwd=PROJECT_DIR)
    time.sleep(4)

    if proc.poll() is not None:
        print(f"  Streamlit CRASHED (exit {proc.returncode})")
        print("  Fix: pip install streamlit")
        return None

    print("  Streamlit is READY!\n")
    return proc

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 58)
    print("   STOCK ROCE PREDICTOR  —  v3.0")
    print(f"   {PROJECT_DIR}")
    print("=" * 58)

    preflight()

    api = start_api()
    ui  = start_ui()

    if ui is None:
        api.terminate()
        sys.exit(1)

    print("=" * 58)
    print("  RUNNING")
    print("  FastAPI   ->  http://localhost:8000/docs")
    print("  Streamlit ->  http://localhost:8501")
    print("  Ctrl+C to stop both servers.")
    print("=" * 58 + "\n")

    try:
        api.wait()
        ui.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        api.terminate()
        ui.terminate()
        try:
            api.wait(timeout=4)
            ui.wait(timeout=4)
        except Exception:
            api.kill()
            ui.kill()
        print("Stopped. Bye!\n")

if __name__ == "__main__":
    main()
