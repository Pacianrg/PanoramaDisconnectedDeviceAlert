import datetime
import config
import pickle
import xml.etree.ElementTree as ET
import smtplib
from panos import panorama
import os

# Username and password for Panorama
username = config.USERNAME
password = config.PASSWORD
hostname = config.HOSTNAME

# SMTP Connection
from_email = config.FROM_EMAIL
to_email = config.TO_EMAIL
smtp_server = config.SMTP_SERVER
smtp_port = 25

# Current time for recording how long a device was down
currentTime = datetime.datetime.now().timestamp()

# Create the pickle file path
pickleFilePath = config.FILE_PATH

# Load disconnected device status from file
try:
    with open(pickleFilePath, "rb") as f:
        disconnectedDevices = pickle.load(f)
except Exception as e:
    print(f'Failed to load disconnected devices: {e} Making new file.')
    disconnectedDevices = {}

try:
    # Connect to Panorama with panos
    panConnect = panorama.Panorama(hostname, username, password)
    devices = panConnect.op(cmd='show devices all', xml=True)
except Exception as e:
    print(f'Error connecting to Panorama: {e}')
    exit()

# Pull devices from the XML in the prior operational command
try:
    responseXml = ET.fromstring(devices)
except Exception as e:
    print(f'Failed XML parse: {e}')

# Check currently connected devices
try:
    for deviceEntry in responseXml.iter('entry'):
        connected = deviceEntry.find('.//connected')
        hostname = deviceEntry.find('.//hostname')
        if connected is not None:
            connected = deviceEntry.find('.//connected').text
            if hostname is not None:
                hostname = deviceEntry.find('.//hostname').text
                # Alert on down devices that haven't already been down
                if connected != 'yes' and hostname not in disconnectedDevices:
                    # Record device and time it went down
                    disconnectedDevices[hostname] = currentTime
                    # Alert device is down
                    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                        message = f'Subject: {hostname} is down\n\nDevice {hostname} is disconnected from Panorama.'
                        smtp.starttls()
                        smtp.sendmail(from_email, to_email, message)
                # Check if device is up after being down
                if connected == 'yes' and hostname in disconnectedDevices:
                    # Calculate time between it going down and coming back up
                    downTime = disconnectedDevices[hostname]
                    upTime = currentTime
                    timeDifference = int(upTime) - int(downTime)
                    hours, remainder = divmod(timeDifference, 3600)
                    minutes, _ = divmod(remainder, 60)
                    # Send message of device coming up and the time it took
                    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                        message = f'Subject: {hostname} is up\n\nDevice {hostname} is connected to Panorama ' \
                                  f'after {hours} hours and {minutes} minutes'
                        smtp.starttls()
                        smtp.sendmail(from_email, to_email, message)
                    # Update file storing devices
                    disconnectedDevices.pop(hostname, None)
except Exception as e:
    print(f'Error when parsing devices: {e}')
try:
    with open(pickleFilePath, 'wb') as f:
        pickle.dump(disconnectedDevices, f)
except Exception as e:
    print(f'Failed to save disconnected devices {e}')
