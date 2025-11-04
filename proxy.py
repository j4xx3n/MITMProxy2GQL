#!/usr/bin/env python3

import asyncio
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import http
import subprocess
import json # Import the json library
import os # Import os for path manipulation
import time

domain = input("Enter Domain to Proxy: ")
print(f"Proxying only: {domain}")
time.sleep(2)

try:
    print(f"Starting Chromium with proxy on 127.0.0.1:8080...")
    time.sleep(2)
    with open('/dev/null', 'w') as devnull:
        process = subprocess.Popen(
            ['chromium', '--proxy-server=http://127.0.0.1:8080'],
            stderr=devnull,
        )
    print(f"Chromium process started with PID: {process.pid}")
    print("The script will continue running with the browser in the background.")
    time.sleep(2)

except FileNotFoundError:
    print("Error: The 'chromium-browser' command was not found. Make sure Chromium is installed and in your system's PATH.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Define the output file name
OUTPUT_FILENAME = "queries.json"

# Clear the file on startup for a fresh run
if os.path.exists(OUTPUT_FILENAME):
    os.remove(OUTPUT_FILENAME)

class InterceptAddon:
    # This method handles incoming client requests
    def request(self, flow: http.HTTPFlow) -> None:
        contentType = flow.request.headers.get("Content-Type", "")
        host = getattr(flow.request, "pretty_host", None) or flow.request.host or ""

        # Check if the domain matches AND the request body is JSON
        if host.endswith(domain):
            if "application/json" in contentType:
                request_text = flow.request.get_text(strict=False)

                # Check if there is actual content
                if request_text:
                    # --- File Output Logic for Requests ---
                    try:
                        with open(OUTPUT_FILENAME, "a") as f:
                            f.write(request_text + "\n")

                        # Print confirmation to the console
                        print(f"JSON request saved to file from: {flow.request.pretty_url}")

                    except Exception as e:
                        print(f"Error writing request to file: {e}")

async def proxy():
    opts = Options(listen_host="127.0.0.1", listen_port=8080)
    m = DumpMaster(opts)
    m.addons.add(InterceptAddon())

    print(f"Starting proxy on 127.0.0.1:8080 ...")
    time.sleep(2)
    print("\n\n*** Press ENTER to stop the proxy and parse schema. ***\n")
    time.sleep(10)
    proxy_task = asyncio.create_task(m.run())

    await asyncio.to_thread(input)

    print("Stopping proxy...")
    m.shutdown()

    # --- run the bash script when we reach "Parsing schema..." ---
    print("Parsing schema...")

    # path to your script (ensure it exists and is executable or call it via bash)
    script_path = "./my_script.sh"

    # Option A — wait for the script to finish and capture output
    proc = await asyncio.create_subprocess_exec(
        "./parser.py", script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if stdout:
        #print("script stdout:")
        print(stdout.decode(errors="ignore"))
    if stderr:
        print("script stderr:")
        print(stderr.decode(errors="ignore"))

    print(f"Script exited with code: {proc.returncode}")

    await proxy_task

def main():
    try:
        asyncio.run(proxy())

    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    main()
