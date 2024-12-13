import time
from datetime import datetime, timedelta
import grovepi
import grove_rgb_lcd
import serial

# Define ports
button_pin = 3
led_pin = 4

grovepi.pinMode(button_pin, "INPUT")
grovepi.pinMode(led_pin, "OUTPUT")

# Serial for RFID
ser = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
ser.flush()

# LCD Messages and Colors
messages = [
    "Welcome!", "Scan your card!", "Access Granted!", "Access Denied!"
]
lcd_colors = [
    [0, 255, 0],  # Green
    [255, 0, 0],  # Red
]

# Variables for RFID and Button Handling
last_auth_time = None
auth_duration = timedelta(minutes=1)  # Valid for 10 minutes
authorized_card = "E30840"  # Replace with the actual card ID

def read_rfid():
    """Reads RFID and returns the card ID."""
    card = b""
    while len(card) < 14:
        c = ser.read()
        card += c
    return card[5:11].decode('utf-8')

def blink_led():
    """Keeps the system alive by blinking the LED."""
    grovepi.digitalWrite(led_pin, 1)
    time.sleep(0.5)
    grovepi.digitalWrite(led_pin, 0)
    time.sleep(0.5)

def update_lcd(message, color):
    """Updates the LCD with the given message and color."""
    grove_rgb_lcd.setText(message)
    grove_rgb_lcd.setRGB(color[0], color[1], color[2])

def is_authorized():
    """Checks if the button press is authorized based on RFID scan."""
    if last_auth_time and datetime.now() - last_auth_time < auth_duration:
        return True
    return False

try:
    print("System initialized. Waiting for RFID...")
    update_lcd(messages[1], lcd_colors[1])  # Prompt to scan RFID

    while True:
        blink_led()  # Keep-alive LED

        # Check for RFID scan
        if ser.in_waiting > 0:
            scanned_card = read_rfid()
            print(f"Scanned card: {scanned_card}")

            if scanned_card == authorized_card:
                print("Access Granted!")
                last_auth_time = datetime.now()
                update_lcd(messages[2], lcd_colors[0])  # Access Granted
            else:
                print("Access Denied!")
                update_lcd(messages[3], lcd_colors[1])  # Access Denied
            time.sleep(2)
            # Only reset LCD to "Scan your card" if not authorized
            if not is_authorized():
                update_lcd(messages[1], lcd_colors[1])  # Prompt again

        # Check button press
        button_state = grovepi.digitalRead(button_pin)
        if button_state == 1:
            time.sleep(0.2)  # Debounce the button press
            if grovepi.digitalRead(button_pin) == 1:  # Confirm button press
                if is_authorized():
                    print("Button Pressed - Action Authorized")
                    update_lcd("Action OK!", lcd_colors[0])
                    time.sleep(5)  # Show final message longer
                else:
                    print("Unauthorized Button Press")
                    update_lcd("Scan Card First!", lcd_colors[1])
                    time.sleep(2)  # Allow message to linger

            # Wait for button release
            while grovepi.digitalRead(button_pin) == 1:
                time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting program.")
    grove_rgb_lcd.setText("")
    grove_rgb_lcd.setRGB(0, 0, 0)
    grovepi.digitalWrite(led_pin, 0)
except Exception as e:
    print(f"Error: {e}")

