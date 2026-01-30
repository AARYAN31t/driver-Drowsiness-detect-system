import urllib.request
import os

url = "https://raw.githubusercontent.com/kurnianggoro/GSOC2017/master/data/lbfmodel.yaml"
filename = "backend/lbfmodel.yaml"

if not os.path.exists("backend"):
    os.makedirs("backend")

print(f"Downloading {filename}...")
try:
    urllib.request.urlretrieve(url, filename)
    print("Download complete!")
    print(f"File size: {os.path.getsize(filename)} bytes")
except Exception as e:
    print(f"Download failed: {e}")
