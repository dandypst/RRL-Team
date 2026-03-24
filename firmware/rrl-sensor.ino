/**
 * RRL-Sensor Firmware
 * BOMBINO Gateway v2 - ESP32-S3
 * 
 * Track Circuit Sensor System for 100 Hectare Perimeter Monitoring
 * Location: Bombana, Sulawesi Tenggara
 * 
 * Features:
 * - 16 section track circuit monitoring
 * - WiFi + 4G connectivity
 * - GPS positioning
 * - Solar power management
 * - Real-time alerts
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// ============== CONFIGURATION ==============
// WiFi Settings
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// API Endpoint
const char* API_ENDPOINT = "https://your-api-endpoint.com/api/sensor-data";
const char* API_KEY = "YOUR_API_KEY";

// Timing
const unsigned long SENSOR_READ_INTERVAL = 100;      // 100ms
const unsigned long STATUS_REPORT_INTERVAL = 30000;  // 30 seconds
const unsigned long GPS_READ_INTERVAL = 5000;        // 5 seconds

// Pin Definitions (ESP32-S3)
#define NUM_SECTIONS 16
const int TC_PINS[NUM_SECTIONS] = {
  4, 5, 6, 7,      // Section 1-4
  15, 16, 17, 18,  // Section 5-8
  8, 3, 46, 9,     // Section 9-12
  10, 11, 12, 13   // Section 13-16
};

// GPS Serial
#define GPS_RX 44
#define GPS_TX 43
HardwareSerial gpsSerial(1);

// 4G Module (Quectel EC200U)
#define LTE_RX 1
#define LTE_TX 2
HardwareSerial lteSerial(2);

// Power Management
#define SOLAR_VOLTAGE_PIN 14
#define BATTERY_VOLTAGE_PIN 21
#define CHARGE_CURRENT_PIN 47

// Status LED
#define LED_STATUS 38
#define LED_ALERT 39

// ============== GLOBAL VARIABLES ==============
TinyGPSPlus gps;

struct SectionStatus {
  bool isOpen;      // true = circuit broken (alert!)
  bool lastState;
  unsigned long lastChangeTime;
  int alertCount;
};

SectionStatus sections[NUM_SECTIONS];

struct SystemStatus {
  float solarVoltage;
  float batteryVoltage;
  float chargeCurrent;
  int wifiRSSI;
  int lteSignal;
  bool gpsValid;
  double latitude;
  double longitude;
  unsigned long uptime;
};

SystemStatus sysStatus;

unsigned long lastSensorRead = 0;
unsigned long lastStatusReport = 0;
unsigned long lastGPSRead = 0;
unsigned long bootTime = 0;

bool alertActive = false;
unsigned long alertStartTime = 0;

// ============== SETUP ==============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("  RRL-SENSOR v1.0 - BOMBINO Gateway");
  Serial.println("  Track Circuit Perimeter System");
  Serial.println("========================================\n");
  
  // Initialize pins
  initPins();
  
  // Initialize GPS
  gpsSerial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  
  // Initialize 4G (optional)
  // lteSerial.begin(115200, SERIAL_8N1, LTE_RX, LTE_TX);
  
  // Initialize section status
  initSections();
  
  // Connect WiFi
  connectWiFi();
  
  // Record boot time
  bootTime = millis();
  
  Serial.println("[SETUP] System initialized successfully");
  Serial.println("[SETUP] Monitoring 16 track circuit sections\n");
}

// ============== MAIN LOOP ==============
void loop() {
  unsigned long currentMillis = millis();
  
  // Read GPS data
  if (currentMillis - lastGPSRead >= GPS_READ_INTERVAL) {
    readGPS();
    lastGPSRead = currentMillis;
  }
  
  // Read track circuit sensors
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    readSensors();
    lastSensorRead = currentMillis;
  }
  
  // Read power metrics
  readPowerMetrics();
  
  // Check and report status
  if (currentMillis - lastStatusReport >= STATUS_REPORT_INTERVAL) {
    checkAlerts();
    reportStatus();
    lastStatusReport = currentMillis;
  }
  
  // Handle alert LED
  handleAlertLED(currentMillis);
  
  // Feed GPS
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }
  
  delay(10);
}

// ============== FUNCTIONS ==============

void initPins() {
  // Initialize track circuit input pins
  for (int i = 0; i < NUM_SECTIONS; i++) {
    pinMode(TC_PINS[i], INPUT_PULLUP);
  }
  
  // Initialize analog pins
  pinMode(SOLAR_VOLTAGE_PIN, INPUT);
  pinMode(BATTERY_VOLTAGE_PIN, INPUT);
  pinMode(CHARGE_CURRENT_PIN, INPUT);
  
  // Initialize LEDs
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_ALERT, OUTPUT);
  digitalWrite(LED_STATUS, HIGH);
  digitalWrite(LED_ALERT, LOW);
}

void initSections() {
  for (int i = 0; i < NUM_SECTIONS; i++) {
    sections[i].isOpen = false;
    sections[i].lastState = false;
    sections[i].lastChangeTime = 0;
    sections[i].alertCount = 0;
  }
}

void connectWiFi() {
  Serial.print("[WIFI] Connecting to ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected!");
    Serial.print("[WIFI] IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WIFI] Failed to connect!");
  }
}

void readSensors() {
  bool anyChange = false;
  
  for (int i = 0; i < NUM_SECTIONS; i++) {
    // Read sensor (LOW = circuit closed/normal, HIGH = circuit open/alert)
    // Note: Adjust logic based on actual wiring
    bool currentState = digitalRead(TC_PINS[i]) == HIGH;
    
    if (currentState != sections[i].lastState) {
      sections[i].isOpen = currentState;
      sections[i].lastState = currentState;
      sections[i].lastChangeTime = millis();
      
      if (currentState) {
        sections[i].alertCount++;
        Serial.print("[ALERT] Section ");
        Serial.print(i + 1);
        Serial.println(" CIRCUIT BROKEN!");
      } else {
        Serial.print("[INFO] Section ");
        Serial.print(i + 1);
        Serial.println(" circuit restored");
      }
      
      anyChange = true;
    }
  }
  
  if (anyChange) {
    checkAlerts();
  }
}

void checkAlerts() {
  bool wasAlert = alertActive;
  alertActive = false;
  
  for (int i = 0; i < NUM_SECTIONS; i++) {
    if (sections[i].isOpen) {
      alertActive = true;
      break;
    }
  }
  
  if (alertActive && !wasAlert) {
    alertStartTime = millis();
    Serial.println("[ALERT] PERIMETER BREACH DETECTED!");
    sendImmediateAlert();
  }
}

void readGPS() {
  if (gps.location.isValid()) {
    sysStatus.gpsValid = true;
    sysStatus.latitude = gps.location.lat();
    sysStatus.longitude = gps.location.lng();
  } else {
    sysStatus.gpsValid = false;
  }
}

void readPowerMetrics() {
  // Read analog values and convert to voltage/current
  // Adjust multipliers based on actual voltage divider values
  int solarRaw = analogRead(SOLAR_VOLTAGE_PIN);
  int batteryRaw = analogRead(BATTERY_VOLTAGE_PIN);
  int currentRaw = analogRead(CHARGE_CURRENT_PIN);
  
  sysStatus.solarVoltage = solarRaw * (3.3 / 4095.0) * 5.0;  // Example multiplier
  sysStatus.batteryVoltage = batteryRaw * (3.3 / 4095.0) * 5.0;
  sysStatus.chargeCurrent = (currentRaw - 2048) * (3.3 / 4095.0) / 0.1;  // Example for shunt
  
  if (WiFi.status() == WL_CONNECTED) {
    sysStatus.wifiRSSI = WiFi.RSSI();
  } else {
    sysStatus.wifiRSSI = -100;
  }
  
  sysStatus.lteSignal = 0;  // TODO: Read from LTE module
  sysStatus.uptime = (millis() - bootTime) / 1000;
}

void handleAlertLED(unsigned long currentMillis) {
  if (alertActive) {
    // Fast blink when alert
    digitalWrite(LED_ALERT, (currentMillis / 200) % 2);
  } else {
    digitalWrite(LED_ALERT, LOW);
  }
  
  // Status LED - slow blink when normal
  digitalWrite(LED_STATUS, (currentMillis / 1000) % 2);
}

void reportStatus() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[ERROR] WiFi not connected, cannot report");
    return;
  }
  
  HTTPClient http;
  http.begin(API_ENDPOINT);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);
  
  // Build JSON payload
  StaticJsonDocument<2048> doc;
  
  doc["device_id"] = "BOMBINO-001";
  doc["timestamp"] = millis();
  doc["uptime"] = sysStatus.uptime;
  
  // Section status
  JsonArray sectionsArray = doc.createNestedArray("sections");
  for (int i = 0; i < NUM_SECTIONS; i++) {
    JsonObject section = sectionsArray.createNestedObject();
    section["id"] = i + 1;
    section["status"] = sections[i].isOpen ? "OPEN" : "CLOSED";
    section["alert_count"] = sections[i].alertCount;
  }
  
  // System status
  JsonObject system = doc.createNestedObject("system");
  system["solar_voltage"] = sysStatus.solarVoltage;
  system["battery_voltage"] = sysStatus.batteryVoltage;
  system["charge_current"] = sysStatus.chargeCurrent;
  system["wifi_rssi"] = sysStatus.wifiRSSI;
  system["lte_signal"] = sysStatus.lteSignal;
  
  // GPS
  JsonObject gpsObj = doc.createNestedObject("gps");
  gpsObj["valid"] = sysStatus.gpsValid;
  if (sysStatus.gpsValid) {
    gpsObj["lat"] = sysStatus.latitude;
    gpsObj["lng"] = sysStatus.longitude;
  }
  
  String payload;
  serializeJson(doc, payload);
  
  Serial.println("[HTTP] Sending status report...");
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
    Serial.printf("[HTTP] Response code: %d\n", httpCode);
    if (httpCode == HTTP_CODE_OK) {
      String response = http.getString();
      Serial.println("[HTTP] Report sent successfully");
    }
  } else {
    Serial.printf("[HTTP] Error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void sendImmediateAlert() {
  // Send immediate alert for perimeter breach
  HTTPClient http;
  http.begin(String(API_ENDPOINT) + "/alert");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);
  
  StaticJsonDocument<512> doc;
  doc["device_id"] = "BOMBINO-001";
  doc["alert_type"] = "PERIMETER_BREACH";
  doc["timestamp"] = millis();
  doc["priority"] = "HIGH";
  
  // List affected sections
  JsonArray affected = doc.createNestedArray("affected_sections");
  for (int i = 0; i < NUM_SECTIONS; i++) {
    if (sections[i].isOpen) {
      affected.add(i + 1);
    }
  }
  
  // GPS location
  if (sysStatus.gpsValid) {
    doc["latitude"] = sysStatus.latitude;
    doc["longitude"] = sysStatus.longitude;
  }
  
  String payload;
  serializeJson(doc, payload);
  
  Serial.println("[ALERT] Sending immediate breach notification...");
  int httpCode = http.POST(payload);
  
  if (httpCode == HTTP_CODE_OK) {
    Serial.println("[ALERT] Breach notification sent!");
  } else {
    Serial.printf("[ALERT] Failed to send: %d\n", httpCode);
  }
  
  http.end();
}
