
import sys
sys.path.insert(1, '/home/justin/PycharmProjects/buildingEnergyApi/py/better_name_later')
import SensorGrapher

sensors_file = open("../../csv/ahs_power.csv", "r")

lines = sensors_file.readlines()

print(lines)

sensors = []

for line in lines:
    if len(line) < 6:
        continue
    label, facility, meter_ = line.split(",")

    meter = meter_.split("\n")[0]

    print(label)
    print(facility)
    print(meter)
    print

    if(label == "Label"):
        continue

    sensor = SensorGrapher.SensorGrapher(facility, meter)
    sensor.init_plot()
    sensors.append(sensor)



while True:
    for sensor in sensors:
        sensor.update_plot()