import RPi.GPIO as GPIO

class Device:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, 0)
    
    def off(self):
        GPIO.output(self.pin, 1)

    def close(self):
        self.off()
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.cleanup()

class Buzz(Device):
    def __init__(self, name, pin):
        super().__init__(name, pin)
        print(f"{self.name} init done...")


class LED(Device):
    def __init__(self, name, pin):
        super().__init__(name, pin)
        print(f"{self.name} init done...")

class Relay(Device):
    def __init__(self, name, pin):
        super().__init__(name, pin)
        print(f"{self.name} init done...")
