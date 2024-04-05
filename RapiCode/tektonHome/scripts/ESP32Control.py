import requests

# Replace with the ESP32's IP address
esp_ip = 'http://192.168.0.104/'

def turn_led_on():
    response = requests.get(esp_ip + 'on')
    print(response.text)

def turn_led_off():
    response = requests.get(esp_ip + 'off')
    print(response.text)

def change_color(red = 0, green = 0, blue = 0):
    params = {'r': red, 'g': green, 'b': blue}
    response = requests.get(esp_ip + 'change-color', params=params)
    print(response.text)


# Example usage
#turn_led_on()
# Wait or do other stuff
#turn_led_off()
#change_color(255, 50, 3)
