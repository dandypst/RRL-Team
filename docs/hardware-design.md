# BOMBINO Gateway v2 - Hardware Design

## Overview
ESP32-S3 based gateway for track circuit perimeter monitoring system.

## Specifications

### Microcontroller
- **Model:** ESP32-S3-WROOM-1
- **Cores:** Dual-core Xtensa LX7 @ 240MHz
- **RAM:** 512KB SRAM + 8MB PSRAM
- **Flash:** 16MB
- **WiFi:** 802.11 b/g/n, 2.4GHz
- **Bluetooth:** 5.0 (LE + Classic)

### Inputs
- 16x Digital inputs (3.3V logic, internal pull-up)
- 3x Analog inputs (12-bit ADC)
  - Solar voltage
  - Battery voltage
  - Charge current

### Communications
- **WiFi:** Onboard
- **4G LTE:** Quectel EC200U (via UART)
- **LoRa:** Optional SX1276 module (915MHz)
- **GPS:** u-blox NEO-M8N (UART)

### Power
- **Input:** 12V DC (solar/battery)
- **Regulation:** 
  - Buck 12V→5V (10A) for track circuits
  - Buck 12V→3.3V (2A) for MCU
- **Protection:** Reverse polarity, overvoltage, undervoltage

### Physical
- **Enclosure:** IP67 polycarbonate
- **Dimensions:** 200mm x 150mm x 80mm
- **Mounting:** Pole/wall mount
- **Connectors:** Waterproof M12

## Pinout

### ESP32-S3 GPIO Assignment

| GPIO | Function | Description |
|------|----------|-------------|
| 4 | TC_1 | Track circuit section 1 |
| 5 | TC_2 | Track circuit section 2 |
| 6 | TC_3 | Track circuit section 3 |
| 7 | TC_4 | Track circuit section 4 |
| 15 | TC_5 | Track circuit section 5 |
| 16 | TC_6 | Track circuit section 6 |
| 17 | TC_7 | Track circuit section 7 |
| 18 | TC_8 | Track circuit section 8 |
| 8 | TC_9 | Track circuit section 9 |
| 3 | TC_10 | Track circuit section 10 |
| 46 | TC_11 | Track circuit section 11 |
| 9 | TC_12 | Track circuit section 12 |
| 10 | TC_13 | Track circuit section 13 |
| 11 | TC_14 | Track circuit section 14 |
| 12 | TC_15 | Track circuit section 15 |
| 13 | TC_16 | Track circuit section 16 |
| 44 | GPS_RX | GPS UART RX |
| 43 | GPS_TX | GPS UART TX |
| 1 | LTE_RX | 4G module UART RX |
| 2 | LTE_TX | 4G module UART TX |
| 14 | SOLAR_V | Solar voltage (ADC) |
| 21 | BATT_V | Battery voltage (ADC) |
| 47 | CHG_I | Charge current (ADC) |
| 38 | LED_STATUS | Status LED |
| 39 | LED_ALERT | Alert LED |

## Schematic

### Track Circuit Input (per channel)
```
TC_WIRE ──┬──[FUSE 500mA]──┬──[R1 100Ω]──┬──[LED]──┐
          │                │             │         │
          │               [C1 100nF]     │         │
          │                │             │         │
         GND              GND           GND    ESP32_GPIO
                                            (with pull-up)
```

### Power Supply
```
SOLAR PANEL (50W, 18V)
         │
         ▼
    ┌─────────┐
    │  MPPT   │─── 14.4V ───┬──► BATTERY (12V 20Ah LiFePO4)
    │CONTROLLER│             │
    └─────────┘              ├──► BUCK 12V→5V (10A) ──► TC POWER
                             │
                             └──► BUCK 12V→3.3V (2A) ──► MCU
```

## Bill of Materials

| Item | Qty | Part Number | Est. Price (IDR) |
|------|-----|-------------|------------------|
| ESP32-S3-WROOM-1 | 1 | - | 150,000 |
| Quectel EC200U | 1 | - | 400,000 |
| u-blox NEO-M8N | 1 | - | 250,000 |
| Buck Converter 12V→5V 10A | 1 | - | 150,000 |
| Buck Converter 12V→3.3V 2A | 1 | - | 50,000 |
| Solar Panel 50W | 1 | - | 750,000 |
| Battery LiFePO4 12V 20Ah | 1 | - | 1,500,000 |
| MPPT Controller 10A | 1 | - | 300,000 |
| Enclosure IP67 | 1 | - | 400,000 |
| PCB + Components | 1 | - | 500,000 |
| Cables & Connectors | 1 set | - | 300,000 |
| **TOTAL** | | | **~4,750,000** |

## Installation

### Site Requirements
- Clear view to sky (for GPS & solar)
- Within cellular coverage
- Secure mounting point

### Wiring
1. Install perimeter wire (AWG 18) for all 16 sections
2. Connect TC wires to terminal blocks
3. Install solar panel facing north (optimal for Indonesia)
4. Connect battery
5. Power on and configure

### Configuration
1. Connect to WiFi AP "BOMBINO-SETUP"
2. Open browser to 192.168.4.1
3. Configure WiFi credentials
4. Set API endpoint
5. Test all sections

## Safety Notes
- Always disconnect battery before servicing
- Use appropriate PPE when working with electrical systems
- Ensure proper grounding
- Follow local electrical codes
