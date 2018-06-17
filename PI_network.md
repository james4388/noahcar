You can setup raspberry's built in wifi as access point and connect to it to control. It's easier since you always know PiCar server IP.

Assume your built in interface is `wlan0`. If you have wifi dongle it may take over `wlan0` so you should enable "predictable network 
interface names" using `raspi-config`. Wifi dongle will be now named something like `wlx000f00491730` but it never changed.

## Setup control software
You will need `hostapd` for access point
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install dnsmasq hostapd
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
```

## Configure static IP
`dhcpcd` will try to assign ip and call `wpa_suplicant` on `wlan0`, this will conflict with `hostapd`. Open dhcpd config
```
sudo nano /etc/dhcpcd.conf
```
add these rule
```
interface wlan0
    static ip_address=192.168.5.1/24
    static routers=192.168.5.1
    static domain_name_servers=8.8.8.8,4.4.4.4
    nohook wpa_supplicant    # Important to tell wpa_suplicant to leave me alone
```

## Configuring DHCP server (dnsmasq)
```
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig  
sudo nano /etc/dnsmasq.conf
```
```
interface=wlan0
  dhcp-range=192.168.5.2,192.168.5.20,255.255.255.0,24h
```

## Configuring access point host software (hostapd)
Create host config
```
sudo nano /etc/hostapd/hostapd.conf
```
```
interface=wlan0
driver=nl80211
ssid=PiCar
wpa_passphrase=ChangeMe
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```
now tell hostapd where to find you config
```
sudo nano /etc/default/hostapd
```
find and change
```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

## Start everything up
```
sudo reboot
sudo service dhcpcd restart
sudo systemctl start hostapd
sudo systemctl start dnsmasq
```
