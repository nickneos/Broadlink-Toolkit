
# Broadlink Toolkit

Python scripts to speed up learning and sending IR commands on a Broadlink device

## Requirements
* [Python 3](https://www.python.org/downloads/)
* **Broadlink Module** for python, which can be installed with pip
```
pip3 install broadlink
```

### bulk_learn.py
I created this python script to speed up the process of learning IR commands for my air conditioner.

This python script will take a list of supplied command names from an input file (`refer to input_exaple.txt`) and prompt you to press the corresponding button on your remote control. Once complete, it will output the learned packets to an output csv file which can then be opened in a text editor of your choice or excel.

```
python3 bulk_learn.py
```

### smartir_generator.py

This is like the `bulk_learn.py` script, except it's specifically designed to create a json file to use for climate devices with [SmartIR](https://github.com/smartHomeHub/SmartIR/).

It will prompt for a json file to get started. Refer to `example.json` on the details needed for the input json file.

```
python3 smartir_generator.py
```

### send_command.py
Run this script if you wish to test out sending IR packets from your Broadlink device.

```
python3 send_command.py
```

<hr>

<a href="https://www.buymeacoffee.com/so3n" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
