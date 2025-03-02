import json
import argparse
from base64 import b64decode
from broadlink import Device
from helpers import get_device, send_command

def parse_args():
    parser = argparse.ArgumentParser(description='Send IR commands from a SmartIR JSON file')
    parser.add_argument('filename', help='Path to the SmartIR JSON file')
    return parser.parse_args()

def load_commands(filename):
    """Load and parse the SmartIR JSON file"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}")
        return None

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Load commands from JSON file
    data = load_commands(args.filename)
    if not data:
        return

    # Get Broadlink device
    device = get_device()
    if not device:
        print("No device found")
        return

    # Print available modes and commands
    print("\nAvailable modes:")
    for mode in data["operationModes"]:
        print(f"- {mode}")

    print("\nAvailable fan speeds:")
    for fan in data["fanModes"]:
        print(f"- {fan}")

    print("\nTemperature range:")
    print(f"Min: {data['minTemperature']}°C")
    print(f"Max: {data['maxTemperature']}°C")
    print(f"Step: {data['precision']}°C")

    # Main interaction loop
    while True:
        print("\nEnter command (or 'q' to quit):")
        print("Format: <mode> <fan_speed> <temperature>")
        print("Example: cool auto 23")
        print("For power off, just type: off")

        cmd = input("> ").strip().lower()
        if cmd == 'q':
            break
        
        if cmd == 'off':
            code = data["commands"]["off"]
            send_command(device, code)
            continue

        try:
            mode, fan, temp = cmd.split()
            temp = float(temp)

            # Validate inputs
            if mode not in data["operationModes"]:
                print(f"Invalid mode. Available modes: {', '.join(data['operationModes'])}")
                continue

            if fan not in data["fanModes"]:
                print(f"Invalid fan speed. Available speeds: {', '.join(data['fanModes'])}")
                continue

            if not (data["minTemperature"] <= temp <= data["maxTemperature"]):
                print(f"Temperature must be between {data['minTemperature']} and {data['maxTemperature']}")
                continue

            # Get the IR code
            code = data["commands"][mode][fan][str(int(temp))]
            send_command(device, code)

        except ValueError:
            print("Invalid command format. Use: <mode> <fan_speed> <temperature>")
        except KeyError:
            print("Command not found in the database")

if __name__ == "__main__":
    main()
    