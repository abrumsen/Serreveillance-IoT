import gc
import json
from time import sleep_us, sleep
from machine import Pin, time_pulse_us, ADC
from umqtt.simple import MQTTClient

# Garbage collection
gc.collect()

# Static vars ----------------------------------
CLIENT_NAME = "ESP-32-Horticonnect"
BROKER_ADDR = "test.mosquitto.org"
# ----------------------------------------------

def send_mqtt(message, topic):
    mqttc = MQTTClient(CLIENT_NAME, BROKER_ADDR, keepalive=60)
    mqttc.connect()
    mqttc.publish(topic.encode(), message.encode())
    mqttc.disconnect()

def get_brightness():
    # Retourne la luminosité en %
    pin = Pin(35, Pin.IN)
    adc = ADC(pin)
    adc.atten(ADC.ATTN_0DB)
    brightness = adc.read()/40.95 # Value ranges from 0-4095
    # Envoie le résultat via mqtt
    msg = {"client": CLIENT_NAME, "brightness (%)": brightness}
    msg = json.dumps(msg)
    send_mqtt(msg, CLIENT_NAME + "/brightness")

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
    # Envoie le résultat via mqtt
    msg = {"client": CLIENT_NAME, "distance (cm)": distance}
    msg = json.dumps(msg)
    send_mqtt(msg, CLIENT_NAME + "/distance")

def main():
    while True:
        get_distance()
        sleep(30)
        get_brightness()
        sleep(30)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error:', e)