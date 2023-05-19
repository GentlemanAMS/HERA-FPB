# HERA-FPB
Implementation of Hotpatching-Embedded Real Time Application using Flash Patch and Breakpoint in ARM Cortex M4 controllers. 

# Environment Setup:

**Required Software:**
+ Git
+ Docker
+ Python
+ Stellaris ICDI Drivers
+ Uniflash

**Recommended Software:**
+ OpenOCD 
+ GDB-Debugger: GDB-Multiarch: ARM GNU Toolchain

**Hardware Setup:**

Arm Cortex-M4 based **TM4C123GH6PM Texas Instruments Tiva microcontroller** is used in this implementation. To prepare the hardware, load the bootloader present in `fpb_tools/bootloader` onto the evaluation board using **Uniflash**. UniFlash is a software tool for programming on-chip flash on TI microcontrollers and wireless connectivity devices and on-board flash for TI processors. UniFlash provides both graphical and command-line interfaces.
UNIFLASH is compatible with Windows, MacOS, and Linux. Download link: [https://www.ti.com/tool/UNIFLASH](https://www.ti.com/tool/UNIFLASH)

Setting up a Python virtual environment makes it easy to handle dependencies.
```
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
```

Install the `fpb_tools` in the virtual environment using
```
python3 -m pip install -e fpb-tools
```

**build.env**
```
python3 -m fpb_tools build.env --design <PATH_TO_DESIGN> --name <SYSTEM_NAME>
```
This builds a Docker image that will be used to create build and run environments for the system. Each subsequent step will be run in temporary containers, where all inputs are provided via read-only volumes, and outputs are stored on writable volumes

**build.build_firmware**
```
python3 -m fpb_tools build.build_firmware --design <PATH_TO_DESING> --name <SYSTEM_NAME> --folder <OUTPUT_VOLUME> --filename <BINARY_FILE_NAME>
```
This step builds the binaries that can be loaded into the development boards. The `fpb_tools` will invoke the design device Makefile in the `src/src_code` folder, which places the firmware binary and EEPROM contents in an output volume. This step also packages the firmware and EEPROM contents together so they can be loaded into the device.

**device.load_hw**

The load stage loads a packaged device binary+EEPROM into a target device. Plug a device with the bootloader installed into your computer, and hold down the right button while turning on the power. The device will slowly flash a cyan LED, indicating it is ready to install firmware. Then start the device load step.
```
python3 -m fpb_tools device.load_hw --folder <OUTPUT_VOLUME> --filename <BINARY_FILE_NAME> --serial-port <SERIAL_PORT>
```
When the install finishes, the cyan LED will be solid. Now, power cycle the device, and the LED should be solid green, showing that the firmware is running.



# Presentation Video

https://drive.google.com/file/d/1JudSKkRnc5fNcGtYRVtBAcMILmWfy48V/view

# References

+ [https://www.ndss-symposium.org/wp-content/uploads/ndss2021_6B-2_24159_paper.pdf](https://www.ndss-symposium.org/wp-content/uploads/ndss2021_6B-2_24159_paper.pdf)
+ [https://www.youtube.com/watch?v=WGE2JhjrcpE&list=PLfUWWM-POgQuaImJ-0o-wxdSmVuVtkE9j&index=4](https://www.youtube.com/watch?v=WGE2JhjrcpE&list=PLfUWWM-POgQuaImJ-0o-wxdSmVuVtkE9j&index=4)
+ [https://www.doulos.com/media/1188/using_cortex-m3_fpb.pdf](https://www.doulos.com/media/1188/using_cortex-m3_fpb.pdf)
+ [https://www.youtube.com/watch?v=Ta4jED8f68U](https://www.youtube.com/watch?v=Ta4jED8f68U)

Following Documentation was referred:
+ [FP_CTRL Register](https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Control-Register--FP-CTRL?lang=en)
+ [FP_REMAP Register](https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Remap-register--FP-REMAP?lang=en)
+ [FP_COMPx Register](https://developer.arm.com/documentation/ddi0403/d/Debug-Architecture/ARMv7-M-Debug/Flash-Patch-and-Breakpoint-unit/FlashPatch-Comparator-register--FP-COMPn?lang=en)
+ [B Branch Instruction](https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Instruction-Details/Alphabetical-list-of-instructions/B?lang=en)
+ [BL Branch & Link Instruction](https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Instruction-Details/Alphabetical-list-of-instructions/BL--BLX--immediate-?lang=en)
+ [Branch and Miscellaneous Control](https://developer.arm.com/documentation/ddi0406/c/Application-Level-Architecture/Thumb-Instruction-Set-Encoding/32-bit-Thumb-instruction-encoding/Branches-and-miscellaneous-control?lang=en)

Bootloader and `fpb_tools` is inspired from
+ [https://github.com/mitre-cyber-academy/2023-ectf-tools](https://github.com/mitre-cyber-academy/2023-ectf-tools)
