#!/usr/bin/env python3

import os
import subprocess
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from time import time, localtime, sleep
from utils import checkHDDstatus
from utils import SD2HD

# Determine the PID of current process
pid = str(os.getpid())
# Define path to the pidfile
pidfile = '/tmp/WSI_HDD_daemon.pid'
# Write the PID to that file
f = open(pidfile, "w")
f.write(pid)
f.close()

# Label/Name of the Hard disk where final data will be stored
HDlabel = 'Seagate Expansion Drive'

# Path where images will be stored
imageDirHD = '/media/pi/'+HDlabel+'/Mayank/WSI/images/'
imageDirSD = '/home/pi/Pictures/'

logsHDDpath = '/home/pi/Desktop/WSIwork/HDDlogs'

log_time = localtime(time())
timeSTR = str(log_time.tm_year)+'/' + \
          str(log_time.tm_mon)+'/' + \
          str(log_time.tm_mday)+' ' + \
          str(log_time.tm_hour)+':' + \
          str(log_time.tm_min)+':' + \
          str(log_time.tm_sec)
logsHDD = open(logsHDDpath, 'a')
logsHDD.write(timeSTR + " - HDD File started with PID: " + pid + "\n")
logsHDD.close()

GPIO.setwarnings(False)    # Ignore warnings for now
GPIO.setmode(GPIO.BCM)     # Use GPIO pin numbering

# Declare Peripherals
LED1 = 22 # Button Press Detected
LED2 = 23 # Removing Hard Disk Completed
LED3 = 24 # Hard Disk detected Once Again
LED4 = 25 # Writing data to disk - notification LED
PBut = 27

# Set all LEDs to OUTPUT and initialize to LOW
GPIO.setup(LED1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED4, GPIO.OUT, initial=GPIO.LOW)
# Set Push Button to INPUT
GPIO.setup(PBut, GPIO.IN)

# Define Unmount Flag :: True = HDD unmounted; False = HDD mounted
if checkHDDstatus(HDlabel): # HDD is mounted
    isUnmounted = False
    log_time = localtime(time())
    timeSTR = str(log_time.tm_year)+'/' + \
              str(log_time.tm_mon)+'/' + \
              str(log_time.tm_mday)+' ' + \
              str(log_time.tm_hour)+':' + \
              str(log_time.tm_min)+':' + \
              str(log_time.tm_sec)
    logsHDD = open(logsHDDpath, 'a')
    logsHDD.write(timeSTR + " - HDD is detected INITIALLY!\n")
    logsHDD.close()
else:
    isUnmounted = True
    log_time = localtime(time())
    timeSTR = str(log_time.tm_year)+'/' + \
              str(log_time.tm_mon)+'/' + \
              str(log_time.tm_mday)+' ' + \
              str(log_time.tm_hour)+':' + \
              str(log_time.tm_min)+':' + \
              str(log_time.tm_sec)
    logsHDD = open(logsHDDpath, 'a')
    logsHDD.write(timeSTR + " - HDD is NOT detected INITIALLY!\n")
    logsHDD.close()

# Define Callback for Push Button Interrupt
def button_pressed(channel):
    global isUnmounted
    print('Button Pressed!!')
    log_time = localtime(time())
    timeSTR = str(log_time.tm_year)+'/' + \
              str(log_time.tm_mon)+'/' + \
              str(log_time.tm_mday)+' ' + \
              str(log_time.tm_hour)+':' + \
              str(log_time.tm_min)+':' + \
              str(log_time.tm_sec)
    logsHDD = open(logsHDDpath, 'a')
    logsHDD.write(timeSTR + " - Button Press Detected\n")
    logsHDD.close()
    # Turn on to indicate detection button press
    GPIO.output(LED1, GPIO.HIGH)
    if checkHDDstatus(HDlabel): # HDD is mounted
        subprocess.call("sudo umount -t fuseblk /dev/sda1", shell=True)
        isUnmounted = True
        # Turn on to indicate successful unmount
        GPIO.output(LED2, GPIO.HIGH)
        sleep(5)
        GPIO.output(LED2, GPIO.LOW)
        sleep(1)
    GPIO.output(LED1, GPIO.LOW)
    log_time = localtime(time())
    timeSTR = str(log_time.tm_year)+'/' + \
              str(log_time.tm_mon)+'/' + \
              str(log_time.tm_mday)+' ' + \
              str(log_time.tm_hour)+':' + \
              str(log_time.tm_min)+':' + \
              str(log_time.tm_sec)
    logsHDD = open(logsHDDpath, 'a')
    logsHDD.write(timeSTR + " - HDD Unmounting routine successful!\n")
    logsHDD.close()

# Define event of pressing Push Button as Interrupt (debounce time in ms)
GPIO.add_event_detect(PBut, GPIO.RISING,\
                      callback = button_pressed, bouncetime = 10000)

# Main Code Statrts Here
prevHr = localtime(time()).tm_hour
while True: # Run Forever
    currHr = localtime(time()).tm_hour
    if (not currHr == prevHr) and (currHr == 0 or currHr==12) and (not isUnmounted):
        log_time = localtime(time())
        timeSTR = str(log_time.tm_year)+'/' + \
                  str(log_time.tm_mon)+'/' + \
                  str(log_time.tm_mday)+' ' + \
                  str(log_time.tm_hour)+':' + \
                  str(log_time.tm_min)+':' + \
                  str(log_time.tm_sec)
        logsHDD = open(logsHDDpath, 'a')
        logsHDD.write(timeSTR + " - Conditions for Writing Data MET - Writing to HDD...\n")
        logsHDD.close()
        # Begin transferring data to HDD
        GPIO.output(LED4, GPIO.HIGH)
        SD2HD(imageDirSD, imageDirHD)
        GPIO.output(LED4, GPIO.LOW)
        # End transferring data to HDD
        log_time = localtime(time())
        timeSTR = str(log_time.tm_year)+'/' + \
                  str(log_time.tm_mon)+'/' + \
                  str(log_time.tm_mday)+' ' + \
                  str(log_time.tm_hour)+':' + \
                  str(log_time.tm_min)+':' + \
                  str(log_time.tm_sec)
        logsHDD = open(logsHDDpath, 'a')
        logsHDD.write(timeSTR + " - Writing to HDD successful!\n")
        logsHDD.close()
        prevHr = currHr
    else:
        temp = localtime(time()).tm_hour
        if not (temp==0 or temp==12):
            prevHr = temp
        if checkHDDstatus(HDlabel) and isUnmounted:
            log_time = localtime(time())
            timeSTR = str(log_time.tm_year)+'/' + \
                      str(log_time.tm_mon)+'/' + \
                      str(log_time.tm_mday)+' ' + \
                      str(log_time.tm_hour)+':' + \
                      str(log_time.tm_min)+':' + \
                      str(log_time.tm_sec)
            logsHDD = open(logsHDDpath, 'a')
            logsHDD.write(timeSTR + " - HDD Redected!\n")
            logsHDD.close()
            isUnmounted = False
            # Turn on LED3 for 5 seconds to indicate HDD detection
            GPIO.output(LED3, GPIO.HIGH)
            sleep(5)
            GPIO.output(LED3, GPIO.LOW)