from pylive import live_plotter_xy
import numpy as np
import time

import sys
sys.path.insert(1, '/home/justin/PycharmProjects/buildingEnergyApi/py')
from building_data_requests import get_value

class SensorGrapher:

    def __init__(self, facility, sensor, wait_time=5, max_time=60):
        self.facility = facility
        self.sensor = sensor
        self.wait_time = wait_time
        self.max_time = max_time

    def get_value(self):
        return get_value(self.facility, self.sensor)

    def init_plot(self):
        self.x_vec = np.full(1, 0)
        kW, units = self.get_value()
        self.y_vec = np.full(len(self.x_vec), int(kW))
        self.line = []

    def update_plot(self):
        kW, units = self.get_value()
        self.y_vec = np.append(self.y_vec, int(kW))
        self.x_vec = np.append(int(self.x_vec[0] - self.wait_time), self.x_vec)

        self.line = live_plotter_xy(self.x_vec, self.y_vec, self.line, pause_time=self.wait_time, xlabel="Time (sec)", ylabel="Power ({})".format(units),
                                title=self.facility + " Power v Time")

        if (len(self.x_vec) > self.max_time // self.wait_time):
            self.x_vec = np.delete(self.x_vec, 0)
            self.y_vec = np.delete(self.y_vec, 0)

#
# tracker = SensorGrapher('ahs', 3007360)
# tracker.init_plot()
# while True:
#     tracker.update_plot()