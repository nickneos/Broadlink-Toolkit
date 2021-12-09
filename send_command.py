from bl_common import get_device
from base64 import b64decode, binascii


def main():
    device = get_device()
    device.auth()
    sel = None

    while sel not in (['q','Q']):
        
        packet = input('\nEnter IR/RF Packet to send: \n')
        
        try :
            payload = b64decode(packet)
            device.send_data(payload)
            
            print('Packet sent\n')
            sel = input('\nPress [Q] to quit or [Enter] to send another command: \n')

        except binascii.Error:
            print('Packet not valid\n')
            sel = input('\nPress [Q] to quit or [Enter] to send another command: \n')


if __name__ == '__main__': main()