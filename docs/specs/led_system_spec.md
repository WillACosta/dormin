## LED status indicators spec

This document shortly explain the definitions for the LED status indicators for the Dormin keyboard. Here are some approaches that I found on the community.

## Requirements

- Minimalist and discret design: LEDs are invisible when off.
- 3 individual RGB lights (each side).
- **Statuses**: Bluetooth Profiles, Battery, and Split link.

## Addressable RGB LEDs using SK6812 Mini-E

- LED Strip:SK6812 addressable LEDs (1-4 LEDs recommended)
- Power: 5V preferred (3.3V compatible), appropriate current capacity
- Data Connection: Single GPIO pin connected to strip's DI (Data In)
- SPI Interface: Available SPI peripheral (uses MOSI pin for data)

> Addressable LED implementations here on [hitsmaxft/zmk-rgbled-widget](https://github.com/hitsmaxft/zmk-rgbled-widget#adding-support-in-custom-boardsshields).

### LED status behaviors

Minimalist and easy-to-remember colors (Nuphy inspired).

**Connection**

🔵🔵🔵 = [Solid] (Left) Host connected
🔵🔵🔵 = [Breathing] (Left) Host disconnected
🔵🔵🔵 = [Blinking] (Left) Advertising

🔵🔵🔵 = [Solid] (Right) Split Linked
🔵🔵🔵 = [Breathing] (Right) Split disconnected

**Battery**

🟢🟢🟢 = [Solid] (Left/Right) 80 - 100%
🟡🟡⚫ = [Solid] (Left/Right) 40 - 79%
🔴⚫⚫ = [Solid] (Left/Right) < 40%

**Layers**

Base = None
Symbol = None
Number = None
Media = 🔵 (Cyan)
Dev = None
Extra = 🟣

## ARGB and LP5012 LED Driver

The LP driver allows fully controled RGB lights with the `SDA` and `SCL` GPIOs, using the I2C protocol, as it's shared it can run more than one peripheral on the same NET. The LP enable the following:

- Fully smooth controled animations
- Ultra Low power
- Don't need dedicated GPIO (Same NET as screens)
