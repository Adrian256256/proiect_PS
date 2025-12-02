# 📡 GSM Detector Romania - RTL-SDR

GSM band detector for Romania using RTL-SDR to scan and measure GSM signal strength from different providers (Orange, Vodafone, Telekom, Digi).

## 🎯 Features

- ✅ Scan GSM 900 MHz band (935-960 MHz downlink)
- ✅ Scan GSM 1800 MHz band (1805-1880 MHz downlink)
- ✅ Measure signal power in dBm for each frequency
- ✅ Identify and analyze signals from providers: Orange, Vodafone, Telekom, Digi
- ✅ Interactive plots with scan results
- ✅ Export results in JSON format
- ✅ Real-time progress display during scanning

## 📋 Hardware Requirements

### RTL-SDR
You need an **RTL-SDR** device (RTL2832U):
- **Recommended**: RTL-SDR Blog V3 or V4
- **Frequency range**: 500 kHz - 1.7 GHz (minimum)
- **Connection**: USB 2.0 or 3.0
- **Antenna**: Telescopic or dipole for GSM bands

### Where to buy RTL-SDR in Romania:
- [RTL-SDR.com](https://www.rtl-sdr.com/buy-rtl-sdr-dvb-t-dongles/) - ~$35-45 (with international shipping)
- Local electronics stores
- AliExpress / eBay (~$25-30)

## 🔧 Installation

### 1. Install RTL-SDR drivers (macOS)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install librtlsdr
brew install librtlsdr
```

### 2. Verify RTL-SDR device

```bash
# Connect RTL-SDR to USB
# Test if it's detected
rtl_test -t
```

You should see:
```
Found 1 device(s):
  0:  Realtek, RTL2838UHIDIR, SN: 00000001
```

### 3. Install Python dependencies

```bash
# Clone or download the project
cd /path/to/project

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install pyrtlsdr numpy matplotlib scipy setuptools
```

## 🚀 Usage

### Method 1: Bash script (recommended)

```bash
chmod +x run.sh
./run.sh
```

### Method 2: Direct with Python

```bash
source .venv/bin/activate
python3 GSM_detector.py
```

## 📊 Results

The application will generate:

1. **Console output**: Displays real-time scanning progress
2. **PNG plot** (`images/gsm_scan_results.png`): Signal power visualization across bands
3. **JSON file** (`gsm_results.json`): Raw data for further analysis

### Example output:

```
╔════════════════════════════════════════════════════════════╗
║         GSM DETECTOR ROMANIA - RTL-SDR                     ║
║         Scanning GSM 900 and 1800 MHz bands                ║
╚════════════════════════════════════════════════════════════╝

============================================================
🔍 GSM DETECTOR ROMANIA - Full Scan
============================================================
Time: 2025-12-02 15:30:45

📡 Scanning GSM-900 (GSM 900 Downlink)
   Range: 935.0 - 960.0 MHz
   935.000 MHz: -65.3 dBm [0%]
   ...
✓ Scan complete: 125 points

📊 Analysis GSM-900:
   Orange      : Max= -52.1 dBm @ 942.50 MHz
   Vodafone    : Max= -58.3 dBm @ 945.20 MHz
   Telekom     : Max= -61.5 dBm @ 948.80 MHz
   Digi        : Max= -64.2 dBm @ 951.40 MHz

📡 Scanning GSM-1800 (GSM 1800 Downlink (DCS))
   Range: 1805.0 - 1880.0 MHz
   ...
```

## 📈 Interpreting Results

### Signal Power (dBm)

| dBm Level | Quality | Description |
|-----------|---------|-------------|
| -50 dBm   | Excellent | Very strong signal (very close to tower) |
| -60 dBm   | Very good | Strong signal (tower proximity) |
| -70 dBm   | Good | Good signal (normal urban coverage) |
| -80 dBm   | Acceptable | Medium signal (edge of coverage) |
| -90 dBm   | Weak | Weak signal (poor coverage area) |
| -100 dBm  | Very weak | Very weak signal (usability limit) |
| -120 dBm  | Noise | No detectable GSM signal |

### GSM Providers in Romania

- **🟠 Orange**: Main operator, extensive national coverage
- **🔴 Vodafone**: Very good urban coverage
- **🟣 Telekom (Magenta)**: Good coverage, especially urban areas
- **🔵 Digi**: Newer operator, growing coverage

## 🔬 GSM Bands in Romania

### GSM 900 MHz
- **Downlink**: 935-960 MHz (scanned by application)
- **Uplink**: 890-915 MHz
- **Usage**: Wide area coverage, good building penetration
- **Operators**: All 4 providers

### GSM 1800 MHz (DCS)
- **Downlink**: 1805-1880 MHz (scanned by application)
- **Uplink**: 1710-1785 MHz
- **Usage**: High capacity, urban areas
- **Operators**: All 4 providers

## ⚠️ Legal Notice

### Legality in Romania
✅ **Legal**: Receiving GSM signals (scanning, monitoring)
❌ **Illegal**: 
- Decoding communications (interception)
- Interference with mobile networks
- Transmission on GSM bands without license

This tool **only listens** to public GSM signals and measures their power - **completely legal**.

## 🐛 Troubleshooting

### Error: "RTL-SDR not found"
```bash
# Check device
rtl_test

# Check USB permissions (Linux)
sudo usermod -a -G plugdev $USER
# Logout and login again

# macOS - reinstall drivers
brew reinstall librtlsdr
```

### Error: "No module named 'rtlsdr'"
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall pyrtlsdr
pip install --upgrade pyrtlsdr
```

### Error: "No module named 'pkg_resources'"
```bash
# Install setuptools
pip install setuptools
```

### Very weak signal power (-120 dBm everywhere)
- Check RTL-SDR antenna (should be fully extended)
- Place RTL-SDR near a window
- Avoid metal objects nearby
- Check gain: try setting manually (e.g., `gain=30`)

### Noisy signal
```python
# In GSM_detector.py, modify:
detector = GSMDetector(sample_rate=2.4e6, gain=20)  # Manual gain
```

## 📁 Project Structure

```
.
├── GSM_detector.py       # Main application
├── run.sh                # Launch script
├── README.md             # Romanian documentation
├── README_EN.md          # English documentation (this file)
├── images/               # Generated plots
│   └── gsm_scan_results.png
├── gsm_results.json      # Scan results
└── .venv/                # Python virtual environment
```

## 📚 References

- [RTL-SDR Documentation](https://www.rtl-sdr.com)
- [GSM Frequencies Romania - ANCOM](https://www.ancom.ro)
- [PyRTLSDR Library](https://github.com/roger-/pyrtlsdr)
- [GSM Architecture](https://en.wikipedia.org/wiki/GSM_frequency_bands)

## 🤝 Contributing

Contributions are welcome! If you have suggestions or improvements:
1. Fork the repository
2. Create a branch for your feature
3. Commit your changes
4. Create a Pull Request

## 📄 License

This project is provided "as-is" for educational purposes.

## 👨‍💻 Author

Created for PS project - Faculty

---

**Last updated**: December 2, 2025

For questions or issues, please open an issue on GitHub! 🚀
