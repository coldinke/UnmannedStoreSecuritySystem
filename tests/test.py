import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock
from src.sensor import *
from src.device import *


class TestDHT11(unittest.TestCase):
    @patch('sensor.adafruit_dht.DHT11')
    def test_read(self, MockDHT11):
        mock_dht11 = MockDHT11.return_value
        mock_dht11.temperature = 25.0
        mock_dht11.humidity = 50.0
        dht11 = DHT11("dht11", 4)
        temperature, humidity = dht11.read()
        self.assertEqual(temperature, 25.0)
        self.assertEqual(humidity, 50.0)

class TestCamera(unittest.TestCase):
    @patch('sensor.picamera.PiCamera')
    def test_capture(self, MockPiCamera):
        mock_picamera = MockPiCamera.return_value
        camera = Camera()
        camera.capture("test.jpg")
        mock_picamera.capture.assert_called_once_with("test.jpg")


if __name__ == "__main__":
    unittest.main()

