
import pandas as pd
from sqlquery import *

df = pd.read_csv("HouseAverageGPD.csv")

people_per_house = []

for i in range(df.shape[0]):
    people_per_house.append(0)

conn = establish_connection("student.sqlite")
people = query(conn, "Select service_id From Lookup")

for person in people:
    # print person
    person_str = person[0].encode('ascii', 'ignore')
    if person_str == '':
        continue

    index = df.index[df.astype('str')['Service_ID'] == person_str]
    # print(index)

    if len(index) == 0:
        # print person_str
        continue
    people_per_house[index[0]] += 1

print people_per_house
print sum(people_per_house)

consumption_per_person = []
for index in range(len(people_per_house)):
    if people_per_house[index] <= 0:
        consumption_per_person.append(-1)
        continue
    consumption_per_person.append(float(df['Average Gallons Per Day'][index]) / people_per_house[index])

print(consumption_per_person)

house_data = []
for i in range(len(consumption_per_person)):
    house_data.append((df['Street'][i], df['Street Address'][i], df['Service_ID'][i], df['Average Gallons Per Day'][i], consumption_per_person[i]))

print house_data


sorted_data = sorted(house_data, key=lambda x: x[4])
sorted_data.reverse()

print sorted_data
