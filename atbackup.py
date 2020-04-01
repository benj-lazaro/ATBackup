from csv import reader
from datetime import datetime
import requests

# Date & Time Format
current_date = datetime.now().strftime("%Y%m%d")
current_time = datetime.now().strftime("%H:%M:%S")

# File containing the list of devices & corresponding configuration files
data_file = 'atbackup.dat'

# Directory name where to save devices' individual configuration file
config_directory = 'config'

try:
    # Open and read contents of the data file
    with open(data_file) as file:
        csv_reader = reader(file)
        next(csv_reader)

        # Read device details per line
        for device_data in csv_reader:
            ip_address = device_data[0]
            hostname = device_data[1]
            config_file = device_data[2]
            login_name = device_data[3]
            login_password = device_data[4]

            try:
                # Connect to target device
                response = requests.get(
                    'http://{}/{}/{}'.format(
                        ip_address, config_directory, config_file), auth=(
                        login_name, login_password))

                # Target device successfully connected
                if response.status_code == requests.codes.ok:
                    # Copy & Save Configuration File to /cfg Directory
                    with open('cfg/{}-{}.cfg'.format(hostname, current_date), 'w', newline='') as file:
                        file.write(response.text)

                    # Log: Target device's configuration file successfully backed up
                    with open('log/backup_success-{}.log'.format(current_date), 'a', newline='') as file:
                        file.write(
                            '{} {} ({}) successfully backup {} file.\n'.format(
                                current_time, hostname, ip_address, config_file))

                # Log: Target device's configuration file not found
                elif response.status_code == 404:
                    with open('log/backup_fail-{}.log'.format(current_date), 'a', newline='') as file:
                        file.write(
                            '{} {} ({}) {} inaccessible.\n'.format(
                                current_time, hostname, ip_address, config_file))

            # Log: Target device unreachable
            except BaseException:
                with open('log/backup_fail-{}.log'.format(current_date), 'a', newline='') as file:
                    file.write('{} {} ({}) device unreachable. \n'.format(
                        current_time, hostname, ip_address, config_file))

# log: Data file (atbackup.date) is missing
except FileNotFoundError:
    with open('log/system-{}.log'.format(current_date), 'a', newline='') as file:
        file.write(
            '*** ALERT *** {} Unable to Access Data File: {}\n'.format(current_time, data_file))
