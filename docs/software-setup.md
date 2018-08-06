#### Enable source
```
sudo vi /etc/apt/sources.list
# Uncomment line below then 'apt-get update' to enable 'apt-get source'
deb-src http://archive.raspbian.org/raspbian/ stretch main contrib non-free rpi
```
#### Install build library
```
sudo apt-get update
sudo apt-get upgrade
```
#### Build tool
```
sudo apt-get install build-essential
sudo apt-get install build-essential libc6-dev
sudo apt-get install libncurses5-dev libncursesw5-dev libreadline6-dev
sudo apt-get install libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev
sudo apt-get install libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev
```
#### Python package
Python 3.5 should be installed already, if not try
```
sudo apt-get install python3.5
```
#### Clone repo
```
git clone https://github.com/james4388/noahcar.git
cd noahcar
```
#### Virtual env
```
virtualenv env -p python3.5
. env/bin/activate
```
#### Install requirement
In virtual env, run
```
pip install -r requirements.txt
```
