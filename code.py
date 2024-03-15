#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Halloween").sheet1

# Sleep times
SleepTimeS = 0.2
SleepTimeL = 0.5

# Control pins for motors
ControlPins = {
    1: [5, 6, 13, 19],
    2: [4, 21, 17, 27],
    3: [22, 23, 24, 25],
    4: [14, 15, 8, 7]
}

# Setup control pins
for pins in ControlPins.values():
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

# Stepper motor sequences
seq1 = [[1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0],
        [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1]]
seq2 = [[1, 0, 0, 1], [0, 0, 0, 1], [0, 0, 1, 1], [0, 0, 1, 0],
        [0, 1, 1, 0], [0, 1, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0]]

# Candy dispensing function
def dispense_candy(input_pin, motor_pins, seq1, seq2, candy_name):
    now_format = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    GPIO.setup(input_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    input_state = GPIO.input(input_pin)
    if input_state == False:
        insertRow = [now_format, candy_name] + [1 if pin == input_pin else 0 for pin in [12, 26, 16, 1]]
        sheet.insert_row(insertRow, 2)
        print(candy_name)
        for i, seq in [(588, seq1), (258, seq2)]:
            for _ in range(i):
                for halfstep in range(8):
                    for pin in range(4):
                        GPIO.output(motor_pins[pin], seq[halfstep][pin])
                    time.sleep(0.001)
        time.sleep(0.1)

# Main loop
try:
    while True:
        for input_pin, motor_num, candy_name in [(12, 2, "dots"), (26, 1, "kitkat"), (16, 3, "nerds"), (1, 4, "twix")]:
            dispense_candy(input_pin, ControlPins[motor_num], seq1, seq2, candy_name)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Done")
