
import pandas as pd
from sqlquery import *
from helpers import *


df = pd.read_csv("HouseAverageGPD.csv")

people_per_house = []
supposed_homeless = []

for i in range(df.shape[0]):
    people_per_house.append(0)

conn = establish_connection("student.sqlite")
people = query(conn, "Select service_id, resident_id From Lookup")

for person in people:
    person_str = person[0].encode('ascii', 'ignore')
    if person_str == '':  # attempt to use resident_id to find the address

        address = address_from_resident_id(person[1].encode('ascii', 'ignore'))
        index = df.index[(df.astype('str')['Street'] == address[0]) & (df.astype('str')['Street Address'] == str(address[1]))]

        if len(index) == 0:
            supposed_homeless.append(person)  # this is the case where we can't associate someone with a particular address' water consumption
            continue
    else:  # can use service_id to identify the person
        index = df.index[df.astype('str')['Service_ID'] == person_str].tolist()
        # print index
        if len(index) == 0:
            supposed_homeless.append(person)  # this is the case where we can't associate someone with a particular address' water consumption
            continue

    people_per_house[index[0]] += 1

print people_per_house
print sum(people_per_house)


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
    house_data.append((df['Street'][i], df['Street Address'][i], df['Service_ID'][i], df['Average Gallons Per Day'][i], consumption_per_person[i]))

# print house_data

print len(supposed_homeless)


sorted_data = sorted(house_data, key=lambda x: (x[4], x[3]))
sorted_data.reverse()

output = open("gpd_per_person.csv", "w")
output.write("Street Name,Street Address,Service ID,Gallons per day,Gallons per day per person\n")
# write to csv
for datum in sorted_data:
    output.write("{},{},{},{},{}\n".format(datum[0], datum[1], datum[2], datum[3], datum[4]))
output.close()

