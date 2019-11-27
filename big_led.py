import time
import network
import secrets
from umqtt.simple import MQTTClient
from machine import Pin,PWM

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.essid, secrets.passwd) # your local wifi credentials

green_led = Pin(14, Pin.OUT) # which pin your LED is connected to
green_led_pwm = PWM(green_led)

# keep trying to connect to the wifi until we suceed
while not wlan.isconnected():
	time.sleep_ms(500)

wlan.ifconfig()

def set_state(msg):
	if msg == b'on':
		green_led_pwm.duty(10) # 0-1023, 512 is 50% brightness
	elif msg == b'off':
		green_led_pwm.duty(0) 

# topics we recognize with their respective functions
subtopic = {
	b'green_led/state': set_state,
}

def handle_msg(topic,msg):
	print("topic:'", topic, "' msg:'", msg, "'")

	if topic in subtopic:
		# call function associated with topic, passing message as parameter
		subtopic[topic](msg)
	else: 
		print("topic not recognized")

# start the MQTT client for this microcontroller
mq = MQTTClient("neo", "192.168.0.23")
mq.set_callback(handle_msg) # set_led will be called for ALL messages received
mq.connect()
mq.subscribe(b"green_led/#") # specify the topic to subscribe to (led in this case)

# wait for messages forever
# when one is received the function we passed to set_callback() will be run
while True:
	mq.wait_msg()