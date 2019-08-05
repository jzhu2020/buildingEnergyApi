
from sqlquery import *

cubic_ft_to_gallons = float(float(1728) / float(231))
conn = establish_connection("student.sqlite")

def print_to_csv(file_name, list, header, size):
    file = open(file_name, "w")
    file.write(header)
    for data in list:
        for i in range(size - 1):
            file.write(str(data[i]) + ",")
        file.write(str(data[size - 1]) + "\n")
    file.close()


def address_from_resident_id(id):
    address = query(conn, "Select residential_address_street_name, residential_address_street_number From Census Where resident_id='{}';".format(id))[0]
    return address

