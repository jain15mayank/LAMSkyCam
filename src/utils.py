#!/usr/bin/env python3

import subprocess
import numpy as np
import picamera.array
from time import sleep, time, localtime
from pathlib import Path
from PIL import Image

def captureImageAsNumpyArray(resolution = (2592, 1944), shutterSpeed = 0):
    """
    Captures images from Raspberry Pi Camera module and returns a Numpy Array
    ----------
    Params:
        resolution: tuple(int, int); Maximum: (2592, 1944)
            - resoulution of the image which is to be captured
    Output:
        imgArray: ndArray of shape (resolution[0], resolution[1], 3)
    """
    if resolution[0]>2592 or resolution[1]>1944:
        raise ValueError('Specified resolution is beyond the capabilities of Raspberry Pi HQ Camera')
    elif resolution[0]<64 or resolution[1]<64:
        raise ValueError('Specified resolution is less than the minimum permitted resolution of 64X64')
    # Begin capturing image
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.shutter_speed = shutterSpeed
        with picamera.array.PiRGBArray(camera, size=resolution) as output:
            sleep(3) # Sleep before capture to allow camera to adjust itself
            camera.capture(output, 'rgb', resize=resolution)
            sleep(3) # Sleep after capture to allow camera to adjust itself
            # print(output.array.shape)
            imgArray = output.array.astype(np.uint8)
            # imgArray = np.swapaxes(output.array, 0, 1).astype(np.uint8)
    return imgArray

def checkHDDstatus(diskLabel):
    """
    Check if the external hard disk is attached to the system
    ----------
    Params:
        diskLabel: string
            - label/name of the hard disk
    Output:
        status: boolean
            - True: if attached and active
            - False: if not attached/active
    """
    # Substitute any spaces in the disk label/name by special character
    processedLabel = diskLabel.replace(' ', '\\\\040')
    # Check if hard disk is attached - 0 if it is - 1 otherwise
    status = subprocess.call("grep -qs '/media/pi/" + processedLabel + "' /proc/mounts", shell=True)
    return not bool(status)

def SD2HD(pathSD, pathHD):
    """
    Moves all the images from pathSD to pathHD while preserving the
    sub-directory architecture. Further removes all sub-directories and
    files from pathSD
    ----------
    Params:
        pathSD: string
            - Path in SD where images were stored (Source)
        pathHD: string
            - Path in HD where images needs to be moved (Destination)
    Output:
        status: boolean
            - True: if operation completed successfully
            - False: otherwise
    """
    # Substitute any spaces in the paths by special character
    pathSD = pathSD.replace(' ', '\\ ')
    pathHD = pathHD.replace(' ', '\\ ')
    
    subprocess.call("rsync -aqr --remove-source-files "+pathSD+" "+pathHD, shell=True)
    subprocess.call("find "+pathSD+" -type d -empty -delete", shell=True)

def captureNsave(path, pathSD=None):
    """
    Captures and saves the image to the specified directory. Folder path
    corresponding to Year, Month, Date will be added in this routine
    itself. The routine will also check and create (if required) the
    directories encountered in the final imagePath.
    ----------
    Params:
        path: string
            - path of directory where image needs to be saved
        pathSD: string
            - alternate path of directory where image can be saved if
              original path fails
            - If None, print error + don't save + continue (on fail)
    Output:
        altSave: boolean
            - True: if operation completed successfully in alternate path
            - False: otherwise
    """
    curr_time = localtime(time())
    if curr_time.tm_hour>19 or curr_time.tm_hour<5:
        shutter_speed = 10000000
    else:
        shutter_speed = 0
    imageArray = captureImageAsNumpyArray(shutterSpeed = shutter_speed)
    im = Image.fromarray(imageArray)
    imagePath = path + str(curr_time.tm_year)+'/' + \
                str(curr_time.tm_mon)+'/' + str(curr_time.tm_mday)+'/'
    hh = "{0:0=2d}".format(curr_time.tm_hour)
    mm = "{0:0=2d}".format(curr_time.tm_min)
    ss = "{0:0=2d}".format(curr_time.tm_sec)
    try:
        Path(imagePath).mkdir(parents=True, exist_ok=True)
        im.save(imagePath+hh+mm+ss+".png")
        altSave = False
    except:
        if pathSD is not None:
            imagePath = pathSD + str(curr_time.tm_year)+'/' + \
                str(curr_time.tm_mon)+'/' + str(curr_time.tm_mday)+'/'
            # Check the path; make directory if does not exist
            Path(imagePath).mkdir(parents=True, exist_ok=True)
            im.save(imagePath+hh+mm+ss+".png")
            altSave = True
        else:
            print("Error in writing to the specified path. No alternate path specified. Skipping save!")
            altSave = False
    return altSave