import board
import time
import smbus
import adafruit_dht
import RPi.GPIO as GPIO
from PyQt5.QtCore import QObject, pyqtSignal


class Sensor:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
    
    def read(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

class DHT11(Sensor, QObject):
    '''
        DHT11 sensor class
    '''
    temperature_humidity_ready = pyqtSignal(float, float)
    read_error = pyqtSignal(str)

    def __init__(self, name, pin):
        Sensor.__init__(self, name, pin)
        QObject.__init__(self)
        self.sensor = adafruit_dht.DHT11(self.pin)
        self.temperature = 0.0
        self.humidity = 0.0

    def read(self):
        try:
            self.temperature = self.sensor.temperature
            self.humidity = self.sensor.humidity
            return (self.temperature, self.humidity)
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
            # self.read_error.emit(str(error.args[0]))
        except Exception as error:
            self.sensor.exit()
            self.read_error.emit(str(error))

    def close(self):
        self.sensor.exit()

class PCF8591(Sensor):
    def __init__(self, name, pin, smbusNumber):
        super().__init__(name, pin)
        self.address = self.pin
        self.busNumber = smbusNumber
        self.adc_dac_bus = smbus.SMBus(self.busNumber)

    def read(self, channel):
        match channel:
            case 0:
                payload = 0x40
            case 1:
                payload = 0x41
            case 2:
                payload = 0x42
            case 3:
                payload = 0x43
        self.adc_dac_bus.write_byte(self.address, payload)
        self.adc_dac_bus.read_byte(self.address)
        return self.adc_dac_bus.read_byte(self.address)

    def write(self, val):
        temp = int(val)
        self.adc_dac_bus.write_byte_data(self.address, 0x40, temp)
        


class LightSensor(Sensor):
    '''
        Light sensor class - Analog Signal Version
        Output value range 0 - 255
        The stronger the light the smaller the output value, and vice versa.
    '''
    def __init__(self, name, pin, smbusNumber):
        super().__init__(name, pin)
        self.pcf8591 = PCF8591(name, pin, smbusNumber)
    
    def read(self):
        return self.pcf8591.read(0)

    def write(self, val):
        self.pcf8591.write(val)

    def close(self):
        pass 

class Light_dt(Sensor):
    '''
        Light sensor class - Digital Signal Version
        Output value range 0 or 1
        0 means light, 1 means no light
    '''
    def __init__(self, name, pin):
        super().__init__(name, pin)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        self.light_value = 0

    def read(self):
        self.light_value = GPIO.input(self.pin)
        return self.light_value

    def close(self):
        GPIO.cleanup()


class SmokeSensor(Sensor):
    def __init__(self, name, pin, smbusNumber):
        super().__init__(name, pin)
        self.pcf8591 = PCF8591(name, pin, smbusNumber)
    
    def read(self):
        return self.pcf8591.read(1)

    def close(self):
        pass  


def main():
    dht11 = DHT11("dht11", board.D18)
    temp, humi = dht11.read()
    dht11.close()
    print(temp, humi)
    light_sensor = LightSensor("light_sensor", 0x48, 1)
    print(light_sensor.read())
    light_dt = Light_dt("light_dt", 16)
    print(light_dt.read())
    smoke_sensor = SmokeSensor('smoke', 0x48, 1)
    print(smoke_sensor.read())

if __name__ == "__main__":
    main()