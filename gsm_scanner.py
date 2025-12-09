"""
GSM Scanner Module
Scans GSM frequencies and collects signal strength data
"""

import subprocess
import re
import threading
import time
import os
import tempfile
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class GSMSignal:
    """Represents a GSM signal measurement"""
    arfcn: int
    frequency: float
    power: float
    provider: str = "Unknown"


class GSMScanner:
    """Scans GSM spectrum using RTL-SDR"""
    
    # Romanian GSM providers and their typical frequency ranges (MHz)
    # Note: These are approximate ranges. Actual allocations may vary by region.
    # GSM-900 downlink: 935-960 MHz (25 MHz total)
    # GSM-1800 downlink: 1805-1880 MHz (75 MHz total)
    ROMANIAN_PROVIDERS = {
        "Orange": [(935.0, 941.0), (1805.0, 1825.0)],     # ~6 MHz in GSM900
        "Vodafone": [(941.0, 948.0), (1825.0, 1850.0)],   # ~7 MHz in GSM900
        "Telekom": [(948.0, 954.0), (1850.0, 1870.0)],    # ~6 MHz in GSM900
        "Digi": [(954.0, 960.0), (1870.0, 1880.0)]        # ~6 MHz in GSM900
    }
    
    def __init__(self, gain=40):
        self.gain = gain
        self.signals = {}
        self.scanning = False
        self.scan_thread = None
        
    def freq_to_provider(self, freq: float) -> str:
        """Identify provider based on frequency"""
        for provider, ranges in self.ROMANIAN_PROVIDERS.items():
            for start, end in ranges:
                if start <= freq <= end:
                    return provider
        return "Unknown"
    
    def scan_with_rtl_power(self, start_freq: float, end_freq: float) -> List[GSMSignal]:
        """Scan frequency range using rtl_power"""
        signals = []
        
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False) as tmp:
                tmp_file = tmp.name
            
            # Run rtl_power
            start_mhz = f"{int(start_freq)}M"
            end_mhz = f"{int(end_freq)}M"
            
            cmd = [
                "rtl_power",
                "-f", f"{start_mhz}:{end_mhz}:200k",
                "-g", str(self.gain),
                "-i", "1",  # 1 second integration
                "-1",  # Single scan
                tmp_file
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"rtl_power error: {result.stderr}")
                return signals
            
            # Parse CSV output
            # Format: date, time, Hz low, Hz high, Hz step, samples, dB, dB, ...
            with open(tmp_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) < 7:
                        continue
                    
                    try:
                        freq_low = float(parts[2]) / 1e6  # Convert to MHz
                        freq_high = float(parts[3]) / 1e6
                        freq_step = float(parts[4]) / 1e6
                        
                        # Power values start from index 6
                        power_values = [float(p) for p in parts[6:] if p]
                        
                        # Create signals for each frequency bin
                        for i, power in enumerate(power_values):
                            freq = freq_low + (i * freq_step)
                            provider = self.freq_to_provider(freq)
                            
                            # Only keep signals above noise floor (e.g., > -60 dB)
                            if power > -60:
                                signals.append(GSMSignal(
                                    arfcn=int(freq * 10),  # Pseudo-ARFCN
                                    frequency=freq,
                                    power=power,
                                    provider=provider
                                ))
                    except (ValueError, IndexError) as e:
                        continue
            
            # Clean up temp file
            os.unlink(tmp_file)
            
        except subprocess.TimeoutExpired:
            print("Scan timeout - RTL-SDR might not be connected")
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
        except FileNotFoundError:
            print("rtl_power not found. Please install: brew install rtl-sdr")
        except Exception as e:
            print(f"Error during scan: {e}")
            if 'tmp_file' in locals() and os.path.exists(tmp_file):
                os.unlink(tmp_file)
        
        return signals
    
    def scan_gsm900(self) -> List[GSMSignal]:
        """Scan GSM-900 band (935-960 MHz downlink)"""
        print("Scanning GSM-900 band (935-960 MHz)...")
        return self.scan_with_rtl_power(935, 960)
    
    def scan_gsm1800(self) -> List[GSMSignal]:
        """Scan GSM-1800 band (1805-1880 MHz downlink)"""
        print("Scanning GSM-1800 band (1805-1880 MHz)...")
        return self.scan_with_rtl_power(1805, 1880)
            
        return signals
    
    def aggregate_by_provider(self, signals: List[GSMSignal]) -> Dict[str, float]:
        """Aggregate signal strength by provider"""
        provider_power = {}
        provider_count = {}
        
        for signal in signals:
            if signal.provider not in provider_power:
                provider_power[signal.provider] = 0
                provider_count[signal.provider] = 0
            
            provider_power[signal.provider] += signal.power
            provider_count[signal.provider] += 1
        
        # Calculate average power per provider
        result = {}
        for provider in provider_power:
            if provider_count[provider] > 0:
                avg_power = provider_power[provider] / provider_count[provider]
                result[provider] = avg_power
        
        return result
    
    def scan_continuous(self, callback=None, interval=30):
        """Continuous scanning with callback for updates"""
        self.scanning = True
        
        while self.scanning:
            print("Scanning GSM-900 band...")
            signals_900 = self.scan_gsm900()
            
            print("Scanning GSM-1800 band...")
            signals_1800 = self.scan_gsm1800()
            
            all_signals = signals_900 + signals_1800
            self.signals = self.aggregate_by_provider(all_signals)
            
            if callback:
                callback(self.signals)
            
            # Wait before next scan
            for _ in range(interval):
                if not self.scanning:
                    break
                time.sleep(1)
    
    def start_scanning(self, callback=None, interval=30):
        """Start continuous scanning in background thread"""
        if self.scan_thread and self.scan_thread.is_alive():
            return
        
        self.scanning = True
        self.scan_thread = threading.Thread(
            target=self.scan_continuous,
            args=(callback, interval),
            daemon=True
        )
        self.scan_thread.start()
    
    def stop_scanning(self):
        """Stop continuous scanning"""
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
    
    def get_latest_signals(self) -> Dict[str, float]:
        """Get the latest aggregated signal data"""
        return self.signals.copy()


if __name__ == "__main__":
    # Test the scanner
    scanner = GSMScanner()
    print("Starting GSM scan...\n")
    
    # Scan GSM-900
    signals_900 = scanner.scan_gsm900()
    print(f"Found {len(signals_900)} signals in GSM-900 band\n")
    
    # Scan GSM-1800
    signals_1800 = scanner.scan_gsm1800()
    print(f"Found {len(signals_1800)} signals in GSM-1800 band\n")
    
    # Combine all signals
    all_signals = signals_900 + signals_1800
    print(f"Total signals detected: {len(all_signals)}\n")
    
    # Show signal count per provider
    provider_counts = {}
    for signal in all_signals:
        provider_counts[signal.provider] = provider_counts.get(signal.provider, 0) + 1
    
    print("Signals per provider:")
    for provider, count in sorted(provider_counts.items()):
        print(f"  {provider}: {count} signals")
    
    # Show average signal strength
    aggregated = scanner.aggregate_by_provider(all_signals)
    print("\nAverage signal strength by provider:")
    for provider in ["Orange", "Vodafone", "Telekom", "Digi"]:
        if provider in aggregated:
            print(f"  {provider}: {aggregated[provider]:.2f} dBm")
        else:
            print(f"  {provider}: No signal detected")
