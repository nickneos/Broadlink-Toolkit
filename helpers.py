from broadlink.exceptions import ReadError, StorageError
from base64 import b64encode
from datetime import datetime, timedelta
from time import sleep
from base64 import b64decode, binascii
from typing import Optional, List, Union
from broadlink import Device
import socket
import broadlink

# Default timeout in seconds for waiting for device responses
DEFAULT_TIMEOUT = 10

def get_local_ip() -> str:
    """
    Get the local IP address by creating a temporary socket connection.
    
    Returns:
        str: Local IP address, defaults to '127.0.0.1' if unable to determine
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable, just used to determine local IP
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def get_device() -> Optional[Device]:
    """
    Discovers and connects to Broadlink devices on the local network.
    
    Prompts user for:
    - WiFi SSID
    - WiFi password
    - Subnet broadcast IP address
    - Local IP address
    
    If multiple devices are found, allows user to select one.
    
    Returns:
        Optional[Device]: Connected Broadlink device instance if successful, None otherwise
    """

    # discover availabile devices on the local network
    # get ssid from user
    ssid = input("Enter WiFi SSID (or press Enter to skip WiFi setup): ").strip()
    if ssid:
        # get network password from user    
        network_password = input("Enter WiFi Network Password: ").strip()
        # get ip address from user
        ip_address = input("Enter IP Address for your subnet broadcast (e.g. 192.168.0.255): ").strip()
        
        # Validate IP address format
        if not all(x.isdigit() and 0 <= int(x) <= 255 for x in ip_address.split('.')):
            print("Invalid IP address format")
            return None
        
        broadlink.setup(ssid, network_password, 3, ip_address=ip_address)


        
    local_ip = get_local_ip()
    devices = broadlink.discover(timeout=5, local_ip_address=local_ip)

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


def get_packet(device: Device, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Attempt to receive an IR/RF packet from the device.
    
    Args:
        device: Broadlink device instance
        timeout: Maximum time to wait for packet in seconds
        
    Returns:
        Optional[str]: Base64 encoded packet if received, None otherwise
    """

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


def learn_command(device: Device, command_lbl: Optional[str] = None) -> Optional[str]:
    """
    Puts device in learning mode and waits for an IR/RF signal.
    
    Allows user to retry if no signal is received.
    
    Args:
        device: Broadlink device instance
        command_lbl: Optional label for the command being learned
        
    Returns:
        Optional[str]: Base64 encoded packet if received and user doesn't quit, None otherwise
    """
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


def send_command(device: Device, packet: str = "") -> None:
    """
    Sends an IR/RF command to the device.
    
    Continuously prompts for packets to send until user quits.
    If initial packet is provided, sends that first.
    
    Args:
        device: Broadlink device instance
        packet: Optional initial packet to send (base64 encoded string)
        
    Returns:
        None
    
    Raises:
        binascii.Error: If packet has invalid base64 encoding
    """
    try:
        device.auth()
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    while packet not in (["q", "Q"]):
        try:
            packet = (
                input("\nEnter IR/RF Packet to send or [Q] to quit: \n")
                if packet == ""
                else packet
            )

            if packet.lower() == 'q':
                break

            payload = b64decode(packet)
            device.send_data(payload)
            print("Packet sent\n")

        except binascii.Error:
            print("Invalid base64 encoding in packet")
        except Exception as e:
            print(f"Error sending packet: {e}")
