import broadlink
from base64 import b64encode, b64decode

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
        mac = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2)) # adds ':' every 2nd char of mac
        ip = device.host[0]
        print(f'Device [{n}]\nName: {type}\nIP: {ip}\nMAC: {mac}\n')

    # exit if no devices
    if n == 0:
        print('No devices found\nTry agin...')
        return None

    # capture device selection from user
    sel = None
    while sel not in range(1,n+1):
        sel = int(input(f'Select a device [1-{n}]: '))
    return devices[n-1]

def main():
    device = get_device()
    device.auth()
    sel = None

    while sel not in (['q','Q']):
        packet = input('Enter IR/RF Packet to send: \n')
        payload = b64decode(packet)
        device.send_data(payload)
        print('Packet sent')
        sel = input('Press [Q] to quite or [Enter] to send another command: ')


if __name__ == '__main__': main()