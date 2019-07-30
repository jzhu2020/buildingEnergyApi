import matplotlib.pyplot as plt
import time
from building_data_requests import get_value

value, units = get_value( 'ahs', 3007360 )

xar = [0]
yar = [value]

# copied and modified from https://pythonprogramming.net/live-graphs-matplotlib-tutorial/
import matplotlib.animation as animation

fig = plt.figure(figsize=(10, 10))
ax1 = fig.add_subplot(1,1,1)

def animate(i):
    value, units = get_value('ahs', 3007360) # AHS Main (electricity)

    xar.insert(0, -1 * len(xar))
    yar.append(value)

    ax1.clear()
    plt.xlabel("seconds", fontsize=20)
    plt.ylabel(units, fontsize=20)
    ax1.plot(xar,yar)

    time.sleep(1)

fig.suptitle("AHS Main Power v Time", fontsize=20)
# fig.set_title("AHS Main")
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.xlabel("seconds", fontsize=20)
plt.ylabel(units, fontsize=20)
plt.show()