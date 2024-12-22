import network

WIFI_SSID = "Horticonnect-NET"
WIFI_PASSWORD = "BrumsenKinet"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass

connect()