from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
from bl_common import get_device, get_packet
from time import sleep

import tkinter
import os.path
import json


def main(quiet_mode = False):

    # initialise some variables
    json_fn = ''
    cmd = {}
    suspend = False

    # select json file using gui if available
    try:
        root = tkinter.Tk()
        root.withdraw()
        useTK = True
    except tkinter.TclError:
        useTK = False

    if useTK:
        while not (os.path.isfile(json_fn)):
            print("Select the JSON config file")
            json_fn = filedialog.askopenfilename(
                title="Select json file",
                filetypes=[("JSON","*.json"),("All Files","*.*")]
            )
    else:
        json_fn = input("Enter input json: ")

        while not (os.path.isfile(json_fn)):
            print(f"{json_fn} not valid file")
            json_fn = input("Enter input filename: ")  

    device = get_device()

    # open json file
    with open(json_fn, "r") as jsonFile:
        json_in = json.load(jsonFile)

    # TODO error handling if not in json
    TempMin = int(json_in["minTemperature"])
    TempMax = int(json_in["maxTemperature"])
    TempStep = int(json_in["precision"])
    OpModes = json_in["operationModes"]
    FanModes = json_in["fanModes"]

    # add "off" to Operation Modes
    OpModes.insert(0,"off")

    # loop through operation mode, fan mode and temperature range
    for m in OpModes:
        if m == "off":
            cmd[m] = ""
            FanModes2 = ["off"]
            isOff = True
        else:
            cmd[m] = {}
            FanModes2 = FanModes
            isOff = False
        
        for f in FanModes2:
            t = TempMin
            if not isOff:
                cmd[m][f] = {}
            
            while t <= TempMax:

                # start with capturing "off" command
                if isOff:
                    button_nm = "off"
                else:
                    button_nm = f"{m}_{f}_{t}"

                # get packet for command
                print(f'\n> Press button for {button_nm}')
                p = get_packet(device)       

                # if no packet received, prompt to try again
                while p is None:
                    prompt = None
                    while prompt not in ['Y','y','N','n']:
                        prompt = str(input('Nothing received. Try again?\n(Y/N) '))
                    if prompt.strip().upper() == 'N': 
                        break     
                    print(f'\n> Press button for {button_nm}')
                    p = get_packet(device)
            
                # break loop if user chooses not to try again
                if p is None:
                    suspend = True
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
                        if isOff:
                            cmd[m] = p
                        else:
                            cmd[m][f][t] = p
                        suspend = True
                        break

                    else:
                        if isOff:
                            cmd[m] = p
                            break
                        else:
                            cmd[m][f][t] = p
                
                # when in quiet mode, automatically goes to next command
                else: 
                    sleep(1)
                    if isOff:
                        cmd[m] = p
                        break
                    else:
                        cmd[m][f][t] = p
            
                t = t + TempStep

            if suspend:
                break

        if suspend:
            break
    
    # remove off from Operation Modes
    OpModes.remove("off")

    # add dict to json and save json file
    json_in["commands"] = cmd
    json_out = json.dumps(json_in, indent=4)

    if useTK:
        print("Save output file...")
        outfile = asksaveasfile(
            initialfile = 'output.json', defaultextension=".json",
            filetypes=[("JSON","*.json"),("All Files","*.*")]
        )
    else:
        fn = input("Save output file as: ")            
        outfile = open(fn, 'w')

    outfile.write(json_out)
    print(f'\nSaving to {outfile.name}\n')

    # close text files
    jsonFile.close
    outfile.close


if __name__ == '__main__': 
    main()
