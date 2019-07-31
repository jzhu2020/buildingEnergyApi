
import sqlite3
from sqlite3 import Error
import time
from datetime import datetime

import statistics


def establish_connection(file):
    try:
        conn = sqlite3.connect(file)
        return conn
    except Error as e:
        print(e)

    return None


cubic_ft_to_gallons = 1728 / 231
number_of_days = 90 * 6
conn = establish_connection("student.sqlite")
count_default = 0


def query(connection, command):
    cursor = connection.cursor()
    cursor.execute(command)
    return cursor.fetchall()


def get_days(house):
    dates = query(conn, "Select prior_date, Water.current_date From Water Where address_street_name='{}' And address_street_number='{}' Order by prior_date Asc;".format(house[0], house[1]))
    total_days = 0
    # print dates
    previous_day = None
    for date in dates:
        # print(date)
        global count_default
        current = None
        prior = None
        try:
            current = datetime.strptime(date[1], "%Y-%m-%d %H:%M:%S")
            previous_day = current
            prior = datetime.strptime(date[0], "%Y-%m-%d %H:%M:%S")
            # print(str(current) + " " + str(prior))
            days = (current - prior).days
            total_days += days
            # print(days)
        except ValueError: # for ' - -'
            if previous_day is not None and current is not None:
                total_days += (current - previous_day).days
            else:
                total_days += 90  # default number of days
                count_default += 1
            previous_day = None
            continue
        except TypeError: # for catching 'None's
            if previous_day is not None and current is not None:
                total_days += (current - previous_day).days
            else:
                total_days += 90  # default number of days
                count_default += 1
            previous_day = None
            continue
    # print("Total: " + str(total_days))
    return total_days


def calc_average_for_houses(houses, per_household):
    averages = []
    for i in range(len(houses)):
        averages.append(per_household[i] / get_days(houses[i]))
    return averages


def calc_house_average_for_streets(streets, avg_per_house, houses_list):
    averages = []
    for i in range(len(streets)):
        houses_list = query(conn, "Select Distinct address_street_name, address_street_number From Water Where address_street_name='{}'".format(streets[i][0]))
        total_water = 0
        for house in houses_list:
            total_water += avg_per_house[houses_list.index(house)]
        averages.append(total_water / len(houses_list))
    return averages


households = query(conn, "Select Distinct address_street_name, address_street_number From Water")
streets = query(conn, "Select Distinct address_street_name From Water")

# print(query(conn, "Select Distinct prior_date From Water"))

per_household = []
for house in households:
    total = 0
    result = query(conn, "Select current_reading From Water Where address_street_name='{}' And address_street_number='{}' Order By current_reading Asc;".format(house[0], house[1]))
    # total += result[0][0]
    for i in range(len(result)):
        total += result[i][0]
        for j in range(len(result) - 1, i, -1):
            result[j] = (result[j][0] - result[i][0], )
    total -= result[0][0]

    total *= cubic_ft_to_gallons

    per_household.append(total)

print(households)
average_per_house = calc_average_for_houses(households, per_household)
print(average_per_house)


per_street = []
for street in streets:
    total = 0
    houses = query(conn, "Select address_street_name, address_street_number From Water Where address_street_name='{}';".format(street[0]))
    # total += result[0][0]
    for house in houses:
        total += per_household[households.index(house)]
    per_street.append(total)

print(streets)
average_per_house_per_street = calc_house_average_for_streets(streets, average_per_house, households)
print(average_per_house_per_street)

count_300 = 0
count_500 = 0
count_1000 = 0
for i in range(len(households)):
    if(average_per_house[i] > 300):
        count_300 += 1
    if (average_per_house[i] > 500):
        count_500 += 1
    if (average_per_house[i] > 1000):
        count_1000 += 1
print("Number of houses using >300 Gallons per day: " + str(count_300))
print("Number of houses using >500 Gallons per day: " + str(count_500))
print("Number of houses using >1000 Gallons per day: " + str(count_1000))

print(count_default)

print statistics.mean(average_per_house)
print statistics.mean(average_per_house_per_street)