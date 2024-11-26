import gc
import network
from time import sleep_us
from machine import Pin, time_pulse_us

# Garbage collection
gc.collect()

# Not possible to use getenv on esp32 :(
WIFI_SSID = "HORTICONNECT-NET"
WIFI_PASSWORD = "BrumsenKinet"

def connect_wifi():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print("Network config:", wlan.ifconfig())

def get_brightness():
    pass

def get_distance():
    # Retourne la distance en cm
    sig = Pin(26, Pin.OUT) # GPIO 26
    sig.value(0)
    sleep_us(5)
    sig.value(1)
    sleep_us(10)
    sig.value(0)
    sig = Pin(26, Pin.IN)
    t = time_pulse_us(sig, 1, 30000)
    distance = 340 * t // 20000
    return distance

def send_mqtt():
    pass

def main():
    connect_wifi()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)