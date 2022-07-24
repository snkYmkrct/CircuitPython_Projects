import ssl
import wifi
import socketpool
import adafruit_requests
import time
import board
import neopixel
import pwmio
from adafruit_io.adafruit_io import IO_HTTP
from adafruit_motor import servo

# create a PWMOut object on Pin A2.
pwm = pwmio.PWMOut(board.A2, frequency=50)

# Create a servo object, my_servo.
my_servo = servo.ContinuousServo(pwm)

num_pixels = 1
pixels = neopixel.NeoPixel(board.A1, num_pixels, brightness=0.2, auto_write=True)

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)

# secrets.py has SSID/password and adafruit.io
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
AIO_USERNAME = secrets["aio_username"]
AIO_KEY = secrets["aio_key"]
SERVO_FEED = "servo-throttle"

# Connect to WiFi
print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])

# Setup Adafruit IO connection
POOL = socketpool.SocketPool(wifi.radio)
REQUESTS = adafruit_requests.Session(POOL, ssl.create_default_context())
# Initialize an Adafruit IO HTTP API object
IO = IO_HTTP(AIO_USERNAME, AIO_KEY, REQUESTS)

pixels.fill(CYAN)
time.sleep(1)

while True:
    try:
        servo_feed = IO.get_feed(SERVO_FEED)
        servo_data = IO.receive_data(servo_feed["key"])
        servo_direction = float(servo_data["value"])
        print(servo_direction)

        if (servo_direction == 1.0):
            print("Forward")
            pixels.fill(PURPLE)
        elif (servo_direction == -1.0):
            print("Backward")
            pixels.fill(RED)
        elif (servo_direction == -0.1):
            # stop value should be 0.0 but this servo is a weirdo
            print("Stopped")
            pixels.fill(OFF)
        else:
            print("Incorrect feed - not a valid continuous servo throttle value")

        my_servo.throttle = servo_direction
    except Exception as error:
        print(error)


