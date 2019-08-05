
from sqlquery import *
from datetime import datetime

import statistics


cubic_ft_to_gallons = float(float(1728) / float(231))
number_of_days = 90 * 6
conn = establish_connection("student.sqlite")
count_default = 0


def get_days(house_address):
    dates = query(conn, "Select prior_date, Water.current_date From Water \
                        Where address_street_name='{}' And address_street_number='{}' And service_id='{}' And transaction_type='Charge' \
                        Order by prior_date, Water.current_date Asc;".format(house_address[0], house_address[1], house_address[2]))

    try:
        first = datetime.strptime(dates[0][0], "%Y-%m-%d %H:%M:%S")
        last = datetime.strptime(dates[len(dates) - 1][0], "%Y-%m-%d %H:%M:%S")
        total_days = (last - first).days
    except:
        global count_default
        total_days = len(dates) * 90
        count_default += len(dates)
    return total_days


def calc_average_for_houses(houses, per_household):
    averages = []
    for index in range(len(houses)):
        days = get_days(houses[index])
        if days == 0:
            print houses[index]  # TODO remove debugging prints
        averages.append(per_household[index] / (-1 if days == 0 else days))
    return averages


def print_to_csv(file_loc, data):
    # this function assumes you are passing in a list with items in the format of: (tuple, int)
    f = open(file_loc, "w")
    # data[0] should be a tuple
    is_houses = len(data[0][0]) >= 2 # it's a household (it has a street address number), otherwise, it's a street
    f.write("Street,Street Address,Service_ID,Average Gallons Per Day\n" if is_houses else "Street,Average Gallons Per Day\n")
    for i in range(len(data)):
        f.write("{},{},{},".format(data[i][0][0], data[i][0][1], data[i][0][2]) if is_houses else "{},".format(data[i][0][0]))

        # print average gallons per day
        f.write("{}\n".format(data[i][1]))
    f.close()


households = query(conn, "Select Distinct address_street_name, address_street_number, service_id From Water")
streets = query(conn, "Select Distinct address_street_name From Water")


per_household = []
for house in households:
    result = query(conn, "Select current_reading From Water Where address_street_name='{}' \
                         And address_street_number='{}' And service_id='{}' And prior_reading!=current_reading \
                         And prior_date!=Water.current_date  And transaction_type='Charge' \
                         Order By prior_date, Water.current_date Asc;".format(house[0], house[1], house[2]))
    prior_reading = query(conn, "Select prior_reading From Water Where address_street_name='{}' \
                         And address_street_number='{}' And service_id='{}' And prior_reading!=current_reading \
                         And prior_date!=Water.current_date And transaction_type='Charge' \
                         Order By prior_date, Water.current_date Asc;".format(house[0], house[1], house[2]))

    total = 0
    if len(result) == 0:
        per_household.append(0)
        continue
    prev = result[0][0]
    for i in range(len(result)):
        if prior_reading[i][0] is not None and prior_reading[i][0] is int:
            prev = prior_reading[i][0]
        if result[i][0] - prev < 0:
            # meter was (likely) reset
            prev = 0
        total += result[i][0] - prev
        prev = result[i][0]

    total *= cubic_ft_to_gallons

    per_household.append(total)

average_per_house = calc_average_for_houses(households, per_household)

consumption_per_street = []
for street in streets:
    total = 0
    houses = query(conn, "Select Distinct address_street_name, address_street_number, service_id From Water \
                         Where address_street_name='{}';".format(street[0]))
    for house in houses:
        total += average_per_house[households.index(house)]
    consumption_per_street.append(total)


household_data = []
for i in range(len(households)):
    household_data.append((households[i], average_per_house[i]))

# merge streets and average_per_house_per_street
street_data = []
for i in range(len(streets)):
    street_data.append((streets[i], consumption_per_street[i]))

count_300 = 0
count_500 = 0
count_1000 = 0
for i in range(len(households)):
    if average_per_house[i] > 300:
        count_300 += 1
    if average_per_house[i] > 500:
        count_500 += 1
    if average_per_house[i] > 1000:
        count_1000 += 1

print("Number of houses using >300 Gallons per day: " + str(count_300))
print("Number of houses using >500 Gallons per day: " + str(count_500))
print("Number of houses using >1000 Gallons per day: " + str(count_1000))
print("Number of incomplete sets of dates: " + str(count_default))
print "Average gallons per day per household " + str(statistics.mean(average_per_house))

print_to_csv("HouseAverageGPD.csv", household_data)
print_to_csv("StreetAverageGPD.csv", street_data)


# Copied from https://stackoverflow.com/questions/17684610/python-convert-csv-to-xlsx
import os
import glob
import csv
from xlsxwriter.workbook import Workbook


for csvfile in glob.glob(os.path.join('.', '*.csv')):
    workbook = Workbook(csvfile[:-4] + '.xlsx')
    worksheet = workbook.add_worksheet()
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()
