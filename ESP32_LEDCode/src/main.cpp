#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_NeoPixel.h>
#include <AceRoutine.h>

using namespace ace_routine;

#define LED_PIN     5 // GPIO pin connected to the NeoPixels.
#define NUM_LEDS    95

static int rgbInts[18];

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// Replace with your network credentials
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_PASSWORD";

WebServer server(80);

// Function to set the whole strip to a specific color
void setColor(uint8_t red, uint8_t green, uint8_t blue) {
  int x = 0;
  for(int i = 0; i < 6; i++) {
    rgbInts[x + i]= red;
    rgbInts[x + i + 1]= green;
    rgbInts[x + i+ 2]= blue;
    x += 2;
  }
}

COROUTINE( setColorZone) {
  int zone0_0 = 0;
  int zone0_f = 13;
  COROUTINE_LOOP(){
    for(zone0_0; zone0_0 < zone0_f; zone0_0++) {

      strip.setPixelColor(zone0_0, strip.Color(rgbInts[0], rgbInts[1], rgbInts[2]));
      strip.setPixelColor(93-zone0_0, strip.Color(rgbInts[0], rgbInts[1], rgbInts[2]));

      strip.setPixelColor(zone0_0 + 13, strip.Color(rgbInts[3], rgbInts[4], rgbInts[5]));

      strip.setPixelColor(zone0_0 + 26, strip.Color(rgbInts[6], rgbInts[7], rgbInts[8]));

      strip.setPixelColor(zone0_0 + 41, strip.Color(rgbInts[9], rgbInts[10], rgbInts[11]));
      
      strip.setPixelColor(zone0_0 + 55, strip.Color(rgbInts[12], rgbInts[13], rgbInts[14]));

      strip.setPixelColor(zone0_0 + 68, strip.Color(rgbInts[15], rgbInts[16], rgbInts[17]));


    }
    strip.show();

    COROUTINE_DELAY(5);

  }


}

// Route for root / web page
void handleRoot() {
  server.send(200, "text/plain", "Hello from ESP32!");
}

void handleLEDOn() {
    // Set the whole strip to bright orange
  setColor(128, 0, 220);
  server.send(200, "text/plain", "LED is now ON");
}

void handleLEDOff() {
    // Set the whole strip to bright orange
  setColor(0, 0, 0);
  server.send(200, "text/plain", "LED is now OFF");
}

// Handler for the color change route
void handleChangeColor() {
  if(server.hasArg("r") && server.hasArg("g") && server.hasArg("b")) {
    int r = server.arg("r").toInt();
    int g = server.arg("g").toInt();
    int b = server.arg("b").toInt();
    setColor(r, g, b);
    server.send(200, "text/plain", "Color changed");
  } else {
    server.send(400, "text/plain", "Missing color parameters");
  }
}

void handleLive(){
  server.send(200, "text/plain", " ");
  if(server.hasArg("vals")){
        // Convert the String to a C-style string (char array)
    String data = server.arg("vals");
    
    char dataCharArray[95]; // Make sure this is large enough to hold your incoming data
    data.toCharArray(dataCharArray, 95);

    // Tokenize the char array based on comma delimiter
    char *token = strtok(dataCharArray, ",");
    int led_i = 0;
    while (token != NULL) {
      // Convert token to an integer
      int number = atoi(token);

      // Do something with the number
      
      if (led_i == 24){
        rgbInts[led_i]= number;
        led_i = 0;
      }else{
        rgbInts[led_i]= number;
        led_i += 1;
      }

      token = strtok(NULL, ",");
    }

  }

}

void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to the WiFi network");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "NeoPixel ESP32 Control");
  });

  // Route HTTP GET requests
  server.on("/", handleRoot);
  server.on("/on", handleLEDOn);
  server.on("/off", handleLEDOff);
  server.on("/change-color", handleChangeColor);
  server.on("/live", handleLive);

  // Additional routes for controlling the LED strip can be added here

  server.begin();
  CoroutineScheduler::setup();
}

void loop() {
  server.handleClient();
  CoroutineScheduler::loop();
}
