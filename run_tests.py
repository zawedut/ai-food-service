import subprocess
import time
import sys

print("Starting server...")
server = subprocess.Popen(["python3", "-m", "uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", "8000"])
time.sleep(3)
print("Testing...")
res = subprocess.run(["python3", "test_api.py"])
server.terminate()
sys.exit(res.returncode)
