from broadlink.exceptions import ReadError,StorageError
from base64 import b64encode
from datetime import datetime
from time import sleep

import broadlink

def get_device():
          
    # discover availabile devices on the local network
    devices = broadlink.discover(timeout=5)

    # counter for device number selection
    n=0

    # print list of devices
    for device in devices:
        n += 1
        type = device.get_type()
        mac = device.mac.hex().upper()
        mac = "".join(reversed([mac[i:i+2] for i in range(0, len(mac), 2)])) # fixes reversed mac
        mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2)) # adds ':' every 2nd char of mac
        ip = device.host[0]
        print(f'\nDevice [{n}]\nName: {type}\nIP: {ip}\nMAC: {mac}\n')

    # exit if no devices
    if n == 0:
        print('No devices found\nTry again...')
        return None

    # if 1 device discovered use that
    elif n == 1:
        print(f'Using device {n}\n')
        return devices[0]

    # when multiple devices discovered, capture device selection from user
    else:
        sel = None
        while sel not in range(1,n+1):
            sel = int(input(f'Select a device [1-{n}]: '))
        return devices[sel-1]


def get_packet(device, timeout = 10):
 
    device.auth()
    device.enter_learning()

    packet = None
    start_time = datetime.utcnow()
    
    while packet is None and \
            (datetime.utcnow() - start_time).total_seconds() <= timeout:
        try:
            sleep(1)
            packet = device.check_data()
        except (ReadError, StorageError):
            continue

    if packet:
        return b64encode(packet).decode('utf8')
    
    device = None
