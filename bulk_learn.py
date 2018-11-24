import broadlink
import time
from base64 import b64decode, b64encode
from datetime import datetime, timedelta

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
    return devices[n-1]

def get_packet(device):
 
    device.auth()
    device.enter_learning()

    packet = None
    start_time = datetime.utcnow()
    
    while packet is None and \
            (datetime.utcnow() - start_time) <= timedelta(seconds=10):
        # time.sleep(3)
        packet = device.check_data()

    if packet:
        return b64encode(packet).decode('utf8')
    
    device = None

def main(in_txt = 'input.txt', out_txt = 'output.csv', quiet_mode = False):

    device = get_device()

    f_in = open(in_txt, 'r')
    f_out = open(out_txt, 'w')

    if f_in.mode == 'r': # check to make sure that the file was opened
        
        lines = list(f_in.readlines())
        i = 0

        # loop through each command in input file
        while i < len(lines):
            line = lines[i].strip()
            print(f'\n*** Press button for {line} ***')
            p = get_packet(device)
            # if no packet received, prompt to try again
            while p is None:
                prompt = None
                while prompt not in ['Y','y','N','n']:
                    prompt = str(input('Nothing received. Try again?\n(Y/N) '))
                if prompt.strip().upper() == 'N': 
                    break     
                print(f'\n*** Press button for {line}***')
                p = get_packet(device)
            # break loop if user chooses not to try again
            if p is None:
                break
            
            # print packet
            print(f'{p}\n')

            if not quiet_mode: # when not in quiet mode, prompts for next action
                # user prompt for next action
                sel = input(f'Press:\n[ENTER] to continue\n[R] to redo last command\n[S] to stop\n')
                if sel in ['R','r']:
                    continue
                elif sel in ['S','s']:
                    f_out.write(f'{line},{p}\n')
                    break
                else:
                    f_out.write(f'{line},{p}\n')
            else: # when in quiet mode, automatically goes to next command
                f_out.write(f'{line},{p}\n')
                time.sleep(5)
            i += 1

    # close text files
    f_in.close
    f_out.close
    print(f'\nSaving to {out_txt}\n')

if __name__ == '__main__': 
    main('input.txt', 'output.csv', False)


