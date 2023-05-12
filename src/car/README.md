# Car Firmware
The firmware is split into a few files that may be of interest to you,

* `firmware.c`: Implements the main functionality of the firmware, including `main()`
* `eeprom.{c,h}`: Implements functions used for interacting with the EEPROM specific for the car \
### Note: 
Other files have common implementation for car and fob, and the details regarding them have been provided in the design document.