from broadlink.exceptions import ReadError, StorageError
from base64 import b64encode
from datetime import datetime, timedelta
from time import sleep
from base64 import b64decode, binascii

import broadlink


def get_device():

    # discover availabile devices on the local network
    devices = broadlink.discover(timeout=5)

    # counter for device number selection
    n = 0

    # print list of devices
    for device in devices:
        n += 1
        type = device.get_type()
        mac = device.mac.hex().upper()
        mac = "".join(
            reversed([mac[i : i + 2] for i in range(0, len(mac), 2)])
        )  # fixes reversed mac
        mac = ":".join(
            mac[i : i + 2] for i in range(0, len(mac), 2)
        )  # adds ':' every 2nd char of mac
        ip = device.host[0]
        print(f"\nDevice [{n}]\nName: {type}\nIP: {ip}\nMAC: {mac}\n")

    # exit if no devices
    if n == 0:
        print("No devices found\nTry again...")
        return None

    # if 1 device discovered use that
    elif n == 1:
        print(f"Using device {n}\n")
        return devices[0]

    # when multiple devices discovered, capture device selection from user
    else:
        sel = None
        while sel not in range(1, n + 1):
            sel = int(input(f"Select a device [1-{n}]: "))
        return devices[sel - 1]


def get_packet(device, timeout=10):

    device.auth()
    device.enter_learning()

    packet = None
    start_time = datetime.now()
    timeout_time = start_time + timedelta(seconds=timeout)

    while not packet and datetime.now() < timeout_time:
        try:
            sleep(1)
            packet = device.check_data()
        except (ReadError, StorageError):
            continue

    if packet:
        return b64encode(packet).decode("utf8")
    else:
        return None


def learn_command(device, command_lbl=None):
    if command_lbl:
        prompt_txt = f"\n> Press button for {command_lbl}"
    else:
        prompt_txt = "\n> Press a button\n"

    # get packet
    print(prompt_txt)
    p = get_packet(device)

    # if no packet received, prompt to try again
    while not p:
        prompt = None

        while True:
            prompt = str(input("Nothing received. Try again?\n(Y/N) "))
            if prompt in ["Y", "y", "N", "n"]:
                break

        if prompt.strip().upper() == "N":
            break

        print(prompt_txt)
        p = get_packet(device)

    # break loop if user chooses not to try again
    if not p:
        return None

    # print packet
    print(f"{p}\n")

    return p


def send_command(device, packet=""):
    device.auth()

    while packet not in (["q", "Q"]):

        packet = (
            input("\nEnter IR/RF Packet to send or [Q] to quit: \n")
            if packet == ""
            else packet
        )

        try:
            if packet not in ["Q", "q"]:
                payload = b64decode(packet)
                device.send_data(payload)
                print("Packet sent\n")

        except binascii.Error:
            print("Packet not valid\n")
            packet = input("\nEnter IR/RF Packet to send or [Q] to quit: \n")
