import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.lines as lns
import time

import sys
sys.path.insert(1, '/home/justin/PycharmProjects/buildingEnergyApi/py')
from building_data_requests import get_value

class MultiLineLivePlotter:

    def __init__(self, file_path):
        df = pd.read_csv(file_path)

        self.sensors = []
        self.values = []
        for index, row in df.iterrows():
            self.sensors.append((row['Label'], row['Facility'], row['Meter']))
            self.values.append(0)

        self.query_sensors()

        self.x_vecs = []
        self.y_vecs = []
        self.lines = []

        for i in range(len(self.sensors)):
            self.x_vecs.append(np.full(1, 0))
            self.y_vecs.append(np.full(1, self.values[i]))
            self.lines.append(lns.Line2D(self.x_vecs[i], self.y_vecs[i]))

        return

    def get_value(self, index):
        # queries using facility and meter
        value, self.units = get_value(self.sensors[index][1], self.sensors[index][2])
        return value

    def query_sensors(self):
        i = 0
        for sensor in self.sensors:
            self.values[i] = self.get_value(i)
            i += 1
        return

    def init_plot(self):
        plt.ion()
        fig = plt.figure(figsize=(10, 6))
        sub = fig.add_subplot(1, 1, 1)
        for i in range(len(self.sensors)):
            self.lines[i], = sub.plot(self.x_vecs[i], self.y_vecs[i], 'r-o', alpha=0.8)
        plt.xlabel("Time (sec)")
        plt.ylabel("Power (kW)")
        return

    def update_plot(self):
        for i in range(len(self.sensors)):
            self.lines[i].set_data(self.x_vecs[i], self.y_vecs[i])
            plt.xlim(np.min(self.x_vecs[i]), np.max(self.x_vecs[i]))
            if np.min(self.y_vecs[i]) <= self.lines[i].axes.get_ylim()[0] or \
                    np.max(self.y_vecs[i]) >= self.lines[i].axes.get_ylim()[1]:
                plt.ylim([np.min(self.y_vecs[i]) - np.std(self.y_vecs[i]), np.max(self.y_vecs[i]) + np.std(self.y_vecs[i])])
        return


plotter = MultiLineLivePlotter("../../csv/ahs_power.csv")
plotter.init_plot()

while True:
    time.sleep(5)
    plotter.update_plot()

