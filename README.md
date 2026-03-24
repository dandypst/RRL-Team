# RRL-Sensor

Track Circuit Sensor System untuk monitoring perimeter 100 hektar di Bombana, Sulawesi Tenggara.

## Overview

Sistem keamanan perimeter menggunakan track circuit detection dengan 16 section untuk mengcover 100 hektar lahan.

## Hardware

### BOMBINO Gateway v2
- **MCU:** ESP32-S3 (dual core, WiFi + BT 5.0)
- **Inputs:** 16x Digital (expandable to 32)
- **Communications:**
  - WiFi 802.11 b/g/n
  - 4G LTE (Quectel EC200U)
  - LoRa 915MHz (optional backup)
- **GPS:** u-blox NEO-M8N
- **Power:** Solar 50W + LiFePO4 12V 20Ah
- **Enclosure:** IP67 anti-tamper

### Track Circuit Module
- Detection: 5V DC current sensing
- Range: 250m per section
- Response time: <100ms
- Isolation: Optocoupler + fuse protection

## Layout

```
1000m x 1000m (100 hektar)
┌────┬────┬────┬────┐
│ 1  │ 2  │ 3  │ 4  │
├────┼────┼────┼────┤
│ 5  │ 6  │ 7  │ 8  │
├────┼────┼────┼────┤
│ 9  │ 10 │ 11 │ 12 │
├────┼────┼────┼────┤
│ 13 │ 14 │ 15 │ 16 │
└────┴────┴────┴────┘
```

Per section: 250m x 250m = 6.25 hektar

## Firmware

See `firmware/` directory for ESP32 code.

## Dashboard

Streamlit-based dashboard for monitoring.

## Documentation

- `docs/hardware-design.md` - Detailed hardware specs
- `docs/installation-guide.md` - Installation procedures
- `docs/api-reference.md` - API documentation

## License

MIT License - RRL-Team 2024
