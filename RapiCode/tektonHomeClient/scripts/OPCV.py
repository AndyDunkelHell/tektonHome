from picamera2 import Picamera2, MappedArray, Preview
import cv2
import time
import numpy as np
import requests
import scripts.ESP32Control as strip
import threading
import scripts.camSetup as cam

import os
import sys
# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)


from func_types import Button, Input


# Replace with the ESP32's IP address
esp_ip = 'http://192.168.0.163/'

# picam2 = Picamera2()
picam2 = None

#config = picam2.create_preview_configuration(main={"size": (480, 640)})
#picam2.configure(config)
live_ = False
# array = picam2.capture_array("main")

# print(array.shape)

Tile_dict = {'tile0': [0, 240, 0, 213], 'tile1': [0, 240, 213, 427], 'tile2': [0, 240, 427, 640], 'tile3': [240, 480, 427, 640], 'tile4': [240, 480, 213, 427], 'tile5': [240, 480, 0, 213]}


def create_hsv(color):
    # Convert the color to HSV
    color_hsv = cv2.cvtColor(np.uint8([[color]]), cv2.COLOR_BGR2HSV)[0][0]
    
    # Extract the hue, saturation, and value components
    hue = int(color_hsv[0])
    saturation = int(color_hsv[1])
    value = int(color_hsv[2])
    
    return (hue, saturation, value)


def create_rgb(color):
    red, green, blue = int(color[0]), int(color[1]), int(color[2])
    return (red, green, blue)


def tilesRGB(frame, Tile_dict = {}):
    k = 0
    tiles_rgb_values = []
    for tileCoord in Tile_dict.values():
        tile = frame[tileCoord[0]:tileCoord[1],tileCoord[2]:tileCoord[3]]

        img = tile
        height, width, _ = np.shape(img)
        #print(height, width)
        #print(img.shape)

        data = np.reshape(img, (height * width, 4))
        data = np.float32(data)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        flags = cv2.KMEANS_RANDOM_CENTERS
        compactness, labels, centers = cv2.kmeans(data, 1, None, criteria, 10, flags)
        #print(centers)

        rgb_values = []

        for index, row in enumerate(centers):
            rgb = create_rgb(row)
            rgb_values.append(rgb)

        tiles_rgb_values.append(rgb_values[0])
        #print(rgb_values)
        k+=1

    return tiles_rgb_values

def stop_sendData(type:Button = None):
    global live_
    live_ = True
    global picam2
    if picam2 == None:
        return 'INITIATE CAM FIRST!'
    else:
        return 'Ambient Live off executed successfully!'

def loop_sendData():
    last_data = None
    global picam2
    
    while True:
        
        global live_
        if live_:
            print("stop live_")
            live_ = False
            break
        start_time = time.time()
        array = picam2.capture_array("main")
        result = tilesRGB(array, Tile_dict)
        current_data = ""

        for x in result:
            str_x = str(x)
            current_data += str_x[1:-1] + ","
        strip.startLive_(current_data[:-1])
        # time.sleep((1/60))
        # print(current_data[:-1])

    cv2.waitKey(0)

def sendData(type:Button = None):
    t = threading.Thread(target=loop_sendData)
    t.start()
    global picam2
    if picam2 == None:
        return 'INITIATE CAM FIRST!'
    else:
        return 'Started Sending Data'

def initCam(type:Button = None):
    global picam2
    if picam2 == None:
        try:
            picam2 = Picamera2()
            picam2.start()
        except:
            return 'Error by initiating camera, please check connection'
        else:
            return 'CAMERA INITIATED! go to Setup Port :7123 to see setup cam preview'
    else:
        return 'Camera already initiated. Setup Port :7123'

def checkCam():
    global picam2
    if picam2 == None:
        return False
    else:
        return True

def fetchCam():
    global picam2
    return picam2



