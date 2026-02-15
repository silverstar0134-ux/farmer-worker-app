import os
import subprocess
import time
import sys

os.chdir(r'c:\Users\silve\Desktop\my\farmer')

# Start the server
process = subprocess.Popen(
    [sys.executable, 'manage.py', 'runserver'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait a bit for startup
time.sleep(2)

# Check if process is still running
if process.poll() is None:
    print("✓ Django development server started successfully!")
    print("✓ Server is running on http://127.0.0.1:8000/")
    
    # Kill the process since we just needed to verify it works
    process.terminate()
else:
    stdout, stderr = process.communicate()
    print("✗ Server failed to start")
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
