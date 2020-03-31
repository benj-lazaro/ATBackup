from csv import reader
from datetime import datetime
import requests

# Date & Time Format
current_date = datetime.now().strftime("%Y%m%d")
current_time = datetime.now().strftime("%H:%M:%S")

# Filename of CSV-format File (.csv or .dat filename extension)
data_file = 'atbackup.dat'

# Directory Name
config_directory = 'test'

try:
    with open(data_file) as file:
        csv_reader = reader(file)
        next(csv_reader)

        for device_data in csv_reader:
            ip_address = device_data[0]
            hostname = device_data[1]
            config_file = device_data[2]
            login_name = device_data[3]
            login_password = device_data[4]

            try:
                # Connect To Device via HTTP
                response = requests.get(
                    'http://{}/{}/{}'.format(
                        ip_address, config_directory, config_file), auth=(
                        login_name, login_password))

                # Device Connectivity Established (Status Code 200)
                if response.status_code == requests.codes.ok:
                    with open('cfg/{}-{}.cfg'.format(hostname, current_date), 'w', newline='') as file:
                        file.write(response.text)

                    with open('log/backup_success-{}.log'.format(current_date), 'a', newline='') as file:
                        file.write(
                            '{} {} ({}) successfully backup {} file.\n'.format(
                                current_time, hostname, ip_address, config_file))

                # Active Configuration File Not Found (Status Code 404)
                elif response.status_code == 404:
                    with open('log/backup_fail-{}.log'.format(current_date), 'a', newline='') as file:
                        file.write(
                            '{} {} ({}) {} inaccessible.\n'.format(
                                current_time, hostname, ip_address, config_file))

            # Write To Log File: Device Unreachable
            except BaseException:
                with open('log/backup_fail-{}.log'.format(current_date), 'a', newline='') as file:
                    file.write('{} {} ({}) device unreachable. \n'.format(
                        current_time, hostname, ip_address, config_file))

# Write To Log File: Active Configuration File Not Found
except FileNotFoundError:
    with open('log/system-{}.log'.format(current_date), 'a', newline='') as file:
        file.write(
            '*** ALERT *** {} Unable to Access Data File: {}\n'.format(current_time, data_file))
