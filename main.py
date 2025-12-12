import network
import time
import urequests as requests
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
from pngdec import PNG
import json

i75 = Interstate75(DISPLAY_INTERSTATE75_128X128, stb_invert=False)
display = i75.display

width = i75.width
height = i75.height

LON = -84.3895
LAT = 33.7490
ZOOM = 13

def load_secrets():
    # Assuming you have a file named 'secrets.json' in the same directory
    with open('secrets.json', 'r') as f:
        data_from_file = json.load(f)
    return data_from_file['WIFI_PASS'], data_from_file['WIFI_SSID'], data_from_file['MAPBOX_TOKEN']

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

def download_map(url, filename, downloaded):
    response = requests.get(url)
    if response.status_code == 200 and response.content:
        data = response.content
        # write binary to file on the board
        with open(filename, "wb") as f:
            f.write(data)
        downloaded = True
    else:
        print("Map fetch failed: ", response.status_code, ", Downloaded: ", downloaded)

def main():
    # Connect WiFi
    UPDATE_INTERVAL = 300
    try:
        print('[MAIN] Loading secrets and connecting to WiFi')
        WIFI_PASS, WIFI_SSID, MAPBOX_TOKEN = load_secrets()
        connect_wifi(WIFI_SSID, WIFI_PASS)
        print('[MAIN] Connected to WiFi')
        MAP_FILENAME = "map.png"
        png = PNG(display)
        print("[MAIN] Starting map download loop")
        while True:
            url = build_static_image_url(LON, LAT, ZOOM, width, height, MAPBOX_TOKEN)
            print("[MAIN] Downloading map from URL: ", url)
            downloaded = False
            download_map(url, MAP_FILENAME, downloaded)
            print("[MAIN] Map was downloaded: ", downloaded)
            if not downloaded:
                # Skip this iteration if download failed
                return
            if png.open_file(MAP_FILENAME):
                print("[MAIN] Displaying map image")
                png.decode(0, 0)
                i75.update()
            for _ in range(int(UPDATE_INTERVAL / 5)):
                time.sleep(5)
            print("[MAIN] nd of iteration, restarting loop")
    except Exception as e:
        print("Exception raised: ", e)
        return

# if run as script
if __name__ == "__main__":
    main()
