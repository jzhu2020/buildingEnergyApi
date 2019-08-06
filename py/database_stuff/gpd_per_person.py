
from helpers import *

import pandas as pd


df = pd.read_csv("HouseAverageGPD.csv")

people_per_house = []
independent_water = []
people_in_house = []

for i in range(df.shape[0]):
    people_per_house.append(0)
    people_in_house.append([])

conn = establish_connection("student.sqlite")
people = query(conn, "Select service_id, resident_id From Lookup")

for person in people:
    person_str = person[0].encode('ascii', 'ignore')
    index = df.index[df.astype('str')['Service_ID'] == person_str].tolist()
    # print index
    if len(index) == 0:
        independent_water.append(person)  # this is the case where we can't associate someone with a particular address' water consumption
        continue

    people_per_house[index[0]] += 1
    people_in_house[index[0]].append(person[1].encode('ascii', 'ignore'))

# print people_per_house
# print sum(people_per_house)


# Start of processing data per person

consumption_per_person = []
for index in range(len(people_per_house)):
    if people_per_house[index] <= 0:
        consumption_per_person.append(-1)
        continue
    consumption_per_person.append(float(df['Average Gallons Per Day'][index]) / people_per_house[index])

# print(consumption_per_person)

house_data = []
for i in range(len(consumption_per_person)):
    house_data.append((df['Street'][i], df['Street Address'][i], df['Service_ID'][i], df['Average Gallons Per Day'][i], consumption_per_person[i], people_in_house[i]))

# print house_data

print len(independent_water)


sorted_data = sorted(house_data, key=lambda x: (x[4], x[3]))
sorted_data.reverse()

# using calculations by hand, Andover is roughly 30 gal/day/person
town_water_total = 0
for datum in sorted_data:  # sorted_data is sorted by the number of gallons per day per person, from smallest to largest
    if datum[4] <= 0:  # we can break once we see that there are either no gallons of water or no people, because sorted
        break
    town_water_total += datum[3]  # sums up total gallons per day in the town

print "Average water use per person per day " + str(town_water_total / sum(people_per_house))

output = open("gpd_per_person.csv", "w")
output.write("Street Name,Street Address,Service ID,Gallons per day,Gallons per day per person,People\n")
# write to csv
for datum in sorted_data:
    output.write("{},{},{},{},{}\n".format(datum[0], datum[1], datum[2], datum[3], datum[4], str(datum[5])))
output.close()

