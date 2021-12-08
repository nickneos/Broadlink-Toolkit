import broadlink
from broadlink.exceptions import ReadError,StorageError
import time
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
import os.path


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
        print(f'Device [{n}]\nName: {type}\nIP: {ip}\nMAC: {mac}\n')

    # exit if no devices
    if n == 0:
        print('No devices found\nTry agin...')
        return None

    # capture device selection from user
    sel = None
    while sel not in range(1,n+1):
        sel = int(input(f'Select a device [1-{n}]: '))
    return devices[sel-1]

def get_packet(device):
 
    device.auth()
    device.enter_learning()

    packet = None
    start_time = datetime.utcnow()
    
    while packet is None and \
            (datetime.utcnow() - start_time) <= timedelta(seconds=30):
        try:
            time.sleep(1)
            packet = device.check_data()
        except (ReadError, StorageError):
            continue

    if packet:
        return b64encode(packet).decode('utf8')
    
    device = None


def main(quiet_mode = False):

    # initialise some variables
    output = ""
    fn = ""

    # select input file
    try:
        root = tk.Tk()
        root.withdraw()
        useTK = True

    except tk.TclError:
        useTK = False

    if useTK:
        while not (os.path.isfile(fn)):
            print("Select the input file")
            fn = filedialog.askopenfilename(title="Select input file",filetypes=[("Text Documents","*.txt"),("CSV","*.csv"),("All Files","*.*")])
    
    else:
        fn = input("Enter input filename: ")
    
        while not (os.path.isfile(fn)):
            print(f"{fn} not valid file")
            fn = input("Enter input filename: ")        
    
    input_file = open(fn, 'r')

    # get broadlink device
    device = get_device()

    # check to make sure that the file was opened
    if input_file.mode == 'r': 

        commands = list(input_file.readlines())
        i = 0

        # loop through each command in input file
        while i < len(commands):
            
            # get packet for command
            cmnd = commands[i].strip()
            print(f'\n*** Press button for {cmnd} ***')
            p = get_packet(device)

            # if no packet received, prompt to try again
            while p is None:
                prompt = None
                while prompt not in ['Y','y','N','n']:
                    prompt = str(input('Nothing received. Try again?\n(Y/N) '))
                if prompt.strip().upper() == 'N': 
                    break     
                print(f'\n*** Press button for {cmnd}***')
                p = get_packet(device)
                
            # break loop if user chooses not to try again
            if p is None:
                break
            
            # print packet
            print(f'{p}\n')


            # quiet mode doesn't prompt for next action
            if not quiet_mode: 
                # user prompt for next action
                sel = input(f'Press:\n[ENTER] to continue\n[R] to redo last command\n[S] to stop\n')
                if sel in ['R','r']:
                    continue
                elif sel in ['S','s']:
                    output += f'{cmnd},{p}\n'
                    break
                else:
                    output += (f'{cmnd},{p}\n')
            else: # when in quiet mode, automatically goes to next command
                output += (f'{cmnd},{p}\n')
                time.sleep(1)

            i += 1

    # create file for output of codes
    if useTK:
        print("Save output file of codes as...")
        output_file = asksaveasfile(initialfile = 'Output.csv', defaultextension=".csv",filetypes=[("All Files","*.*"),("Text Documents","*.txt"),("CSV","*.csv")])

    else:
        fn = input("Save output file of codes as: ")            
        output_file = open(fn, 'w')

    output_file.write(output)

    # close text files
    input_file.close
    output_file.close


if __name__ == '__main__':
    main()


