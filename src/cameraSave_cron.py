#!/usr/bin/env python3

from utils import captureNsave
import RPi.GPIO as GPIO
from time import sleep, time, localtime
import subprocess
from pathlib import Path

GPIO.setwarnings(False)    # Ignore warnings for now
GPIO.setmode(GPIO.BCM)     # Use GPIO pin numbering

# Declare Peripherals
LDR = 4 # LDR Connected Here

imageDirSD = '/home/pi/Pictures/'

# Function to check LDR Reading
def rc_time (pin_to_circuit):
    for i in range(5):
        count = 0
        
        #Output LOW on the pin for 0.1 seconds
        GPIO.setup(pin_to_circuit, GPIO.OUT)
        GPIO.output(pin_to_circuit, GPIO.LOW)
        sleep(0.1)
        
        #Change the pin back to input
        GPIO.setup(pin_to_circuit, GPIO.IN)
      
        #Count until the pin goes high
        while (GPIO.input(pin_to_circuit) == GPIO.LOW):
            count += 1
        sleep(0.1)
    
    return count/5

curr_time = localtime(time())
timeSTR = str(curr_time.tm_year)+'/' + \
          str(curr_time.tm_mon)+'/' + \
          str(curr_time.tm_mday)+' ' + \
          str(curr_time.tm_hour)+':' + \
          str(curr_time.tm_min)+':' + \
          str(curr_time.tm_sec)
fLogs = open("/home/pi/Desktop/WSIwork/logs", "a")
fLogs.write(timeSTR + " - Capture Begin...\n")
fLogs.close()

imagePath = imageDirSD + str(curr_time.tm_year)+'/' + \
            str(curr_time.tm_mon)+'/' + \
            str(curr_time.tm_mday)+'/'
hh = "{0:0=2d}".format(curr_time.tm_hour)
mm = "{0:0=2d}".format(curr_time.tm_min)
ss = "{0:0=2d}".format(curr_time.tm_sec)
Path(imagePath).mkdir(parents=True, exist_ok=True)
#if curr_time.tm_hour>=19 or curr_time.tm_hour<5:
rcTime = rc_time(LDR)
curr_time = localtime(time())
timeSTR = str(curr_time.tm_year)+'/' + \
          str(curr_time.tm_mon)+'/' + \
          str(curr_time.tm_mday)+' ' + \
          str(curr_time.tm_hour)+':' + \
          str(curr_time.tm_min)+':' + \
          str(curr_time.tm_sec)
fLogs = open("/home/pi/Desktop/WSIwork/logs", "a")
fLogs.write(timeSTR + " - Value of rcTime is " + str(rcTime) + "\n")
fLogs.close()
if rcTime>100:
    subprocess.call("raspistill -md 3 -drc high -ex night -ss 2500000 -o " +imagePath+hh+mm+ss+".png", shell=True)
elif rcTime<50:
    subprocess.call("raspistill -md 3 -o " +imagePath+hh+mm+ss+".png", shell=True)
else:
    subprocess.call("raspistill -md 3 -drc med -ex night -ss 1500000 -o " +imagePath+hh+mm+ss+".png", shell=True)
#captureNsave(imageDirSD)

curr_time = localtime(time())
timeSTR = str(curr_time.tm_year)+'/' + \
          str(curr_time.tm_mon)+'/' + \
          str(curr_time.tm_mday)+' ' + \
          str(curr_time.tm_hour)+':' + \
          str(curr_time.tm_min)+':' + \
          str(curr_time.tm_sec)
fLogs = open("/home/pi/Desktop/WSIwork/logs", "a")
fLogs.write(timeSTR + " - Capture and Save Completed\n")
fLogs.close()