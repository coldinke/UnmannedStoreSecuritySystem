from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
        QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
        QSpinBox, QTableWidget, QPlainTextEdit)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from sensor import *
from device import *

import sys

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        camera = Camera()
        raw_capture = picamera.array.PiRGBArray(camera.camera)
        while True:
            camera.capture(raw_capture, format="bgr")
            frame = raw_capture.array
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888).rgbSwapped()
            self.changePixmap.emit(image)
            raw_capture.truncate(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_labels = dict()
        # thread
        self.video_thread = VideoThread()
        self.video_thread.changePixmap.connect(self.setImage)
        self.video_thread.start()

        # Sensors
        self.dht11 = DHT11("dht11", board.D4)
        self.pcf8591 = PCF8591("pcf8591", board.D0, 1)

        # Devices
        self.buzzer = Buzzer("buzzer", board.D18)
        self.led = LED("led", board.D17)

        self.init_ui()

        # self.setWindowOpacity(0.9) # 设置窗口透明度
    

    def init_ui(self):
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        left_widget= QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        sensor_button_layout = QVBoxLayout()
        self.query_temperature_button = QPushButton('获取温度数据')
        self.query_temperature_button.clicked.connect(self.get_temperature_from_sensor)
        sensor_button_layout.addWidget(self.query_temperature_button)

        self.query_illuminance_button = QPushButton('获取光照度数据')
        self.query_illuminance_button.clicked.connect(self.get_illuminance_from_sensor)
        sensor_button_layout.addWidget(self.query_illuminance_button)

        self.query_smoke_button = QPushButton('获取烟雾数据')
        self.query_smoke_button.clicked.connect(self.get_smoke_from_sensor)
        sensor_button_layout.addWidget(self.query_smoke_button)

        left_layout.addLayout(sensor_button_layout)

        fan_control_layout = QHBoxLayout()
        fan_label = QLabel("风扇等级:")
        fan_control_layout.addWidget(fan_label)

        self.fan_spin_box = QSpinBox()
        self.fan_spin_box.setRange(0, 3)
        self.fan_spin_box.valueChanged.connect(self.fan_level_changed)
        fan_control_layout.addWidget(self.fan_spin_box)

        left_layout.addLayout(fan_control_layout)

        device_control_layout = QHBoxLayout()
        led_label = QLabel("LED:")
        device_control_layout.addWidget(led_label)

        self.led_button = QPushButton("开")
        self.led_button.clicked.connect(self.control_led)
        device_control_layout.addWidget(self.led_button)

        buzz_label = QLabel("蜂鸣器:")
        device_control_layout.addWidget(buzz_label)

        self.buzz_button = QPushButton("开")
        self.buzz_button.clicked.connect(self.control_buzzer)
        device_control_layout.addWidget(self.buzz_button)

        left_layout.addLayout(device_control_layout)


        self.status_text = QPlainTextEdit()
        self.status_text.setReadOnly(True)
        left_layout.addWidget(self.status_text)

        main_layout.addWidget(left_widget, 0, 0, 12, 4)

        right_widget = QWidget()
        right_layout = QGridLayout()
        right_widget.setLayout(right_layout)

        self.video_label = QLabel('视频')
        self.video_label.setStyleSheet("background-color: gray; color: white; font-weight: bold;")
        right_layout.addWidget(self.video_label, 0, 0, 7, 7)

        sensor_group = QGroupBox("传感器数据")
        sensor_layout = QVBoxLayout()
        sensor_group.setLayout(sensor_layout)

        self.create_sensor_display(sensor_layout, "温度传感器", "25°C")
        self.create_sensor_display(sensor_layout, "光照传感器", "100 lx")
        self.create_sensor_display(sensor_layout, "烟雾传感器", "正常")

        right_layout.addWidget(sensor_group, 7, 0, 5, 7)

        print(self.data_labels)

        main_layout.addWidget(right_widget, 0, 4, 12, 8)
        main_layout.setSpacing(0)

        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(main_layout)


    def create_sensor_display(self, layout, sensor_name, initial_value):
        sensor_layout = QHBoxLayout()
        name_label = QLabel(sensor_name + ":")
        name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: navy;")
        sensor_layout.addWidget(name_label)

        data_label = QLabel(initial_value)
        data_label.setFont(QFont("Arial", 24))
        data_label.setStyleSheet("font-size: 40px; color: green; background-color: lightblue;")
        sensor_layout.addWidget(data_label)
        self.data_labels[sensor_name] = data_label

        layout.addLayout(sensor_layout)

    def add_message_to_status(self, message):
        self.status_text.appendPlainText(message)

    def setImage(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def get_temperature_from_sensor(self):
        temperature, _ = self.dht11.read()
        self.data_labels["温度传感器"].setText(f"{temperature}°C")
        self.add_message_to_status(f"获取温度数据: {temperature}°C 成功")

    def get_illuminance_from_sensor(self):
        print("获取光照度数据")

    def get_smoke_from_sensor(self):
        print("获取烟雾数据")

    def fan_level_changed(self, value):
        print(f"选择的风扇等级: {value}")

    def control_led(self):
        if self.led_button.isChecked():
            self.led.on()
            self.led_button.setText("关")
        else:
            self.led.off()
            self.led_button.setText("开")

    def control_buzzer(self):
        if self.buzz_button.isChecked():
            self.buzzer.on()
            self.buzz_button.setText("关")
        else:
            self.buzzer.off()
            self.buzz_button.setText("开")


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
