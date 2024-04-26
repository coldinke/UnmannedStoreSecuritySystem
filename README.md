# Unmanned Store Security System

## Project Intro

### Requirements

The project is based on the PyQt5 and the raspberryPi.

see the `requirements.txt`, the current version in below:
```requirements.txt
Adafruit-Blinka==8.39.1
adafruit-circuitpython-busdevice==5.2.9
adafruit-circuitpython-connectionmanager==1.0.1
adafruit-circuitpython-dht==4.0.4
adafruit-circuitpython-requests==3.2.5
adafruit-circuitpython-typing==1.10.3
Adafruit-DHT==1.4.0
Adafruit-PlatformDetect==3.62.0
Adafruit-PureIO==1.1.11
av==12.0.0
numpy==1.26.4
picamera2==0.3.18
pidng==4.0.9
piexif==1.1.3
pillow==10.3.0
pyftdi==0.55.4
PyOpenGL==3.1.7
pyserial==3.5
python-prctl==1.8.1
pyusb==1.2.1
rpi-ws281x==5.0.0
RPi.GPIO==0.7.1
simplejpeg==1.7.2
smbus==1.1.post2
sysv-ipc==1.1.0
typing_extensions==4.11.0
v4l2-python3==0.3.4
PyQt==5.15.9
```

### Usage

> It is assumed here that your hardware connectivity is in line with that of the project develops.

- Clone the current project code from Github.

`git clone git@github.com:coldinke/factory.git`

- Create a new virtual environment and activate it

```bash
python -m venv ./VIRTUAL_NAME
# bash
source ./VIRTUAL_NAME/bin/activate
```
- Install project dependencies

`python install -r ./requirements.txt`

- Go to the `src` directory and execute the follow command

`python app.py`


## Used hardware

### Sensor

- DHT11: [link](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup)

- Light: [link](https://cloud.tencent.com/developer/article/1705838)

- Smoke: [link](https://cloud.tencent.com/developer/article/1705846)

### Device

LED, Relay, Buzzer: see Reference.

Fan:    [TODO](...)

Camera: [link](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)

## Reference

Raspberry Pi: [link](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
Raspberry Pi Pinout: [link](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
GPIO zero: [link](https://gpiozero.readthedocs.io/en/latest/)
Picamera2 [link](https://github.com/raspberrypi/picamera2/blob/main/examples)