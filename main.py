import network
import time
import urequests as requests
from picographics import PicoGraphics, DISPLAY_INTERSTATE75_64X64
from pngdec import PNG
import json
import logging

logging.basicConfig(level=logging.INFO)

display = PicoGraphics(display=DISPLAY_INTERSTATE75_64X64, rotate=0)
png = PNG(display)

LON = -84.3895
LAT = 33.7490
ZOOM = 13

W, H = 64

def load_secrets(WIFI_PASS=None, WIFI_SSID=None, MAPBOX_TOKEN=None):
    # Assuming you have a file named 'secrets.json' in the same directory
    data_from_file = []
    with open('secrets.json', 'r') as f:
        data_from_file = json.load(f)
    WIFI_PASS = data_from_file['WIFI_PASS']
    WIFI_SSID = data_from_file['WIFI_SSID']
    MAPBOX_TOKEN = data_from_file['MAPBOX_TOKEN']

# Optional: a little LED indicator using onboard RGB if available
# (Interstate board examples sometimes expose an RGB LED API; if not, ignore)
def connect_wifi(ssid, password, timeout=20):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    if wlan.isconnected():
        return wlan
    wlan.connect(ssid, password)
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            raise RuntimeError("WiFi connect timeout")
        time.sleep(0.5)
    return wlan

def build_static_image_url(lon, lat, zoom, w, h, token):
    base = "https://api.mapbox.com/styles/v1"
    style_path = "mapbox/streets-v11"
    url = "{}/{}/static/{:.6f},{:.6f},{}/{}x{}?access_token={}".format(
        base, style_path, lon, lat, zoom, w, h, token
    )
    return url

def download_map(url, filename):
    response = requests.get(url)
    if response.status_code == 200 and response.content:
        data = response.content
        # write binary to file on the board
        with open(filename, "wb") as f:
            f.write(data)
        complete = True
    else:
        print("Map fetch failed: ", response.status_code)

def main():
    # Connect WiFi
    WIFI_PASS, WIFI_SSID, MAPBOX_TOKEN = ''
    UPDATE_INTERVAL = 300
    try:
        load_secrets(WIFI_PASS, WIFI_SSID, MAPBOX_TOKEN)
        connect_wifi(WIFI_SSID, WIFI_PASS)
        MAP_FILENAME = "map.png"
        png = PNG(None)
        while True:
            url = build_static_image_url(LON, LAT, ZOOM, W, H, MAPBOX_TOKEN)
            downloaded = download_map(url, MAP_FILENAME)
            if not downloaded:
                # Skip this iteration if download failed
                return
            if png.open_file(MAP_FILENAME):
                png.decode(0, 0)
                display.update()
            for _ in range(int(UPDATE_INTERVAL / 5)):
                time.sleep(5)
    except Exception as e:
        print("Exception raised: ", e)
        return

# if run as script
if __name__ == "__main__":
    main()
