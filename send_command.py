from bl_common import get_device
from base64 import b64decode, binascii


def main():
    device = get_device()
    device.auth()
    packet = ""

    while packet not in (["q","Q"]):
        
        packet = input("\nEnter IR/RF Packet to send or [Q] to quit: \n")
        
        try :
            if packet not in ["Q","q"]:
                payload = b64decode(packet)
                device.send_data(payload)
                print("Packet sent\n")
            
        except binascii.Error:
            print("Packet not valid\n")
            packet = input("\nEnter IR/RF Packet to send or [Q] to quit: \n")


if __name__ == "__main__": main()