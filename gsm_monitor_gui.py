"""
GSM Signal Monitor GUI
Minimal interface for real-time GSM signal monitoring
"""

import tkinter as tk
from tkinter import ttk
from gsm_scanner import GSMScanner
import threading
from datetime import datetime


class GSMMonitorGUI:
    """Minimal GUI for GSM signal monitoring"""
    
    PROVIDER_COLORS = {
        "Orange": "#FF6600",
        "Vodafone": "#E60000",
        "Telekom": "#E20074",
        "Digi": "#0066CC",
        "Unknown": "#808080"
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("GSM Signal Monitor - Romania")
        self.root.geometry("750x720")
        self.root.resizable(True, True)
        self.root.configure(bg="#1A2332")  # Dark blue background
        
        self.scanner = GSMScanner(gain=40)
        self.is_scanning = False
        self.last_update_time = None
        self.next_update_seconds = 0
        self.countdown_timer = None
        self.previous_values = {}  # Store previous values for comparison
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface"""
        # Title bar with gradient effect
        title_frame = tk.Frame(self.root, bg="#0F1419", height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="GSM Signal Monitor",
            font=("Helvetica", 22, "bold"),
            bg="#0F1419",
            fg="white"
        )
        title_label.place(x=20, y=8)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Real-time spectrum analysis",
            font=("Helvetica", 10),
            bg="#0F1419",
            fg="#7A8BA0"
        )
        subtitle_label.place(x=20, y=50)
        
        # Main content
        content_frame = tk.Frame(self.root, bg="#1A2332")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Info panel
        info_frame = tk.Frame(content_frame, bg="#263447", relief=tk.RIDGE, bd=2)
        info_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        info_title = tk.Label(
            info_frame,
            text="Network Status",
            font=("Helvetica", 12, "bold"),
            bg="#263447",
            fg="#FFFFFF"
        )
        info_title.pack(pady=(8, 2), anchor="w", padx=15)
        
        self.status_label = tk.Label(
            info_frame,
            text="Ready to scan",
            font=("Helvetica", 10),
            bg="#263447",
            fg="#A0B0C0"
        )
        self.status_label.pack(pady=(0, 2), anchor="w", padx=15)
        
        # Last update timestamp
        self.timestamp_label = tk.Label(
            info_frame,
            text="Last update: Never",
            font=("Helvetica", 9),
            bg="#263447",
            fg="#7A8BA0"
        )
        self.timestamp_label.pack(pady=(0, 2), anchor="w", padx=15)
        
        # Next update countdown
        self.countdown_label = tk.Label(
            info_frame,
            text="Next update in: --",
            font=("Helvetica", 9),
            bg="#263447",
            fg="#7A8BA0"
        )
        self.countdown_label.pack(pady=(0, 8), anchor="w", padx=15)
        
        # Signal strength panel
        signal_frame = tk.Frame(content_frame, bg="#263447", relief=tk.RIDGE, bd=2)
        signal_frame.pack(fill=tk.X, pady=(0, 10), padx=5)
        
        signal_title = tk.Label(
            signal_frame,
            text="Signal Strength (dBm)",
            font=("Helvetica", 12, "bold"),
            bg="#263447",
            fg="#FFFFFF"
        )
        signal_title.pack(pady=(10, 5), anchor="w", padx=15)
        
        signal_subtitle = tk.Label(
            signal_frame,
            text="Lower values indicate stronger signals",
            font=("Helvetica", 9, "italic"),
            bg="#263447",
            fg="#7A8BA0"
        )
        signal_subtitle.pack(pady=(0, 10), anchor="w", padx=15)
        
        # Provider signal display
        providers_container = tk.Frame(signal_frame, bg="#263447")
        providers_container.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.provider_frames = {}
        providers = ["Orange", "Vodafone", "Telekom", "Digi"]
        
        for provider in providers:
            self.create_provider_row(providers_container, provider)
        
        # Control panel
        control_frame = tk.Frame(content_frame, bg="#263447", relief=tk.RIDGE, bd=2)
        control_frame.pack(fill=tk.X, padx=5)
        
        control_title = tk.Label(
            control_frame,
            text="Scan Controls",
            font=("Helvetica", 11, "bold"),
            bg="#263447",
            fg="#FFFFFF"
        )
        control_title.pack(pady=(10, 5))
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg="#263447")
        button_frame.pack(pady=(5, 15))
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Scanning",
            command=self.start_scan,
            font=("Helvetica", 12, "bold"),
            bg="#27AE60",
            fg="#000000",  # Black text for better visibility
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            activebackground="#229954",
            activeforeground="#000000"
        )
        self.start_button.pack(side=tk.LEFT, padx=8)
        
        self.stop_button = tk.Button(
            button_frame,
            text="■ Stop Scanning",
            command=self.stop_scan,
            font=("Helvetica", 12, "bold"),
            bg="#E74C3C",
            fg="#000000",  # Black text for better visibility
            width=20,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor="hand2",
            state=tk.DISABLED,
            activebackground="#C0392B",
            activeforeground="#000000"
        )
        self.stop_button.pack(side=tk.LEFT, padx=8)
        
    def create_provider_row(self, parent, provider):
        """Create a row for provider signal display"""
        # Container with border
        container = tk.Frame(parent, bg="#1E2A3A", relief=tk.SOLID, bd=1)
        container.pack(fill=tk.X, pady=4, padx=5)
        
        row_frame = tk.Frame(container, bg="#1E2A3A", height=42)
        row_frame.pack(fill=tk.X, padx=8, pady=6)
        row_frame.pack_propagate(False)
        
        # Provider name with colored indicator
        name_container = tk.Frame(row_frame, bg="#1E2A3A")
        name_container.pack(side=tk.LEFT)
        
        color_indicator = tk.Label(
            name_container,
            text="●",
            font=("Helvetica", 16),
            bg="#1E2A3A",
            fg=self.PROVIDER_COLORS[provider]
        )
        color_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        name_label = tk.Label(
            name_container,
            text=provider,
            font=("Helvetica", 13, "bold"),
            bg="#1E2A3A",
            fg="#FFFFFF",
            width=10,
            anchor="w"
        )
        name_label.pack(side=tk.LEFT)
        
        # Progress bar for signal strength
        progress_container = tk.Frame(row_frame, bg="#1E2A3A")
        progress_container.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        style = ttk.Style()
        style.configure(
            f"{provider}.Horizontal.TProgressbar",
            troughcolor="#0F1419",
            background=self.PROVIDER_COLORS[provider],
            thickness=22,
            borderwidth=0
        )
        
        progress = ttk.Progressbar(
            progress_container,
            style=f"{provider}.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            mode='determinate',
            maximum=100
        )
        progress.pack(fill=tk.X)
        
        # Signal value label with units - SIMPLIFIED
        value_container = tk.Frame(row_frame, bg="#1E2A3A")
        value_container.pack(side=tk.LEFT, padx=10)
        
        # Single label with value and unit together
        value_label = tk.Label(
            value_container,
            text="-- dBm",
            font=("Helvetica", 12, "bold"),
            bg="#1E2A3A",
            fg="#E0E8F0",
            width=8,
            anchor="e"
        )
        value_label.pack(side=tk.LEFT)
        
        # Arrow indicator for value change
        arrow_label = tk.Label(
            value_container,
            text="",
            font=("Helvetica", 12, "bold"),
            bg="#1E2A3A",
            fg="#FFFFFF",
            width=2,
            anchor="w"
        )
        arrow_label.pack(side=tk.LEFT)
        
        self.provider_frames[provider] = {
            "progress": progress,
            "value_label": value_label,
            "arrow_label": arrow_label,
            "container": container
        }
    
    def update_signal_display(self, signals):
        """Update the GUI with new signal data"""
        def update():
            print(f"DEBUG: Received signals: {signals}")  # Debug output
            
            # Update timestamp
            self.last_update_time = datetime.now()
            timestamp_str = self.last_update_time.strftime("%H:%M:%S")
            self.timestamp_label["text"] = f"Last update: {timestamp_str}"
            self.timestamp_label["fg"] = "#00FF88"
            
            # Reset countdown timer to 5 seconds
            self.next_update_seconds = 5
            self.update_countdown()
            
            # Normalize power values for display (0-100 scale)
            if signals:
                max_power = max(signals.values()) if signals else 1
                min_power = min(signals.values()) if signals else 0
                power_range = max_power - min_power if max_power != min_power else 1
                
                active_count = 0
                for provider in self.provider_frames:
                    if provider in signals:
                        power = signals[provider]
                        # Normalize to 0-100
                        normalized = ((power - min_power) / power_range) * 100
                        
                        print(f"DEBUG: Setting {provider} = {power:.2f} dBm (normalized: {normalized:.1f}%)")
                        
                        self.provider_frames[provider]["progress"]["value"] = normalized
                        self.provider_frames[provider]["value_label"]["text"] = f"{power:.2f} dBm"
                        self.provider_frames[provider]["value_label"]["fg"] = "#00FF88"  # Bright green for active
                        self.provider_frames[provider]["container"]["bg"] = "#1E2A3A"
                        
                        # Compare with previous value based on displayed precision (2 decimal places)
                        # Round both values to 2 decimals for comparison
                        power_rounded = round(power, 2)
                        
                        if provider in self.previous_values:
                            prev_power_rounded = round(self.previous_values[provider], 2)
                            
                            if power_rounded > prev_power_rounded:
                                # Improved (higher is better for signal strength)
                                self.provider_frames[provider]["arrow_label"]["text"] = "↑"
                                self.provider_frames[provider]["arrow_label"]["fg"] = "#00FF88"  # Green
                            elif power_rounded < prev_power_rounded:
                                # Worse (lower is worse for signal strength)
                                self.provider_frames[provider]["arrow_label"]["text"] = "↓"
                                self.provider_frames[provider]["arrow_label"]["fg"] = "#FF4444"  # Red
                            else:
                                # Same when rounded to display precision
                                self.provider_frames[provider]["arrow_label"]["text"] = ""
                        else:
                            # First time, no arrow
                            self.provider_frames[provider]["arrow_label"]["text"] = ""
                        
                        # Store current value for next comparison
                        self.previous_values[provider] = power
                        active_count += 1
                    else:
                        self.provider_frames[provider]["progress"]["value"] = 0
                        self.provider_frames[provider]["value_label"]["text"] = "-- dBm"
                        self.provider_frames[provider]["value_label"]["fg"] = "#5A6A7A"  # Dim for inactive
                        self.provider_frames[provider]["arrow_label"]["text"] = ""  # No arrow for inactive
                        self.provider_frames[provider]["container"]["bg"] = "#1E2A3A"
                
                self.status_label["text"] = f"Active providers detected: {active_count} | Last scan: successful"
                self.status_label["fg"] = "#27AE60"
            else:
                print("DEBUG: No signals received")
                self.status_label["text"] = "No signals detected | Check RTL-SDR connection"
                self.status_label["fg"] = "#E67E22"
        
        self.root.after(0, update)
    
    def update_countdown(self):
        """Update the countdown timer for next scan"""
        if self.is_scanning and self.next_update_seconds > 0:
            self.countdown_label["text"] = f"Next update in: {self.next_update_seconds}s"
            self.countdown_label["fg"] = "#3498DB"
            self.next_update_seconds -= 1
            self.countdown_timer = self.root.after(1000, self.update_countdown)
        elif self.is_scanning:
            self.countdown_label["text"] = "Scanning now..."
            self.countdown_label["fg"] = "#F39C12"

    
    def start_scan(self):
        """Start the scanning process"""
        if not self.is_scanning:
            self.is_scanning = True
            self.start_button["state"] = tk.DISABLED
            self.start_button["bg"] = "#95A5A6"
            self.start_button["fg"] = "#000000"
            self.stop_button["state"] = tk.NORMAL
            self.stop_button["bg"] = "#E74C3C"
            self.stop_button["fg"] = "#000000"
            self.status_label["text"] = "Initializing scan... Please wait"
            self.status_label["fg"] = "#3498DB"
            
            # Start scanner in background
            self.scanner.start_scanning(
                callback=self.update_signal_display,
                interval=5  # Scan every 5 seconds
            )
    
    def stop_scan(self):
        """Stop the scanning process"""
        if self.is_scanning:
            self.is_scanning = False
            
            # Cancel countdown timer
            if self.countdown_timer:
                self.root.after_cancel(self.countdown_timer)
                self.countdown_timer = None
            
            self.start_button["state"] = tk.NORMAL
            self.start_button["bg"] = "#27AE60"
            self.start_button["fg"] = "#000000"
            self.stop_button["state"] = tk.DISABLED
            self.stop_button["bg"] = "#95A5A6"
            self.stop_button["fg"] = "#000000"
            self.status_label["text"] = "Stopping scan..."
            self.status_label["fg"] = "#E67E22"
            self.countdown_label["text"] = "Next update in: --"
            self.countdown_label["fg"] = "#7A8BA0"
            
            # Stop scanner
            threading.Thread(target=self._stop_scanner, daemon=True).start()
    
    def _stop_scanner(self):
        """Stop scanner in background thread"""
        self.scanner.stop_scanning()
        self.root.after(0, lambda: self.status_label.config(
            text="Ready to scan",
            fg="#7F8C8D"
        ))
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_scanning:
            self.scanner.stop_scanning()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = GSMMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
