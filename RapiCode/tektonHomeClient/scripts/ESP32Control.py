import requests
import threading
# import base.func_types 
import sys
import os
import shlex
# Get the parent directory
parent_dir = os.path.dirname(os.path.realpath(__file__))

# Add the parent directory to sys.path
sys.path.append(parent_dir)


from func_types import Button, Input


# Replace with the ESP32's IP address
esp_ip = 'http://192.168.0.104/'

def turn_led_on(type:Button = None):
    response = requests.get(esp_ip + 'on')
    print(response.text)
    return 'Turn on executed successfully!'

def turn_led_off(type:Button = None):
    response = requests.get(esp_ip + 'off')
    print(response.text)
    return 'Turn off executed successfully!'

def change_color(type:Input = None, param_vals = ""):
    try:
        RGBval_list = shlex.split(param_vals)
        params = {'r': RGBval_list[0], 'g': RGBval_list[1], 'b': RGBval_list[2]}
        response = requests.get(esp_ip + 'change-color', params=params)
        print(response.text)
        return "Changed Color Succesfully to: " + param_vals
    except:
        return "Wrong Input: " + param_vals

def liveView(rgbValues = None):
        params = {'vals': rgbValues}
        response = requests.get(esp_ip + 'live', params=params)
        # print(response)

def startLive_(rgbValues):
    t = threading.Thread(target=liveView, args=(rgbValues,))
    t.start()

# Example usage
#turn_led_on()
# Wait or do other stuff
#turn_led_off()
#change_color(255, 50, 3)
