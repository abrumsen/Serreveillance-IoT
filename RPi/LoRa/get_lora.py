import serial
import json
import re
import paho.mqtt.client as mqtt
import time
import logging
import systemd.journal

CLIENT_ID = "Client_1"
SERRE_ID = "Serre_1"
TOPIC_PREFIX = "Heltec-Horticonnect-Prototype"
SERVER = "192.168.1.110"

# Configure logging to use systemd journal
logger = logging.getLogger("lora-relay")
logger.addHandler(systemd.journal.JournalHandler())
logger.setLevel(logging.INFO)

class LoRaRelay:
    def __init__(self, client_id, serre_id, server, serial_port='/dev/ttyUSB0', baud_rate=9600, port=1883, keepalive=300):
        """Initialize serial and MQTT connection parameters"""
        self.client_id = client_id
        self.serre_id = serre_id
        self.server = server
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.port = port
        self.keepalive = keepalive
        self.connected = False
        self.mqtt_client = None
        
    def on_connect(self, client, userdata, flags, rc, properties):
        """Callback for when the client receives a CONNACK response from the server"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker with result code {rc}")
            self.connected = True
        else:
            logger.error(f"Failed to connect to MQTT broker with result code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, disconnect_flags, rc, properties):
        """Callback for when the client disconnects from the server"""
        logger.warning(f"Disconnected from MQTT broker with result code {rc}")
        self.connected = False
    
    def on_publish(self, client, userdata, mid, rc, properties):
        """Callback for when a message is published"""
        logger.debug(f"Message {mid} published successfully")
        
    def connect_mqtt(self):
        """Establish MQTT connection"""
        try:
            # Create a new MQTT client instance
            self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "Heltec-Horticonnect-Prototype")
            
            # Set callbacks
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_disconnect = self.on_disconnect
            self.mqtt_client.on_publish = self.on_publish
            
            # Connect to broker
            logger.info(f"Connecting to {self.server}")
            self.mqtt_client.connect(self.server, self.port, self.keepalive)
            
            # Start the loop
            self.mqtt_client.loop_start()
            
            # Wait for connection to be established
            timeout = 5
            start_time = time.time()
            while not self.connected and (time.time() - start_time < timeout):
                time.sleep(5)
            
            return self.connected
            
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            return False

    def publish_message(self, message):
        """Publish MQTT message with connection retry"""
        if not self.connected:
            logger.warning("Not connected to MQTT broker. Attempting to reconnect...")
            if not self.connect_mqtt():
                logger.error("Reconnection failed")
                return False
        
        try:
            topic = f"{TOPIC_PREFIX}/temphumi"
            info = self.mqtt_client.publish(topic, message, qos=2)
            info.wait_for_publish()
            return True
            
        except Exception as e:
            logger.error(f"Error publishing message: {e}")
            return False

    def get_readings(self):
        """Get humidity and temperature from serial and publish via MQTT"""
        try:
            with serial.Serial(self.serial_port, self.baud_rate, timeout=1) as ser:
                while True:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        pattern = r"horticonnect t: (\d+) h: (\d+)"
                        match = re.search(pattern, line)
                        if match:
                            temperature = match.group(1)
                            humidity = match.group(2)
                            msg = json.dumps({
                                "client": self.client_id,
                                "serre": self.serre_id,
                                "temp": temperature,
                                "humi": humidity
                            })
                            self.publish_message(msg)
                            
        except serial.SerialException as e:
            logger.error(f"Error: Could not open serial port {self.serial_port}. {e}")
        except KeyboardInterrupt:
            logger.error("\nExiting program.")
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()

    def start_relay(self):
        """Start relaying the humidity and temperature readings"""
        logger.info(f"Starting LoRa relay for {self.serre_id}")
        
        if not self.connect_mqtt():
            logger.error("Failed to start relay - MQTT connection failed")
            return
        
        logger.info("Beginning data collection...")
        self.get_readings()

def main():
    relay = LoRaRelay(
        CLIENT_ID,
        SERRE_ID,
        SERVER
    )
    relay.start_relay()

if __name__ == "__main__":
    main()