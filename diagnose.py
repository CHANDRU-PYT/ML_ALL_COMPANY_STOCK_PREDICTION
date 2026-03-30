"""
================================================
  diagnose.py — Run this FIRST to find & fix
  the "FastAPI Offline" error automatically.
  Usage:  python diagnose.py
================================================
"""
import sys, os, socket, subprocess, importlib

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
print("=" * 60)
print("  STOCK ROCE PREDICTOR — DIAGNOSTIC TOOL")
print("=" * 60)
print(f"\n  Project folder : {PROJECT_DIR}")
print(f"  Python         : {sys.executable}")
print(f"  Python version : {sys.version.split()[0]}\n")

errors   = []
warnings = []

# ── 1. Check required files ───────────────────────────────────────────────────
print("── [1] Checking files ───────────────────────────────────")
required_files = {
    "main.py":       "FastAPI backend",
    "app.py":        "Streamlit frontend",
    "pipeline.pkl":  "ML model (REQUIRED for predictions)",
}
for fname, desc in required_files.items():
    fpath = os.path.join(PROJECT_DIR, fname)
    if os.path.exists(fpath):
        print(f"  OK   {fname:<15}  {os.path.getsize(fpath):>10,} bytes  — {desc}")
    else:
        print(f"  MISS {fname:<15}  NOT FOUND  — {desc}")
        if fname == "pipeline.pkl":
            errors.append(f"pipeline.pkl missing — copy it to: {PROJECT_DIR}")
        else:
            errors.append(f"{fname} missing from: {PROJECT_DIR}")

# ── 2. Check required packages ────────────────────────────────────────────────
print("\n── [2] Checking Python packages ─────────────────────────")
packages = {
    "fastapi":            "fastapi",
    "uvicorn":            "uvicorn",
    "streamlit":          "streamlit",
    "pandas":             "pandas",
    "sklearn":            "scikit-learn",
    "xgboost":            "xgboost",
    "pydantic":           "pydantic",
    "requests":           "requests",
    "yfinance":           "yfinance",
    "mysql.connector":    "mysql-connector-python",
    "category_encoders":  "category_encoders",
}
missing_pkgs = []
for mod, pkg in packages.items():
    try:
        importlib.import_module(mod)
        print(f"  OK   {pkg}")
    except ImportError:
        print(f"  MISS {pkg}  <-- NOT INSTALLED")
        missing_pkgs.append(pkg)

if missing_pkgs:
    errors.append(f"Missing packages: {', '.join(missing_pkgs)}")

# ── 3. Check port 8000 ────────────────────────────────────────────────────────
print("\n── [3] Checking ports ───────────────────────────────────")
for port, name in [(8000, "FastAPI"), (8501, "Streamlit")]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        in_use = s.connect_ex(("localhost", port)) == 0
    if in_use:
        print(f"  BUSY Port {port} ({name}) — already occupied, will be auto-killed by run.py")
        warnings.append(f"Port {port} in use — run.py will kill it automatically")
    else:
        print(f"  FREE Port {port} ({name})")

# ── 4. Try importing main.py to catch syntax/import errors ────────────────────
print("\n── [4] Validating main.py for errors ────────────────────")
main_path = os.path.join(PROJECT_DIR, "main.py")
if os.path.exists(main_path):
    result = subprocess.run(
        [sys.executable, "-c", f"import ast; ast.parse(open(r'{main_path}').read()); print('Syntax OK')"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  OK   main.py syntax is valid")
    else:
        print(f"  ERR  main.py has syntax errors:\n{result.stderr}")
        errors.append("main.py has syntax errors — see above")

# ── 5. Test uvicorn availability ──────────────────────────────────────────────
print("\n── [5] Checking uvicorn command ─────────────────────────")
result = subprocess.run(
    [sys.executable, "-m", "uvicorn", "--version"],
    capture_output=True, text=True
)
if result.returncode == 0:
    print(f"  OK   {result.stdout.strip()}")
else:
    print("  ERR  uvicorn not found!")
    errors.append("uvicorn not installed — run: pip install uvicorn[standard]")

# ── 6. Auto-fix: install missing packages ────────────────────────────────────
if missing_pkgs:
    print(f"\n── [6] Auto-installing missing packages ─────────────────")
    pkgs_str = " ".join(missing_pkgs)
    print(f"  Running: pip install {pkgs_str}")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install"] + missing_pkgs,
        capture_output=False, text=True
    )
    if result.returncode == 0:
        print("  Packages installed successfully!")
        errors = [e for e in errors if "Missing packages" not in e]
    else:
        print("  pip install failed — try running manually.")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if not errors:
    print("  ALL CHECKS PASSED — Ready to run!")
    print("\n  Next step:  python run.py")
else:
    print(f"  {len(errors)} ERROR(S) FOUND:")
    for i, e in enumerate(errors, 1):
        print(f"    {i}. {e}")
    print()
    if any("pipeline.pkl" in e for e in errors):
        print("  MOST IMPORTANT FIX:")
        print(f"  Copy pipeline.pkl into this folder:")
        print(f"  {PROJECT_DIR}")

if warnings:
    print(f"\n  {len(warnings)} WARNING(S):")
    for w in warnings:
        print(f"    - {w}")

print("=" * 60)
print("\nAfter fixing errors above, run:  python run.py\n")
input("Press Enter to exit...")
