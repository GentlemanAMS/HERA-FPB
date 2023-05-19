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


