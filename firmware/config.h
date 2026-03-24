/**
 * RRL-Sensor Configuration Header
 * 
 * Edit this file before uploading to ESP32
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============== DEVICE CONFIGURATION ==============
#define DEVICE_ID "BOMBINO-001"
#define DEVICE_NAME "RRL-Sensor Gateway"
#define FIRMWARE_VERSION "1.0.0"

// ============== NETWORK CONFIGURATION ==============
// WiFi Credentials
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// WiFi Timeout (seconds)
#define WIFI_TIMEOUT 30

// ============== API CONFIGURATION ==============
// API Endpoint
#define API_ENDPOINT "https://your-api-endpoint.com/api/sensor-data"
#define API_ALERT_ENDPOINT "https://your-api-endpoint.com/api/alert"
#define API_KEY "YOUR_API_KEY_HERE"

// HTTP Timeout (milliseconds)
#define HTTP_TIMEOUT 10000

// ============== TIMING CONFIGURATION ==============
// Sensor reading interval (milliseconds)
#define SENSOR_READ_INTERVAL 100

// Status report interval (milliseconds)
#define STATUS_REPORT_INTERVAL 30000

// GPS reading interval (milliseconds)
#define GPS_READ_INTERVAL 5000

// Alert debounce time (milliseconds)
#define ALERT_DEBOUNCE_TIME 500

// ============== HARDWARE CONFIGURATION ==============
// Number of track circuit sections
#define NUM_SECTIONS 16

// Track circuit input pins
const uint8_t TC_PINS[NUM_SECTIONS] = {
  4, 5, 6, 7,      // Section 1-4
  15, 16, 17, 18,  // Section 5-8
  8, 3, 46, 9,     // Section 9-12
  10, 11, 12, 13   // Section 13-16
};

// GPS Serial pins
#define GPS_RX_PIN 44
#define GPS_TX_PIN 43
#define GPS_BAUDRATE 9600

// 4G LTE Module pins
#define LTE_RX_PIN 1
#define LTE_TX_PIN 2
#define LTE_BAUDRATE 115200

// Analog input pins
#define SOLAR_VOLTAGE_PIN 14
#define BATTERY_VOLTAGE_PIN 21
#define CHARGE_CURRENT_PIN 47

// LED pins
#define LED_STATUS_PIN 38
#define LED_ALERT_PIN 39

// ============== CALIBRATION ==============
// Voltage divider multipliers
#define SOLAR_VOLTAGE_MULTIPLIER 5.0
#define BATTERY_VOLTAGE_MULTIPLIER 5.0
#define CURRENT_SHUNT_RESISTANCE 0.1

// ADC reference voltage
#define ADC_REFERENCE 3.3
#define ADC_RESOLUTION 4095.0

// ============== ALERT CONFIGURATION ==============
// Enable immediate alert on breach
#define ENABLE_IMMEDIATE_ALERT true

// Alert cooldown time (milliseconds)
#define ALERT_COOLDOWN 60000

// ============== DEBUG CONFIGURATION ==============
// Enable serial debug output
#define DEBUG true

// Debug baudrate
#define DEBUG_BAUDRATE 115200

#endif // CONFIG_H
