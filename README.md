# GSM Spectrum Monitor

Educational project for monitoring GSM signal strength from Romanian mobile operators using RTL-SDR.

## Features

- Real-time signal strength monitoring (Orange, Vodafone, Telekom, Digi)
- Visual progress bars with trend indicators
- GSM-900 and GSM-1800 band scanning
- Automatic 5-second interval updates

## Requirements

**Hardware:**
- RTL-SDR dongle (RTL2832U chipset)
- 900-1800 MHz antenna

**Software:**
```bash
# macOS installation
brew install rtl-sdr kalibrate-rtl
pip install -r requirements.txt
```

## Usage

```bash
# Run GUI application
python3 gsm_monitor_gui.py

# Test scanner module
python3 gsm_scanner.py
```

## How It Works

**Signal Measurement:**
1. RTL-SDR scans GSM bands (935-960 MHz, 1805-1880 MHz)
2. `rtl_power` measures RF power in dBm per frequency
3. Signals mapped to providers by frequency range
4. Average power calculated per provider

**Signal Strength (dBm):**
- `-10 to -50`: Excellent
- `-50 to -70`: Good
- `-70 to -90`: Weak
- `< -90`: Very weak

**Frequency Allocation:**
- Orange: 935-941 MHz, 1805-1825 MHz
- Vodafone: 941-948 MHz, 1825-1845 MHz
- Telekom: 948-954 MHz, 1845-1865 MHz
- Digi: 954-960 MHz, 1860-1880 MHz

## Architecture

```
RTL-SDR → rtl_power → CSV → scan_with_rtl_power() 
  → freq_to_provider() → aggregate_by_provider() 
  → update_signal_display() → GUI
```

**Key Components:**

- `gsm_scanner.py`: Core scanning logic
  - `scan_with_rtl_power()`: Executes spectrum scan
  - `freq_to_provider()`: Maps frequency to operator
  - `aggregate_by_provider()`: Averages signal strength
  
- `gsm_monitor_gui.py`: Tkinter GUI
  - Threading for responsive interface
  - Progress bars with gradients
  - Trend indicators (↑/↓)

## Legal Notice

Passive monitoring only. No interception of private communications. Educational purposes.
