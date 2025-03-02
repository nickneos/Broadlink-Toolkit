import json
import argparse
from typing import Dict, List, Union, Optional, Any, Literal
import broadlink  # Added for type hints

# my modules
from helpers import get_device, learn_command

# Define custom types
JsonDict = Dict[str, Any]
CommandDict = Dict[str, Union[str, Dict[str, Dict[str, str]]]]
ActionType = Literal["redo", "stop", "continue"]
Temperature = Union[int, float, str]

def main() -> None:

    # initialise some variables
    suspend: bool = False
    args = parse_args()
    json_config: str = args.json_file

    try:
        # read json file to dict
        with open(json_config, "r") as fp:
            ac_dict: JsonDict = json.load(fp)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file: {e}")
        return

    # get broadlink device
    device: Optional[broadlink.Device] = get_device()
    if device is None:
        return

    # get config values with type validation
    try:
        min_temp: int = int(ac_dict.get("minTemperature", 18))
        max_temp: int = int(ac_dict.get("maxTemperature", 30))
        temp_step: int = int(ac_dict.get("precision", 1))
        if min_temp > max_temp or temp_step <= 0:
            raise ValueError("Invalid temperature configuration")
    except ValueError as e:
        print(f"Error in temperature configuration: {e}")
        return
    op_modes: List[str] = ac_dict.get("operationModes", ["cool", "heat"])
    fan_modes: List[str] = ac_dict.get("fanModes", ["auto"])
    commands: CommandDict = ac_dict.get("commands", {})

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
            temp: int = min_temp
            while temp <= max_temp:
                try:
                    temp_key = clean_temp(temp)
                    if temp_key in commands[op_mode][fan_mode]:
                        temp += temp_step
                        continue

                    # label for command
                    lbl: str = "off" if op_mode == "off" else f"{op_mode}_{fan_mode}_{temp_key}"

                    # get packet
                    pkt: Optional[str] = learn_command(device, lbl)
                    if pkt is None:
                        print("Failed to learn command")
                        continue

                    # get next action
                    action: ActionType = prompt_next_action()

                    # save command to json if action is continue or stop
                    if action in ["continue", "stop"]:
                        if op_mode == "off":
                            commands["off"] = pkt
                        else:
                            commands[op_mode][fan_mode][temp_key] = pkt
                        
                        if not update_json(json_config, commands):
                            print("Failed to update JSON file")
                            return

                        # break out if action was stop
                        if action == "stop":
                            suspend = True
                            break

                        # increment temp
                        temp += temp_step
                    # redo command if action is redo
                    else:
                        continue

                except ValueError as e:
                    print(f"Error processing temperature: {e}")
                    continue

                if op_mode == "off":
                    break

            if op_mode == "off":
                break


def prompt_next_action() -> ActionType:
    """Prompt user for next action

    Returns:
        ActionType: one of "redo", "stop" or "continue"
    """

    sel = input(f"Press:\n[ENTER] to continue\n[R] to redo last command\n[S] to stop\n")

    if sel in ["R", "r"]:
        return "redo"
    elif sel in ["S", "s"]:
        return "stop"
    else:
        return "continue"


def update_json(json_config_file: str, commands_dict: CommandDict) -> bool:
    try:
        with open(json_config_file, "r") as fp:
            config_dict: JsonDict = json.load(fp)

        config_dict["commands"] = commands_dict

        with open(json_config_file, "w") as fp:
            json.dump(config_dict, fp, indent=4)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error updating JSON file: {e}")
        return False
    return True


def clean_temp(temp: Temperature) -> str:
    """Convert temperature to standardized string format

    Args:
        temp: Temperature value to clean

    Returns:
        str: Cleaned temperature string

    Raises:
        ValueError: If temperature format is invalid
    """
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


def parse_args() -> argparse.Namespace:
    # cli arguments
    parser = argparse.ArgumentParser(
        description="Generates json file of Climate IR commands for SmartIR Home Assistant integration"
    )
    parser.add_argument("json_file", metavar="JSON-FILE", help="SmartIR json file to update")

    return parser.parse_args()

if __name__ == "__main__":
    main()
