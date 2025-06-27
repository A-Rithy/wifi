# wifi.png
# Wifi hacking
![alt text](image.png)
// Installation Instructions for Linux:
# 1. Update system packages
```
sudo apt update && sudo apt upgrade -y
```
# 2. Install required dependencies
```
sudo apt install -y \
    python3 \
    python3-pip \
    aircrack-ng \
    wireless-tools \
    net-tools \
    tshark \
    hcxdumptool \
    hcxtools \
    libpcap-dev
```
# 3. Clone the repository (if available)
git clone https://github.com/A-Rithy/wifi-deauth-tool.git
cd wifi-deauth-tool
```
# 4. Make the script executable
chmod +x wifi_deauth.py
```
# 5. Install Python dependencies
pip3 install -r requirements.txt  # If available
```
# Or manually install:
pip3 install colorama
```
# 6. Run the tool
```
sudo ./wifi_deauth.py
```
// Alternative Installation (Docker):
bash

# 1. Install Docker
```
sudo apt install -y docker.io
```
# 2. Create Dockerfile (if not included)
```
cat > Dockerfile <<EOL
FROM kalilinux/kali-rolling
RUN apt update && apt install -y \
    aircrack-ng \
    wireless-tools \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
COPY wifi_deauth.py /app/
WORKDIR /app
RUN chmod +x wifi_deauth.py
CMD ["./wifi_deauth.py"]
EOL
```
# 3. Build and run
```
sudo docker build -t wifi-deauth .
sudo docker run -it --net=host --privileged wifi-deauth
```
# README.md\wifi.png
![alt text](image-1.png)
// Uninstallation:

# Remove the tool and dependencies
```
sudo apt remove -y aircrack-ng wireless-tools
pip3 uninstall colorama
```
# Remove the repository
```
cd ..
rm -rf wifi-deauth-tool
```
# For Docker cleanup
```
sudo docker rmi wifi-deauth
```
# Important Notes:
Requirements:

Kali Linux or any Linux distro with kernel supporting monitor mode

Wireless adapter that supports monitor mode (check with iw list)

Root privileges are mandatory

# Recommended Hardware:

Alfa AWUS036NHA or similar high-power wireless adapters

At least 2GB RAM

Dual-core processor

# Usage Tips:

# Check available wireless interfaces
```
iwconfig
```
# Verify monitor mode support
```
sudo airmon-ng
```
# Run with verbose output (for debugging)
```
sudo ./wifi_deauth.py --verbose
```
# Legal Disclaimer:

This tool is for educational purposes only

Use only on networks you own or have permission to test

Unauthorized use may violate laws in your jurisdiction

# Troubleshooting:

# If monitor mode fails, try:
```
sudo rfkill unblock all
sudo ifconfig wlan0 down
sudo iwconfig wlan0 mode monitor
sudo ifconfig wlan0 up
```
# For driver issues, check:
```
sudo apt install firmware-linux firmware-realtek
```
# tools DoS @![alt text](image.png)
