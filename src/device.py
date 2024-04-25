import RPi.GPIO as GPIO
import time

class Device:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

    def off(self):
        print('off')
        GPIO.output(self.pin, GPIO.LOW)
    
    def on(self):
        print('on')
        GPIO.output(self.pin, GPIO.HIGH)

    def close(self):
        self.off()
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.cleanup()

class Buzz(Device):
    def __init__(self, name, pin):
        super().__init__(name, pin)
        print(f"{self.name} init done...")

    # def on(self):
    #     super().on()
    
    # def off(self):
    #     super().off()

    # def close(self):
    #     super().close()

class LED(Device):
    def __init__(self, name, pin):
        super().__init__(name, pin)
        print(f"{self.name} init done...")

class Relay(Device):
    def __init__(self, name, pin):
        super().__init__(name, pin)
        print(f"{self.name} init done...")

def main():
    buzzer = Buzz('buzzer', 26)
    led = LED('led', 5)
    relay = Relay('relay', 6)

    led.on()
    buzzer.on()
    relay.on()
    time.sleep(2)
    relay.off()
    led.off()
    buzzer.off()
    # time.sleep(2)
    # buzzer.on()
    # time.sleep(2)
    # buzzer.off()
     


if __name__ == '__main__':
    main()