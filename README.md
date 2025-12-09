# RTL-SDR Project: GSM Spectrum Monitoring and Analysis

## Description

This project uses an RTL-SDR (Software Defined Radio) device to monitor and analyze GSM signals in the area. The purpose is educational, aiming to understand the radio spectrum and mobile networks.

## Objectives

1. Visualization of GSM frequency bands
   - GSM 900 MHz (935-960 MHz downlink)
   - GSM 1800 MHz (1805-1880 MHz downlink)

2. Identification of active channels
   - Detection of frequencies used by operators
   - Mapping of ARFCN channels (Absolute Radio Frequency Channel Number)

3. Signal strength measurement (RSSI)
   - Real-time signal intensity monitoring
   - Comparison of power levels between different cells

4. Coverage map creation
   - Collection of GPS data and signal strength
   - Generation of coverage maps for different operators

## Required Hardware

- RTL-SDR Dongle (RTL2832U chipset)
- Antenna optimized for 900-1800 MHz
- Computer (macOS/Linux/Windows)

## Required Software

```bash
# Installation on macOS
brew install rtl-sdr
brew install kalibrate-rtl
brew install gqrx
```

## Usage

### GUI Application - Real-time Signal Monitor

The project includes a graphical interface that monitors GSM signal strength from Romanian providers in real-time.

```bash
# Run the GUI application
python3 gsm_monitor_gui.py
```

Features:
- Real-time signal strength monitoring for Orange, Vodafone, Telekom, and Digi
- Visual progress bars showing relative signal strength
- Automatic scanning every 5 seconds with countdown timer
- Value change indicators (arrows showing improvement or degradation)
- Timestamp of last update
- Clean dark blue interface

### How Signal Strength Values Are Calculated

The signal strength values displayed in the GUI are measured in **dBm (decibels-milliwatt)**, which is a standard unit for RF power measurement.

#### Measurement Process:

1. **Spectrum Scanning**: The RTL-SDR device scans GSM frequency bands (935-960 MHz for GSM-900 and 1805-1880 MHz for GSM-1800) using the `rtl_power` tool

2. **Power Detection**: For each frequency bin (200 kHz wide), the tool measures the RF power level in dBm:
   - Higher values (closer to 0) = Stronger signal
   - Lower values (more negative) = Weaker signal
   - Example: -10 dBm is stronger than -30 dBm

3. **Provider Identification**: Signals are mapped to providers based on frequency ranges:
   - Orange: 935-945 MHz, 1805-1825 MHz
   - Vodafone: 945-955 MHz, 1825-1845 MHz
   - Telekom: 955-960 MHz, 1845-1865 MHz
   - Digi: 940-950 MHz, 1860-1880 MHz

4. **Averaging**: Multiple power measurements within a provider's frequency range are averaged to give a single representative value

5. **Display**: Values are shown with 2 decimal places (e.g., -17.35 dBm) with color-coded arrows:
   - Green up arrow (↑): Signal improved since last scan
   - Red down arrow (↓): Signal degraded since last scan
   - No arrow: Signal unchanged

#### Typical Value Ranges:
- **-10 to -50 dBm**: Excellent signal (close to cell tower)
- **-50 to -70 dBm**: Good signal (normal coverage)
- **-70 to -90 dBm**: Weak signal (edge of coverage)
- **Below -90 dBm**: Very weak signal (poor coverage)

**Note**: These are passive measurements of broadcast signals only. No private communications are intercepted.

### Command Line Tools

#### Quick GSM-900 scan
```bash
kal -s GSM900 -g 40
```

#### Test the scanner module
```bash
python3 gsm_scanner.py
```

#### Spectrum visualization in GQRX
1. Open GQRX
2. Set frequency to 945 MHz (GSM-900 band center)
3. Observe active channels

#### Signal strength monitoring
```bash
rtl_power -f 935M:960M:200k -g 40 -i 1 gsm900_scan.csv
```

## Legal Considerations

- Passive monitoring only - no interception of private communications
- Educational purposes - compliance with telecommunications legislation
- Public channels - only broadcast information is analyzed

## Expected Results

- Identification of active frequencies in the area
- Coverage maps for mobile operators
- Statistics about GSM cell density
- Radio spectrum visualizations
- Real-time signal strength comparison between providers

## Project Structure

```
.
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── gsm_scanner.py           # Core scanning module
└── gsm_monitor_gui.py       # GUI application
```

## Resources

- [RTL-SDR Wiki](https://www.rtl-sdr.com/)
- [Kalibrate-rtl Documentation](https://github.com/steve-m/kalibrate-rtl)
- [GSM Frequency Bands](https://en.wikipedia.org/wiki/GSM_frequency_bands)

---
