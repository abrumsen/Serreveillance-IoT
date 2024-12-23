import time
from datetime import datetime, timedelta
import grovepi
import grove_rgb_lcd
import serial
import requests

import logging
import systemd.journal

# Configure logging to use systemd journal
logger = logging.getLogger("greenhouse-interface")
logger.addHandler(systemd.journal.JournalHandler())
logger.setLevel(logging.INFO)

CLIENT_ID = "Client1"

class Interface:
    def __init__(self):
        """"Initialize pins, pin modes, serial connection, messages and auth time."""
        self.button_pin= 3
        self.led_pin = 4
        self.buzzer_pin = 2
        grovepi.pinMode(self.button_pin, "INPUT")
        grovepi.pinMode(self.led_pin, "OUTPUT")
        grovepi.pinMode(self.buzzer_pin, "OUTPUT")
        self.rfid = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
        self.rfid.flush()
        self.messages = ["Welcome!", "Scan your card!", "Access Granted!", "Access Denied!"]
        self.lcd_colors = [[0, 255, 0],[255, 0, 0]]
        self.last_auth_time = None
        self.auth_duration = timedelta(minutes=3)

    def read_rfid(self):
        """Reads RFID and returns the card ID."""
        tag_id = b""
        while len(tag_id) < 14:
            raw_data = self.rfid.read()
            tag_id += raw_data
        tag_id = tag_id[5:11]
        if tag_id:
            return "validcard"

    def blink_led(self):
        """Show system keepalive by blinking the LED."""
        grovepi.digitalWrite(self.led_pin, 1)
        time.sleep(0.5)
        grovepi.digitalWrite(self.led_pin, 0)
        time.sleep(0.5)

    def update_lcd(self,message, color):
        """Updates the LCD with the given message and color."""
        grove_rgb_lcd.setText(message)
        grove_rgb_lcd.setRGB(color[0], color[1], color[2])

    def is_authorized(self):
        """Checks if the button press is authorized based on RFID scan."""
        if self.last_auth_time and datetime.now() - self.last_auth_time < self.auth_duration:
            return True
        return False

    def sound_buzzer(self):
        """Sounds the buzzer briefly."""
        grovepi.digitalWrite(self.buzzer_pin, 1)
        time.sleep(0.5)
        grovepi.digitalWrite(self.buzzer_pin, 0)
    
    def start(self):
        try:
            logger.info("System initialized. Ready for RFID...")
            self.update_lcd(self.messages[1], self.lcd_colors[1])

            while True: # This should be threaded ideally, but race conditions happen on I/O
                self.blink_led()
                # Check for RFID scan
                if self.rfid.in_waiting > 14:
                    logger.info("Card detected")
                    scanned_card = self.read_rfid()
                    # API CALL HERE
                    logger.info("Checking authorization with server...")
                    r = requests.get(f"http://192.168.1.110:5000/auth?id={scanned_card}&client={CLIENT_ID}", headers={"x-api-key": "test"})
                    logger.debug("Got response:")
                    response = r.json()
                    logger.debug(response)
                    if response["isAuthorized"]:
                        logger.info("Access Granted!")
                        self.last_auth_time = datetime.now()
                        self.sound_buzzer()
                        self.update_lcd(self.messages[2], self.lcd_colors[0])
                    else:
                        logger.warning("Access Denied!")
                        self.update_lcd(self.messages[3], self.lcd_colors[1])
                    time.sleep(2)
                    # Only reset LCD to "Scan your card" if not authorized
                    if not self.is_authorized():
                        self.update_lcd(self.messages[1], self.lcd_colors[1])

                # Check button press
                button_state = grovepi.digitalRead(self.button_pin)
                if button_state == 1:
                    if self.is_authorized():
                        logger.info("Button Pressed - Action Authorized")
                        self.update_lcd(f"ClientID: {CLIENT_ID}", self.lcd_colors[0])
                        time.sleep(5)
                    else:
                        logger.warning("Unauthorized Button Press")
                        self.update_lcd("Scan Card First!", self.lcd_colors[1])
                        time.sleep(2)

                # Wait for button release
                while grovepi.digitalRead(self.button_pin) == 1:
                    time.sleep(0.1)
                self.rfid.close()
                self.rfid.open()
                

        except KeyboardInterrupt:
            logger.warning("Exiting program.")
            grove_rgb_lcd.setText("")
            grove_rgb_lcd.setRGB(0, 0, 0)
            grovepi.digitalWrite(self.led_pin, 0)
            grovepi.digitalWrite(self.buzzer_pin, 0)
        except Exception as e:
            logger.error(f"Error: {e}")

def main():
    interface = Interface()
    interface.start()

if __name__ == "__main__":
    main()
