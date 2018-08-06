1. Download raspberry pi image. [https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/ "https://www.raspberrypi.org/downloads/raspbian/")
2. Follow instruction to burn image to sd card [https://www.raspberrypi.org/documentation/installation/installing-images/README.md](https://www.raspberrypi.org/documentation/installation/installing-images/README.md "https://www.raspberrypi.org/documentation/installation/installing-images/README.md"). 
TLDR: use [Etcher](https://etcher.io/ "Etcher")
3. You may need a monitor (via hdmi) to setup your Pi
4. Rename root password, user password. Default user `pi` password `raspberry`
5. Open `raspi-config` enable `expand filesystem`, `ssh`, `I2C` & `GPIO` (for hardware control)
6. Optional: setup rasberry pi wifi as AP so you can connect to it and drive (instead of finding its ip) [Tutorial](/docs/PI_network.md	"Setup network")
