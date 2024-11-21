import gc
import network
import time
# Garbage collection
gc.collect()

WIFI_SSID = "your_ssid"
WIFI_PASSWORD = "your_password"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print("Network config:", wlan.ifconfig())

def main():
    connect_wifi()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)