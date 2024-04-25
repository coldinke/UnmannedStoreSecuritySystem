from gui import *


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