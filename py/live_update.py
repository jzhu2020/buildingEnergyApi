from pylive import live_plotter_xy
import numpy as np
import time
from building_data_requests import get_value

x_vec = np.full(1, 0)
kW, units = get_value('ahs', 3007360)
y_vec1 = np.full(len(x_vec), int(kW))

kW, units = get_value('west_middle-12', 3027266) # West Middle
y_vec2 = np.full(len(x_vec), int(kW))
line1 = []
line2 = []

wait_time = 5 # seconds

while True:
    kW, units = get_value('ahs', 3007360)
    y_vec1 = np.append(y_vec1, int(kW))
    x_vec = np.append(int(x_vec[0] - wait_time), x_vec)

    kW, units = get_value('west_middle-12', 3027266)  # West Middle
    y_vec2 = np.append(y_vec2, int(kW))

    line1 = live_plotter_xy(x_vec, y_vec1, line1, pause_time=wait_time, xlabel="Time (sec)", ylabel="Power (kW)", title="AHS Main Power v Time")
    line2 = live_plotter_xy(x_vec, y_vec2, line2, pause_time=wait_time, xlabel="Time (sec)", ylabel="Power (kW)", title="WMS Main Power v Time")

    if(len(x_vec) > 60 // wait_time):
        x_vec = np.delete(x_vec, 0)
        y_vec1 = np.delete(y_vec1, 0)
        y_vec2 = np.delete(y_vec2, 0)



