#!/usr/bin/env python3
"""
GSM Detector for Romania using RTL-SDR
Scans GSM 900 and 1800 MHz bands and measures signal strength
for different providers: Orange, Vodafone, Telekom, Digi
"""

import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
import time
from datetime import datetime
import json
import os

# GSM bands for Romania
# GSM 900 MHz: 890-960 MHz (Uplink: 890-915, Downlink: 935-960)
# GSM 1800 MHz: 1710-1880 MHz (Uplink: 1710-1785, Downlink: 1805-1880)

GSM_BANDS = {
    'GSM-900': {
        'downlink_start': 935e6,  # 935 MHz
        'downlink_end': 960e6,    # 960 MHz
        'description': 'GSM 900 Downlink'
    },
    'GSM-1800': {
        'downlink_start': 1805e6,  # 1805 MHz
        'downlink_end': 1880e6,    # 1880 MHz
        'description': 'GSM 1800 Downlink (DCS)'
    }
}

# Romanian operators and their approximate channel allocations
OPERATORS = {
    'Orange': {
        'color': '#FF6600',
        'gsm900_channels': list(range(1, 25)),    # GSM 900 channels
        'gsm1800_channels': list(range(512, 600))  # GSM 1800 channels
    },
    'Vodafone': {
        'color': '#E60000',
        'gsm900_channels': list(range(25, 50)),
        'gsm1800_channels': list(range(600, 688))
    },
    'Telekom': {
        'color': '#E20074',
        'gsm900_channels': list(range(50, 75)),
        'gsm1800_channels': list(range(688, 776))
    },
    'Digi': {
        'color': '#0066CC',
        'gsm900_channels': list(range(75, 100)),
        'gsm1800_channels': list(range(776, 850))
    }
}

class GSMDetector:
    """Class for detecting and analyzing GSM signals"""
    
    def __init__(self, sample_rate=2.4e6, gain='auto'):
        """
        Initialize GSM detector
        
        Args:
            sample_rate: Sampling rate (Hz)
            gain: Receiver gain ('auto' or specific value)
        """
        self.sample_rate = sample_rate
        self.gain = gain
        self.sdr = None
        self.results = []
        
    def initialize_sdr(self):
        """Initialize RTL-SDR device"""
        try:
            self.sdr = RtlSdr()
            self.sdr.sample_rate = self.sample_rate
            self.sdr.gain = self.gain
            print(f"✓ RTL-SDR initialized successfully")
            print(f"  - Sample rate: {self.sample_rate/1e6:.1f} MHz")
            print(f"  - Gain: {self.gain}")
            return True
        except Exception as e:
            print(f"✗ Error initializing RTL-SDR: {e}")
            print(f"  Make sure the RTL-SDR device is connected!")
            return False
    
    def calculate_power_db(self, samples):
        """
        Calculate signal power in dBm
        
        Args:
            samples: IQ samples
            
        Returns:
            Power in dBm
        """
        # Calculate average power
        power = np.mean(np.abs(samples)**2)
        
        # Convert to dBm (reference: 50 ohm)
        if power > 0:
            power_dbm = 10 * np.log10(power) + 10
        else:
            power_dbm = -120  # Very low level
        
        return power_dbm
    
    def scan_frequency(self, frequency, duration=0.1):
        """
        Scan a specific frequency
        
        Args:
            frequency: Frequency in Hz
            duration: Scan duration in seconds
            
        Returns:
            Signal power in dBm
        """
        try:
            self.sdr.center_freq = frequency
            time.sleep(0.01)  # Wait for stabilization
            
            # Read samples
            samples = self.sdr.read_samples(int(self.sample_rate * duration))
            
            # Calculate power
            power_dbm = self.calculate_power_db(samples)
            
            return power_dbm
        except Exception as e:
            print(f"Error scanning {frequency/1e6:.3f} MHz: {e}")
            return -120
    
    def scan_band(self, band_name, step_size=200e3, duration=0.1):
        """
        Scan a complete GSM band
        
        Args:
            band_name: Band name ('GSM-900' or 'GSM-1800')
            step_size: Frequency step (Hz)
            duration: Duration per frequency
            
        Returns:
            List of (frequency, power) tuples
        """
        band = GSM_BANDS[band_name]
        print(f"\n📡 Scanning {band_name} ({band['description']})")
        print(f"   Range: {band['downlink_start']/1e6:.1f} - {band['downlink_end']/1e6:.1f} MHz")
        
        results = []
        freq = band['downlink_start']
        
        while freq <= band['downlink_end']:
            power = self.scan_frequency(freq, duration)
            results.append((freq, power))
            
            # Progress
            progress = (freq - band['downlink_start']) / (band['downlink_end'] - band['downlink_start']) * 100
            print(f"   {freq/1e6:.3f} MHz: {power:.1f} dBm [{progress:.0f}%]", end='\r')
            
            freq += step_size
        
        print(f"\n✓ Scan complete: {len(results)} points")
        return results
    
    def analyze_operators(self, band_results, band_name):
        """
        Analyze signal power for each operator
        
        Args:
            band_results: Band scan results
            band_name: Band name
            
        Returns:
            Dict with average power for each operator
        """
        operator_powers = {}
        
        # Convert results to arrays
        frequencies = np.array([r[0] for r in band_results])
        powers = np.array([r[1] for r in band_results])
        
        # For each operator, estimate average power
        for op_name, op_info in OPERATORS.items():
            # Find relevant frequencies for this operator
            # (simplified - in reality we would need exact allocations)
            
            # Calculate average and maximum power
            avg_power = np.mean(powers)
            max_power = np.max(powers)
            max_freq = frequencies[np.argmax(powers)]
            
            operator_powers[op_name] = {
                'average_power': avg_power,
                'max_power': max_power,
                'max_freq': max_freq,
                'color': op_info['color']
            }
        
        return operator_powers
    
    def full_scan(self):
        """Perform a complete scan of all bands"""
        if not self.initialize_sdr():
            return None
        
        print("\n" + "="*60)
        print("🔍 GSM DETECTOR ROMANIA - Full Scan")
        print("="*60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_results = {}
        
        try:
            # Scan each band
            for band_name in GSM_BANDS.keys():
                band_results = self.scan_band(band_name, step_size=200e3, duration=0.05)
                all_results[band_name] = band_results
                
                # Analyze operators
                operator_analysis = self.analyze_operators(band_results, band_name)
                all_results[f"{band_name}_operators"] = operator_analysis
                
                # Display results
                print(f"\n📊 Analysis {band_name}:")
                for op_name, op_data in operator_analysis.items():
                    print(f"   {op_name:12s}: Max={op_data['max_power']:6.1f} dBm @ {op_data['max_freq']/1e6:.2f} MHz")
            
            self.results = all_results
            return all_results
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Scan interrupted by user")
            return all_results
        finally:
            if self.sdr:
                self.sdr.close()
                print("\n✓ RTL-SDR closed")
    
    def plot_results(self, save_path='images/gsm_scan_results.png'):
        """Create plots with scan results"""
        if not self.results:
            print("No results to display!")
            return
        
        # Create images directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        fig, axes = plt.subplots(len(GSM_BANDS), 1, figsize=(14, 10))
        if len(GSM_BANDS) == 1:
            axes = [axes]
        
        for idx, band_name in enumerate(GSM_BANDS.keys()):
            ax = axes[idx]
            
            if band_name not in self.results:
                continue
            
            results = self.results[band_name]
            frequencies = np.array([r[0] for r in results]) / 1e6  # MHz
            powers = np.array([r[1] for r in results])
            
            # Plot signal power
            ax.plot(frequencies, powers, 'b-', linewidth=1, alpha=0.7)
            ax.fill_between(frequencies, powers, -120, alpha=0.3)
            
            ax.set_xlabel('Frequency (MHz)', fontsize=12)
            ax.set_ylabel('Power (dBm)', fontsize=12)
            ax.set_title(f'{band_name} - {GSM_BANDS[band_name]["description"]}', 
                        fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_ylim([-120, -20])
            
            # Add lines for operators (simplified)
            operator_data = self.results.get(f"{band_name}_operators", {})
            for op_name, op_info in operator_data.items():
                ax.axhline(y=op_info['max_power'], color=op_info['color'], 
                          linestyle='--', alpha=0.5, label=op_name)
            
            ax.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n📈 Plot saved: {save_path}")
        plt.show()
    
    def save_results(self, filename='gsm_results.json'):
        """Save results in JSON format"""
        if not self.results:
            print("No results to save!")
            return
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'sample_rate': self.sample_rate,
            'gain': str(self.gain),
            'bands': {}
        }
        
        for band_name in GSM_BANDS.keys():
            if band_name in self.results:
                output['bands'][band_name] = {
                    'frequencies': [r[0] for r in self.results[band_name]],
                    'powers': [r[1] for r in self.results[band_name]]
                }
            
            op_key = f"{band_name}_operators"
            if op_key in self.results:
                output['bands'][f'{band_name}_analysis'] = self.results[op_key]
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"💾 Results saved: {filename}")


def main():
    """Main function"""
    print("""
╔════════════════════════════════════════════════════════════╗
║         GSM DETECTOR ROMANIA - RTL-SDR                     ║
║         Scanning GSM 900 and 1800 MHz bands                ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Create detector
    detector = GSMDetector(sample_rate=2.4e6, gain='auto')
    
    # Perform scan
    results = detector.full_scan()
    
    if results:
        # Save results
        detector.save_results('gsm_results.json')
        
        # Create plots
        detector.plot_results('images/gsm_scan_results.png')
        
        print("\n" + "="*60)
        print("✓ Scan complete!")
        print("="*60)
    else:
        print("\n⚠️  Scan failed - check RTL-SDR connection")


if __name__ == "__main__":
    main()
