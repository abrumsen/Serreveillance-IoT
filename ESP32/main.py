from json import dumps
from time import sleep, sleep_us
from machine import Pin, ADC, time_pulse_us
from umqtt.simple import MQTTClient
import _thread
from cert import ROOT_CA

CLIENT_ID = "Client_1"
SERRE_ID = "Serre_1"
#SERVER = "192.168.1.110"
SERVER = "broker.hivemq.com"

class SensorPublisher:
    def __init__(self, client_id, serre_id, server, port=8883, keepalive=300):
        """Initialize MQTT connection parameters"""
        self.client_id = client_id
        self.serre_id = serre_id
        self.server = server
        self.port = port
        self.keepalive = keepalive
        self.mqtt_client = None
        self.lock = _thread.allocate_lock() # Make MQTTClient thread-safe(r)
    
    def connect_mqtt(self):
        """Establish MQTT connection"""
        try:
            self.mqtt_client = MQTTClient(
                "ESP32-Horticonnect-Prototype", 
                self.server, 
                keepalive=self.keepalive, 
                port=self.port,
                ssl=True,
                ssl_params={"cadata": ROOT_CA}
            )
            self.mqtt_client.connect()
        except Exception as e:
            print(f"MQTT Connection Error: {e}")
            self.mqtt_client = None
    
    def publish_message(self, topic, message):
        """Publish MQTT message with connection retry"""
        try:
            with self.lock:
                if not self.mqtt_client:
                    self.connect_mqtt()
                
                if self.mqtt_client:
                    if not isinstance(message, str):
                        raise ValueError("Message must be a string")
                    self.mqtt_client.publish(topic.encode(), message.encode())
        except Exception as e:
            print(f"Publish Error on {topic}: {e}")
            self.mqtt_client = None
    
    def get_brightness(self):
        """Get brightness and publish via MQTT every minute"""
        while True:
            try:
                pin = Pin(35, Pin.IN)
                adc = ADC(pin)
                adc.atten(ADC.ATTN_0DB)
                brightness = round(adc.read() / 40.95, 1) # Value ranges from 0-4095
                
                msg = dumps({
                    "client": self.client_id,
                    "serre": self.serre_id,
                    "brightness (%)": brightness
                })
                
                self.publish_message(
                    "ESP32-Horticonnect-Prototype/brightness", 
                    msg
                )
            except Exception as e:
                print("Brightness sensor error:", e)
            
            sleep(60)
    
    def get_distance(self):
        """Get distance and publish via MQTT every minute"""
        while True:
            try:
                sig = Pin(26, Pin.OUT)
                sig.value(0)
                sleep_us(5)
                sig.value(1)
                sleep_us(10)
                sig.value(0)
                
                sig = Pin(26, Pin.IN)
                t = time_pulse_us(sig, 1, 30000)
                distance = 340 * t // 20000
                
                msg = dumps({
                    "client": self.client_id, 
                    "serre": self.serre_id,
                    "distance (cm)": distance
                })
                
                self.publish_message(
                    "ESP32-Horticonnect-Prototype/distance", 
                    msg
                )
            except Exception as e:
                print("Distance sensor error:", e)
            
            sleep(60)
    
    def start_monitoring(self):
        """Start threads for brightness and distance sensors"""
        try:
            # Initial MQTT connection
            self.connect_mqtt()
            
            # Start brightness thread
            _thread.start_new_thread(self.get_brightness, ())
            
            # Start distance thread
            _thread.start_new_thread(self.get_distance, ())
            
            # Keep main thread alive and check MQTT connection
            while True:
                try:
                    # Send a ping to keep connection alive
                    if self.mqtt_client:
                        self.mqtt_client.ping()
                except:
                    self.connect_mqtt()
                sleep(30)
        except Exception as e:
            print("Error in main thread:", e)

def main():
    sensor_pub = SensorPublisher(
        CLIENT_ID,
        SERRE_ID,
        SERVER
    )
    sensor_pub.start_monitoring()

if __name__ == '__main__':
    main()