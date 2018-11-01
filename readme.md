## bulk_learn.py

I created this python script to speed up the process of learning IR commands for my air conditioner.

This python script will take a list of supplied command names from input.txt, and prompt you to press the corresponding button on your remote control. Once complete, it will output the learned packets to a csv file (output.csv) which can then be opened in a text editor of your choice or excel.

## Requirements
* [Python 3](https://www.python.org/downloads/)
* **Broadlink Module** for python, which can be installed by typing the below in a terminal/command prompt
```
pip install broadlink
```
To run the script in windows as an example, open command prompt from where the script is saved and run:
```
python bulk_learn.py
```


