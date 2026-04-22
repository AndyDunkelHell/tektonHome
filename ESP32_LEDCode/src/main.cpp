#include <WiFi.h>
#include <WiFiUdp.h>
#include <PubSubClient.h>
#include <Adafruit_NeoPixel.h>
#include <string.h>
#include <stdlib.h>

// =====================
// CONFIG (EDIT)
// =====================
const char* WIFI_SSID = "<WIFI_SSID>";
const char* WIFI_PASS = "<WIFI_PASSWORD>";

const char* MQTT_HOST = "<MQTT_HOST_IP>";  // camera Pi running mosquitto
const uint16_t MQTT_PORT = 1883;

const uint16_t UDP_PORT = 7777;

// Match your old main.cpp
#define LED_PIN   5
#define NUM_LEDS  95
#define NUM_TILES 8
Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// =====================
// STATE
// =====================
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
WiFiUDP udp;

volatile bool power_on = false;
volatile bool mode_live = false;   // false=SOLID, true=LIVE
volatile uint8_t brightness = 180;

// default purple (same as your old default)
volatile uint8_t solid_r = 128, solid_g = 0, solid_b = 220;

// 8 tiles x RGB (r,g,b)
uint8_t tiles[NUM_TILES][3] = {0};

// How many LEDs per tile segment (must sum to NUM_LEDS = 95)
// Adjust this array to match your physical strip layout.
// Order: tile0 through tile7 going around the TV perimeter.
const int segs[NUM_TILES] = {12, 12, 12, 12, 12, 12, 12, 11};

// mark when we need to re-render
volatile bool dirty = true;
uint32_t last_render_ms = 0;

// =====================
// HELPERS
// =====================
static inline uint8_t clamp8(int v) {
  if (v < 0) return 0;
  if (v > 255) return 255;
  return (uint8_t)v;
}

// scale 0..255 by brightness 0..255 without floats
static inline uint8_t scale8(uint8_t v, uint8_t b) {
  return (uint16_t(v) * uint16_t(b) + 127) / 255;
}

// very small JSON-ish parser: looks for "r":, "g":, "b":
static int find_key(const char* s, const char* key) {
  const char* p = strstr(s, key);
  return p ? int(p - s) : -1;
}
static int parse_int_after_colon(const char* s, int start) {
  const char* p = s + start;
  p = strchr(p, ':');
  if (!p) return 0;
  p++;
  while (*p == ' ' || *p == '\t') p++;
  return strtol(p, nullptr, 10);
}

static const char* wlStatusName(wl_status_t s) {
  switch (s) {
    case WL_IDLE_STATUS:     return "IDLE";
    case WL_NO_SSID_AVAIL:   return "NO_SSID";
    case WL_SCAN_COMPLETED:  return "SCAN_DONE";
    case WL_CONNECTED:       return "CONNECTED";
    case WL_CONNECT_FAILED:  return "CONNECT_FAILED";
    case WL_CONNECTION_LOST: return "CONNECTION_LOST";
    case WL_DISCONNECTED:    return "DISCONNECTED";
    default:                 return "UNKNOWN";
  }
}

// =====================
// RENDER
// =====================
void renderNow() {
  if (!power_on) {
    for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, 0, 0, 0);
    strip.show();
    return;
  }

  uint8_t b = brightness;

  if (!mode_live) {
    uint8_t r  = scale8((uint8_t)solid_r, b);
    uint8_t g  = scale8((uint8_t)solid_g, b);
    uint8_t bl = scale8((uint8_t)solid_b, b);
    for (int i = 0; i < NUM_LEDS; i++) strip.setPixelColor(i, r, g, bl);
    strip.show();
    return;
  }

  // LIVE: 8 tiles mapped evenly across 95 LEDs
  int led = 0;
  for (int t = 0; t < NUM_TILES; t++) {
    uint8_t r  = scale8(tiles[t][0], b);
    uint8_t g  = scale8(tiles[t][1], b);
    uint8_t bl = scale8(tiles[t][2], b);
    for (int j = 0; j < segs[t]; j++) {
      strip.setPixelColor(led++, r, g, bl);
    }
  }

  strip.show();
}

// =====================
// MQTT CALLBACK (NO String, bounded buffers)
// =====================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  static char msg[200];
  unsigned int n = (length < sizeof(msg) - 1) ? length : (sizeof(msg) - 1);
  memcpy(msg, payload, n);
  msg[n] = '\0';

  // power
  if (strcmp(topic, "led/cmd/power") == 0) {
    if (strcasecmp(msg, "ON") == 0)  power_on = true;
    if (strcasecmp(msg, "OFF") == 0) power_on = false;
    dirty = true;
    return;
  }

  // mode
  if (strcmp(topic, "led/cmd/mode") == 0) {
    if (strcasecmp(msg, "LIVE") == 0)  mode_live = true;
    if (strcasecmp(msg, "SOLID") == 0) mode_live = false;
    dirty = true;
    return;
  }

  // brightness
  if (strcmp(topic, "led/cmd/brightness") == 0) {
    brightness = clamp8(atoi(msg));
    dirty = true;
    return;
  }

  // color JSON {"r":..,"g":..,"b":..}
  if (strcmp(topic, "led/cmd/color") == 0) {
    int ir = find_key(msg, "\"r\"");
    int ig = find_key(msg, "\"g\"");
    int ib = find_key(msg, "\"b\"");
    if (ir >= 0) solid_r = clamp8(parse_int_after_colon(msg, ir));
    if (ig >= 0) solid_g = clamp8(parse_int_after_colon(msg, ig));
    if (ib >= 0) solid_b = clamp8(parse_int_after_colon(msg, ib));
    dirty = true;
    return;
  }
}

// =====================
// CONNECTIVITY (FIXED)
// =====================
void startWiFiOnce() {
  Serial.printf("WiFi: starting STA, SSID=%s\n", WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);          // IMPORTANT: avoids lots of flaky behavior
  WiFi.setAutoReconnect(true);
  WiFi.persistent(false);        // avoid flash writes
  WiFi.disconnect(true, true);   // clear stale state
  delay(250);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
}

void ensureWiFi() {
  static uint32_t last_try = 0;

  if (WiFi.status() == WL_CONNECTED) return;

  uint32_t now = millis();
  if (now - last_try < 10000) return; // retry every 10s max
  last_try = now;

  Serial.printf("WiFi: not connected status=%d(%s) RSSI=%d -> retry begin()\n",
                (int)WiFi.status(), wlStatusName(WiFi.status()), WiFi.RSSI());

  WiFi.begin(WIFI_SSID, WIFI_PASS);
}

void ensureMQTT() {
  static uint32_t last_try = 0;

  if (mqtt.connected()) return;
  if (WiFi.status() != WL_CONNECTED) return;

  uint32_t now = millis();
  if (now - last_try < 2000) return;  // retry every 2s max
  last_try = now;

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
  mqtt.setBufferSize(256);

  char clientId[64];
  uint32_t mac = (uint32_t)ESP.getEfuseMac();
  snprintf(clientId, sizeof(clientId), "esp32_tvled_%08lx", (unsigned long)mac);

  Serial.printf("MQTT: connecting to %s:%u ...\n", MQTT_HOST, MQTT_PORT);
  if (mqtt.connect(clientId)) {
    Serial.println("MQTT: connected, subscribe led/cmd/#");
    mqtt.subscribe("led/cmd/#");
  } else {
    Serial.printf("MQTT: connect failed state=%d\n", mqtt.state());
  }
}

// =====================
// UDP LIVE (8 tiles = 24 bytes)
// =====================
void pollUDP() {
  int sz = udp.parsePacket();
  if (sz <= 0) return;

  uint8_t buf[NUM_TILES * 3];  // 24 bytes
  int n = udp.read(buf, sizeof(buf));
  if (n != NUM_TILES * 3) return;

  for (int i = 0; i < NUM_TILES; i++) {
    tiles[i][0] = buf[i * 3 + 0];
    tiles[i][1] = buf[i * 3 + 1];
    tiles[i][2] = buf[i * 3 + 2];
  }

  if (power_on && mode_live) dirty = true;
}

// =====================
// SETUP / LOOP
// =====================
void setup() {
  Serial.begin(115200);
  delay(200);

  strip.begin();
  strip.show();  // clear

  // Start WiFi once, then only periodic retries in loop
  startWiFiOnce();

  // UDP listen
  udp.begin(UDP_PORT);
  Serial.printf("UDP: listening on %u\n", UDP_PORT);

  // MQTT will connect once WiFi is up
  ensureMQTT();

  power_on = false;
  mode_live = false;
  dirty = true;
}

void loop() {
  ensureWiFi();
  ensureMQTT();

  // keep MQTT alive
  mqtt.loop();

  // handle UDP tiles
  pollUDP();

  // render only when needed, max ~100 fps
  uint32_t now = millis();
  if (dirty && (now - last_render_ms) >= 10) {
    dirty = false;
    last_render_ms = now;
    renderNow();
  }

  // heartbeat every ~5s (helps debugging)
  static uint32_t last_hb = 0;
  if (now - last_hb >= 5000) {
    last_hb = now;
    Serial.printf("HB: wifi=%d(%s) ip=%s rssi=%d | mqtt=%s | power=%s mode=%s bright=%u solid=(%u,%u,%u)\n",
      (int)WiFi.status(), wlStatusName(WiFi.status()),
      (WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString().c_str() : "-"),
      WiFi.RSSI(),
      (mqtt.connected() ? "OK" : "DOWN"),
      (power_on ? "ON" : "OFF"),
      (mode_live ? "LIVE" : "SOLID"),
      brightness,
      (uint8_t)solid_r, (uint8_t)solid_g, (uint8_t)solid_b
    );
  }

  delay(5);
}
