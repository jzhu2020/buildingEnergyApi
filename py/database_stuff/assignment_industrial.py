
from helpers import *

from datetime import datetime
import statistics

conn = establish_connection("student.sqlite")
count_default = 0


def get_last_adjustment(house_address):
    adjustments = query(conn, "Select prior_date, Water.current_date From Water \
                            Where address_street_name='{}' And address_street_number='{}' And service_id='{}' And transaction_type='Adjustment' And service_type='industrial' \
                            Order by prior_date, Water.current_date Asc;".format(house_address[0], house_address[1],
                                                                                 house_address[2]))

    if len(adjustments) == 0:
        last_adjustment = "0000-00-00 00:00:00"  # the beginning of time will be before everything
    else:
        last_adjustment = adjustments[len(adjustments) - 1][1]
        if last_adjustment is None:
            last_adjustment = adjustments[len(adjustments) - 1][0]
    return last_adjustment


def get_days(house_address):  # TODO perfect time calculations (prior and current date)
    last_adjustment = get_last_adjustment(house_address)

    dates = query(conn, "Select prior_date, Water.current_date From Water \
                        Where address_street_name='{}' And address_street_number='{}' And service_id='{}' \
                        And (Water.current_date>'{}' Or prior_date>'{}') And transaction_type='Charge' And service_type='industrial' \
                        Order by prior_date, Water.current_date Asc;".format(house_address[0], house_address[1], house_address[2], last_adjustment, last_adjustment))

    try:
        first = datetime.strptime(dates[0][0], "%Y-%m-%d %H:%M:%S")
        last = datetime.strptime(dates[len(dates) - 1][1], "%Y-%m-%d %H:%M:%S")
        total_days = (last - first).days
    except:
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


households = query(conn, "Select Distinct address_street_name, address_street_number, service_id From Water Where service_type='industrial' ")
streets = query(conn, "Select Distinct address_street_name From Water Where service_type='industrial' ")

no_water_houses = []
per_household = []
for house in households:

    last_adjustment = get_last_adjustment(house)

    result = query(conn, "Select current_reading, prior_reading From Water Where address_street_name='{}' \
                        And address_street_number='{}' And service_id='{}' And (prior_reading!=current_reading or prior_reading is Null or current_reading is Null) \
                        And (prior_date!=Water.current_date or prior_date is Null or Water.current_date is Null) And (Water.current_date>'{}' Or prior_date>'{}') And transaction_type='Charge'\
                        And service_type='industrial' And prior_date<Water.current_date Order By prior_date, Water.current_date Asc;".format(house[0], house[1], house[2], last_adjustment, last_adjustment))

    # TODO properly debug this section, it likely doesn't process the readings correctly
    total = 0
    if len(result) == 0:
        per_household.append(0)
        no_water_houses.append(house)
        continue
    prev = int(result[0][0])
    for i in range(len(result)):
        if result[i][0] is not None and result[i][1] is int:
            prev = int(result[i][1])
            print "used prior"
        if int(result[i][0]) - prev < 0:
            # meter was (likely) reset
            prev = 0
        total += int(result[i][0]) - prev
        prev = int(result[i][0])

    total *= cubic_ft_to_gallons

    per_household.append(total)

average_per_house = calc_average_for_houses(households, per_household)

consumption_per_street = []
for street in streets:
    total = 0
    houses = query(conn, "Select Distinct address_street_name, address_street_number, service_id From Water \
                         Where address_street_name='{}' And service_type='industrial';".format(street[0]))
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

print("Number of sites using >300 Gallons per day: " + str(count_300))
print("Number of sites using >500 Gallons per day: " + str(count_500))
print("Number of sites using >1000 Gallons per day: " + str(count_1000))
print("Number of incomplete sets of dates: " + str(count_default))
print "Average gallons per day per sites " + str(statistics.mean(average_per_house)) + " for " + str(len(average_per_house)) + " sites"
print no_water_houses

print_to_csv("IndustrialAverageGPD.csv", household_data)
print_to_csv("IndustrialStreetAverageGPD.csv", street_data)

# TODO DOES NOT WORK BECAUSE DATA IS WEIRD
