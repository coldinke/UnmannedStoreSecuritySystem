import adafruit_dht
import board
class Sensor:
    def __init__(self, name, pin):
        self.name = name
        self.pin = self.pin
    
    def read(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

class DHT11(Sensor):
    def __init__(self):
        super().__init__()
        self.operation =  adafruit_dht.DHT11(self.pin)
        self.temperature = 0.0
        self.humidity = 0.0

    def read(self):
        self.temperature = self.operation.temperature
        self.humidity = self.operation.temperature
        return (self.temperature, self.humidity)

    def close(self):
        self.operation.exit()

class PCF8591(Sensor):
    def __init__(self, name, addr, smbusNumber):
        self.name = self.name
        self.address = addr
        self.busNumber = smbusNumber
        self.adc_dac_bus = smbus.SMbus(self.busNumber)

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
        
        
    