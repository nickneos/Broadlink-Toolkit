import json
import argparse

# my modules
from helpers import get_device, learn_command


def main():

    # initialise some variables
    suspend = False
    args = parse_args()
    json_config = args.json_file

    # read json file to dict
    with open(json_config, "r") as fp:
        ac_dict = json.load(fp)

    # get broadlink device
    device = get_device()

    # get config values
    min_temp = int(ac_dict.get("minTemperature", 18))
    max_temp = int(ac_dict.get("maxTemperature", 30))
    temp_step = int(ac_dict.get("precision", 1))
    op_modes = ac_dict.get("operationModes", ["cool", "heat"])
    fan_modes = ac_dict.get("fanModes", ["auto"])
    commands = ac_dict.get("commands", {})

    # loop through operation modes
    for op_mode in ["off"] + op_modes:
        if suspend:
            break

        # skip over off command if already in config
        if op_mode == "off" and "off" in commands:
            continue

        # initialise operation mode dictionary
        if op_mode not in commands:
            commands[op_mode] = {}

        # loop through fan modes
        for fan_mode in fan_modes:
            if suspend:
                break

            # initialise fan mode dictionary
            if fan_mode not in commands[op_mode]:
                commands[op_mode][fan_mode] = {}

            # loop through temps
            temp = min_temp
            while temp <= max_temp:

                # skip temp if already in config
                if clean_temp(temp) in commands[op_mode][fan_mode]:
                    temp += temp_step
                    continue

                # label for command
                if op_mode == "off":
                    lbl = "off" 
                else:
                    lbl = f"{op_mode}_{fan_mode}_{clean_temp(temp)}"

                # get packet
                pkt = learn_command(device, lbl)

                # get next action
                action = prompt_next_action()

                # save command to json if action is continue or stop
                if action in ["continue", "stop"]:

                    if op_mode == "off":
                        commands["off"] = pkt
                    else:
                        commands[op_mode][fan_mode][clean_temp(temp)] = pkt
                    
                    update_json(json_config, commands)

                    # break out if action was stop
                    if action == "stop":
                        suspend = True
                        break

                    # increment temp
                    temp += temp_step

                # redo command if action is redo
                else:
                    continue

                if op_mode == "off":
                    break

            if op_mode == "off":
                break


def prompt_next_action():
    """Prompt user for next action

    Returns:
        str: one of "redo", "stop" or "continue"
    """

    sel = input(f"Press:\n[ENTER] to continue\n[R] to redo last command\n[S] to stop\n")

    if sel in ["R", "r"]:
        return "redo"
    elif sel in ["S", "s"]:
        return "stop"
    else:
        return "continue"


def update_json(json_config_file, commands_dict):

    with open(json_config_file, "r") as fp:
        config_dict = json.load(fp)

    config_dict["commands"] = commands_dict

    with open(json_config_file, "w") as fp:
        json.dump(config_dict, fp, indent=4)


def clean_temp(temp):

    if isinstance(temp, int):
        return str(temp)
    elif isinstance(temp, float):
        if int(temp) == temp:
            return str(int(temp))
        else:
            return str(temp)
    elif isinstance(temp, str):
        return temp
    else:
        raise ValueError(f"Temperature: {temp} not valid")


def parse_args():
    # cli arguments
    parser = argparse.ArgumentParser(
        description="Generates json file of Climate IR commands for SmartIR Home Assistant integration"
    )
    parser.add_argument("json_file", metavar="JSON-FILE", help="SmartIR json file to update")

    return parser.parse_args()

if __name__ == "__main__":
    main()
