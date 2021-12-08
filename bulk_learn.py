from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
from bl_common import get_device, get_packet
from time import sleep

import tkinter
import os.path


def main(quiet_mode = False):

    # initialise some variables
    output = ""
    fn = ""

    # select input file using gui if available
    try:
        root = tkinter.Tk()
        root.withdraw()
        useTK = True
    except tkinter.TclError:
        useTK = False

    if useTK:
        while not (os.path.isfile(fn)):
            print("Select the input file")
            fn = filedialog.askopenfilename(
                title="Select input file",
                filetypes=[("Text Documents","*.txt"),("CSV","*.csv"),("All Files","*.*")]
            )
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
            print(f'\n> Press button for {cmnd}')
            p = get_packet(device)

            # if no packet received, prompt to try again
            while p is None:
                prompt = None
                while prompt not in ['Y','y','N','n']:
                    prompt = str(input('Nothing received. Try again?\n(Y/N) '))
                if prompt.strip().upper() == 'N': 
                    break     
                print(f'\n> Press button for {cmnd}')
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
                sleep(1)

            i += 1

    # create file for output of codes
    if useTK:
        print("Save output file of codes as...")
        output_file = asksaveasfile(
            initialfile = 'output.csv', defaultextension=".csv",
            filetypes=[("CSV","*.csv"),("Text Documents","*.txt"),("All Files","*.*")]
        )
    else:
        fn = input("Save output file of codes as: ")            
        output_file = open(fn, 'w')

    output_file.write(output)

    # close text files
    input_file.close
    output_file.close


if __name__ == '__main__':
    main()
