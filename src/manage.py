class Manager:
    def __init__(self, name):
        self.name = name
        self.sensors = list()

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def delete_sensor(self, sensor):
        self.sensors.remove(sensor)

    
