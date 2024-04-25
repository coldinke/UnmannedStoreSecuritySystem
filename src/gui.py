from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout,
        QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
        QSpinBox, QTableWidget, QPlainTextEdit, QLineEdit)
from PyQt5.QtGui import QFont, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QObject, QTimer

from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2

from sensor import *
from device import *

import sys

class VideoThread(QThread):
    def __init__(self, picam2):
        super().__init__()
        self.picam2 = picam2
        self._stop_flag = False

    def run(self):
        def post_callback(request):
            metadata = request.get_metadata()
            text = ''.join(f"{k}: {v}\n" for k, v in metadata.items())

        self.picam2.post_callback = post_callback
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (800, 600)}))
        self.picam2.start()

    def stop(self):
        self._stop_flag = True
        self.picam2.stop()
        self.wait()

class SensorThread(QThread):
    sensor_data_ready = pyqtSignal(int, int)
    exceeded_threshold = pyqtSignal(str, int)

    def __init__(self, light_sensor, smoke_sensor, main_window):
        super().__init__()
        self.light_sensor = light_sensor
        self.smoke_sensor = smoke_sensor
        self.main_window = main_window
        self.illuminance_threshold = 100
        self.smoke_threshold = 100


    def run(self):
        while True:
            illuminance = self.light_sensor.read()
            smoke = self.smoke_sensor.read()
            self.sensor_data_ready.emit(illuminance, smoke)

            # 检查是否超过阈值
            if illuminance > self.illuminance_threshold:
                self.exceeded_threshold.emit("光照", illuminance)
            if smoke > self.smoke_threshold:
                self.exceeded_threshold.emit("烟雾", smoke)
            self.msleep(5000)

    def set_illuminance_threshold(self, threshold):
        self.illuminance_threshold = int(threshold)

    def set_smoke_threshold(self, threshold):
        self.smoke_threshold = int(threshold)

class DHHThread(QThread):
    dht_data_ready = pyqtSignal(float, float)
    exceeded_threshold_dht = pyqtSignal(int)

    def __init__(self, dht11, main_window):
        super().__init__()
        self.dht11_sensor = dht11
        self.dht11_sensor.read_error.connect(self.handle_read_error)

    def run(self):
        while True:
            temperature, humidity = self.dht11_sensor.read()
            self.dht11_sensor.temperature_humidity_ready.emit(temperature, humidity)
            self.msleep(5000)

            if temperature > self.temperature_threshold:
                self.exceeded_threshold_dht.emit(temperature)

    @pyqtSlot(str)
    def handle_read_error(self, error_message):
        print(f"DHT11 read error: {error_message}")

    def set_temperature_threshold(self, threshold):
        self.temperature_threshold = float(threshold)


class AppEventFilter(QObject):
    def __init__(self, app, main_window):
        super().__init__()
        self.app = app
        self.main_window = main_window
        self.app.aboutToQuit.connect(self.cleanup)

    @pyqtSlot()
    def cleanup(self):
        self.main_window.video_thread.stop()
        self.main_window.video_thread = None
        self.main_window.dht11.close()
        self.main_window.light_sensor.close()
        self.main_window.smoke_sensor.close()
        self.main_window.buzzer.close()
        self.main_window.led.close()
        self.main_window.relay.close()
        self.app.removeEventFilter(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_labels = dict()
        # thread
        self.picam2 = Picamera2()
        self.video_thread = VideoThread(self.picam2)

        # # Sensors
        self.dht11 = DHT11("dht11", board.D18)
        self.light_sensor = LightSensor("light_sensor", 0x48, 1)
        self.smoke_sensor = SmokeSensor('smoke', 0x48, 1)

        # # Devices
        self.buzzer = Buzz("buzzer", 26)
        self.led = LED("led", 5)
        self.relay = Relay('relay', 6)

        self.init_ui()

        self.dht_thread = DHHThread(self.dht11, self)
        self.dht_thread.dht_data_ready.connect(self.update_temperature)
        self.dht_thread.exceeded_threshold_dht.connect(self.handle_exceeded_threshold_dht)
        self.sensor_thread = SensorThread(self.light_sensor, self.smoke_sensor, self)
        self.sensor_thread.sensor_data_ready.connect(self.update_ui)
        self.sensor_thread.exceeded_threshold.connect(self.handle_exceeded_threshold)

    def update_temperature(self, temperature, humidity):
        self.set_temperature(temperature)

    def update_ui(self, illuminance, smoke):
        self.set_illuminance(illuminance)
        self.set_smoke(smoke)

    @pyqtSlot(int)
    def handle_exceeded_threshold_dht(self, value):
        if value > self.dht_thread.temperature_threshold:
            self.add_message_to_status(f"温度值 {value} 超过阈值!")
            self.relay.on()

    @pyqtSlot(str, int)
    def handle_exceeded_threshold(self, sensor_type, value):
        # 处理超过阈值的情况
        if sensor_type == "光照":
            self.add_message_to_status(f"光照值 {value} 超过阈值!")
            self.led.on()
            self.led_button.setText("关")
        elif sensor_type == "烟雾":
            self.add_message_to_status(f"烟雾值 {value} 超过阈值!")
            self.buzzer.on()
            self.buzz_button.setText("关")

    def set_temperature_threshold(self):
        threshold = self.temperature_threshold_edit.text()
        try:
            threshold_value = float(threshold)
            self.dht_thread.set_temperature_threshold(threshold_value)
        except ValueError:
            # 处理无效输入
            pass

    def set_illuminance_threshold(self):
        threshold = self.illuminance_threshold_edit.text()
        try:
            threshold_value = int(threshold)
            self.sensor_thread.set_illuminance_threshold(threshold_value)
        except ValueError:
            # 处理无效输入
            pass

    def set_smoke_threshold(self):
        threshold = self.smoke_threshold_edit.text()
        try:
            threshold_value = int(threshold)
            self.sensor_thread.set_smoke_threshold(threshold_value)
        except ValueError:
            # 处理无效输入
            pass

    def init_ui(self):
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        left_widget= QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # sensor_button_layout = QVBoxLayout()
        # self.query_temperature_button = QPushButton('获取温度数据')
        # self.query_temperature_button.clicked.connect(self.get_temperature_from_sensor)
        # sensor_button_layout.addWidget(self.query_temperature_button)

        # self.query_illuminance_button = QPushButton('获取光照度数据')
        # self.query_illuminance_button.clicked.connect(self.get_illuminance_from_sensor)
        # sensor_button_layout.addWidget(self.query_illuminance_button)

        # self.query_smoke_button = QPushButton('获取烟雾数据')
        # self.query_smoke_button.clicked.connect(self.get_smoke_from_sensor)
        # sensor_button_layout.addWidget(self.query_smoke_button)

        # left_layout.addLayout(sensor_button_layout)

        sensor_layout = QVBoxLayout()

        # 温度传感器
        temperature_layout = QHBoxLayout()
        self.temperature_threshold_edit = QLineEdit()
        self.set_temperature_threshold_button = QPushButton('设置温度阈值')
        self.set_temperature_threshold_button.clicked.connect(self.set_temperature_threshold)
        temperature_layout.addWidget(QLabel('温度阈值:'))
        temperature_layout.addWidget(self.temperature_threshold_edit)
        temperature_layout.addWidget(self.set_temperature_threshold_button)
        sensor_layout.addLayout(temperature_layout)

        # 光照传感器
        illuminance_layout = QHBoxLayout()
        self.illuminance_threshold_edit = QLineEdit()
        self.set_illuminance_threshold_button = QPushButton('设置光照阈值')
        self.set_illuminance_threshold_button.clicked.connect(self.set_illuminance_threshold)
        illuminance_layout.addWidget(QLabel('光照阈值:'))
        illuminance_layout.addWidget(self.illuminance_threshold_edit)
        illuminance_layout.addWidget(self.set_illuminance_threshold_button)
        sensor_layout.addLayout(illuminance_layout)

        left_layout.addLayout(sensor_layout)

        # 烟雾传感器
        smoke_layout = QHBoxLayout()
        self.smoke_threshold_edit = QLineEdit()
        self.set_smoke_threshold_button = QPushButton('设置烟雾阈值')
        self.set_smoke_threshold_button.clicked.connect(self.set_smoke_threshold)
        smoke_layout.addWidget(QLabel('烟雾阈值:'))
        smoke_layout.addWidget(self.smoke_threshold_edit)
        smoke_layout.addWidget(self.set_smoke_threshold_button)
        sensor_layout.addLayout(smoke_layout)

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

        qpicamera2 = QGlPicamera2(self.picam2, width=800, height=600, keep_ar=False)
        qpicamera2.done_signal.connect(self.capture_done)
        right_layout.addWidget(qpicamera2, 0, 0, 7, 7)

        sensor_group = QGroupBox("传感器数据")
        sensor_layout = QVBoxLayout()
        sensor_group.setLayout(sensor_layout)

        self.create_sensor_display(sensor_layout, "温度传感器", "25°C")
        self.create_sensor_display(sensor_layout, "光照传感器", "100")
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

    def capture_done(job):
        self.picam2.wait(job)
        button.setEnabled(True)

    def add_message_to_status(self, message):
        self.status_text.appendPlainText(message)

    def setImage(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def set_temperature(self, temperature):
        self.data_labels["温度传感器"].setText(f"{temperature}°C")

    def set_illuminance(self, illuminance):
        self.data_labels["光照传感器"].setText(str(illuminance))

    def set_smoke(self, smoke):
        self.data_labels["烟雾传感器"].setText(str(smoke))

    def get_temperature_from_sensor(self):
        temperature, _ = self.dht11.read()
        self.data_labels["温度传感器"].setText(f"{temperature}°C")
        self.add_message_to_status(f"获取温度数据: {temperature}°C 成功")

    def get_illuminance_from_sensor(self):
        illumiance_analog_value = self.light_sensor.read()
        self.data_labels["光照传感器"].setText(str(illumiance_analog_value))
        self.add_message_to_status(f"获取光敏传感器数据: {illumiance_analog_value} 成功")

    def get_smoke_from_sensor(self):
        smoke_analog_value = self.smoke_sensor.read()
        self.data_labels["烟雾传感器"].setText(str(smoke_analog_value))
        self.add_message_to_status(f"获取烟雾数据: {smoke_analog_value} 成功")

    def fan_level_changed(self, value):
        print(f"选择的风扇等级: {value}")

    def control_led(self):
        if self.led_button.text() == "开":
            self.led.on()
            self.led_button.setText("关")
        elif self.led_button.text() == "关":
            self.led.off()
            self.led_button.setText("开")

    def control_buzzer(self):
        if self.buzz_button.text() == "开":
            self.buzzer.on()
            self.buzz_button.setText("关")
        elif self.buzz_button.text() == "关":
            self.buzzer.off()
            self.buzz_button.setText("开")


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    event_filter = AppEventFilter(app, main_window)
    # 启动视频渲染线程
    main_window.video_thread.start()
    main_window.dht_thread.start()
    main_window.sensor_thread.start()
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
