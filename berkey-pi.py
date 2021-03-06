 #!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import smtplib
import os
import json
from datetime import datetime,date
import sqlite3
import berkeydb


def get_config():
	with open(os.path.dirname(os.path.realpath(__file__)) + '/berkey-pi.config.json') as f:
		data = json.load(f)
		return data

def setup_io():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.IN)
	GPIO.setup(4, GPIO.OUT)

def send_alert_email(config):
	server= smtplib.SMTP(config['smtp_server'], config['smtp_port'])
	server.starttls()
	server.login(config['smtp_auth_user'], config['smtp_auth_password'])
	msg="\r\n\r\n The Berkey is almost full! time: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\r\n\r\n"
	server.sendmail(config['berkey_alert_from'], config['berkey_alert_recipients'],msg)

	server.quit()

def blink_led(current_time, alert_time):
	is_on = GPIO.input(4) == 1
	state = 0 if is_on else 1
	GPIO.output(4, state)

def main():
	setup_io()
	config = get_config()

	is_in_water = False
	time_in_water = 0
	max_time_in_water = 1
	alert_time = 10

	while True:
		is_in_water = GPIO.input(18) == 1

		if is_in_water:
			time_in_water += 1
		else:
			GPIO.output(4, 0)
			time_in_water = 0
		
		if time_in_water == max_time_in_water:
			output_alert(time_in_water, alert_time)
			send_alert_email(config)
			berkeydb.log_fill()
		elif time_in_water > 0:
			output_alert(time_in_water, alert_time)

		time.sleep(1)

if __name__ == "__main__":
   main()