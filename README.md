# SPRINT 3 PRODUCT DEMO

## Authors: James Kluz, Xiangru Qian, Aviv Sheriff 

### To Do:
- basic refactoring and test code removal

## Requirements:
- python 2.7
- Adafruit_BlueFruitLE -> arduino / python
- Adafruit_NeoPixel  -> arduino
- Bluetooth LE -> python 

## Execution:

### Step 1: Load code into each wearable:
#### This optional step accomplishes the following:
1) Readys wearables for communication

- attatch the wearable via usb
- click upload

### Step 2: Turn on both devices

#### This step accomplishes the following:
1) Resets bluetooth
2) Puts bluetooth into pairing mode

- The LED will flash red-blue-red-blue-red to let you know it has successfully booted up
- Evebtualy the light will go to steady blue to let you know it is ready to pair
- when both devices are steady blue you're ready to go

### Step 2: Pair the devices

#### This step accomplishes the following:
1) pairs the devices to each other
2) you're ready to have fun!

- run `$python pair_devices.py`  