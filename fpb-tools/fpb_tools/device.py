import logging
from enum import Enum
from pathlib import Path
from rich.progress import Progress
from typing import Optional

from serial import Serial
from serial.tools import list_ports
from serial.serialutil import SerialException

from fpb_tools.utils import CmdFailedError, get_logger, HandlerRet, SOCKET_BASE


"""
Device Image Sizes
"""

BLOCK_SIZE = 16
PAGE_SIZE = 1024

FLASH_PAGES = 256
FLASH_SIZE = FLASH_PAGES * PAGE_SIZE
EEPROM_PAGES = 2
EEPROM_SIZE = EEPROM_PAGES * PAGE_SIZE

FW_FLASH_PAGES = 110
FW_FLASH_SIZE = FW_FLASH_PAGES * PAGE_SIZE
FW_FLASH_BLOCKS = FW_FLASH_SIZE // BLOCK_SIZE

FW_EEPROM_PAGES = 2
FW_EEPROM_SIZE = FW_EEPROM_PAGES * PAGE_SIZE
FW_EEPROM_BLOCKS = FW_EEPROM_SIZE // BLOCK_SIZE

TOTAL_FW_SIZE = FW_FLASH_SIZE + FW_EEPROM_SIZE
TOTAL_FW_PAGES = FW_FLASH_PAGES + FW_EEPROM_PAGES
TOTAL_FW_BLOCKS = FW_FLASH_BLOCKS + FW_EEPROM_BLOCKS


class BootloaderResponseCode(Enum):
    RequestUpdate = b"\x00"
    StartUpdate = b"\x01"
    UpdateInitFlashEraseOK = b"\x02"
    UpdateInitEEPROMEraseOK = b"\x03"
    UpdateInitEEPROMEraseError = b"\x04"
    AppBlockInstallOK = b"\x05"
    AppBlockInstallError = b"\x06"
    EEPROMBlockInstallOK = b"\x07"
    EEPROMBlockInstallError = b"\x08"
    AppInstallOK = b"\x09"
    AppInstallError = b"\x0a"


def get_serial_port():
    orig_ports = set(list_ports.comports())
    while True:
        ports = set(list_ports.comports())
        new_ports = ports - orig_ports

        if len(new_ports) == 1:
            new_port = new_ports.pop()
            return new_port.device

        orig_ports = ports


def verify_resp(ser: Serial, expected: BootloaderResponseCode):
    resp = ser.read(1)
    while resp == b"":
        resp = ser.read(1)

    assert BootloaderResponseCode(resp) == expected



async def load_hw(
    dev_in: Path, dev_name: str, dev_serial: str, logger: logging.Logger = None,
) -> HandlerRet:
    # Usage: Turn on the device holding SW2, then start this script

    logger = logger or get_logger()

    # Set up file references
    image_path = dev_in / f"{dev_name}.img"

    # Try to connect to the serial port
    logger.info(f"Connecting to serial port {dev_serial}...")
    ser = Serial(dev_serial, 115200, timeout=2)
    ser.reset_input_buffer()
    logger.info(f"Connection opened on {dev_serial}")

    # Open firmware
    logger.info("Reading image file...")
    if not image_path.exists():
        ser.close()
        raise CmdFailedError(f"Image file {image_path} not found")

    fw_data = image_path.read_bytes()
    fw_size = len(fw_data)
    if fw_size != TOTAL_FW_SIZE:
        ser.close()
        raise CmdFailedError(
            f"Invalid image size 0x{fw_size:X}. Expected 0x{TOTAL_FW_SIZE:X}"
        )

    # Wait for bootloader ready
    logger.info("Requesting update...")
    ser.write(BootloaderResponseCode.RequestUpdate.value)
    try:
        verify_resp(ser, BootloaderResponseCode.StartUpdate)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Bootloader did not start an update")

    # Wait for Flash erase
    logger.info("Waiting for Flash Erase...")
    try:
        verify_resp(ser, BootloaderResponseCode.UpdateInitFlashEraseOK)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Error while erasing Flash")

    # Wait for EEPROM erase
    logger.info("Waiting for EEPROM Erase...")
    try:
        verify_resp(ser, BootloaderResponseCode.UpdateInitEEPROMEraseOK)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Error while erasing EEPROM")

    # Send data in 16-byte blocks
    logger.info("Sending firmware...")
    total_bytes = len(fw_data)
    block_count = 0
    i = 0
    with Progress() as progress:
        task = progress.add_task("Sending firmware...", total=total_bytes)
        while i < total_bytes:
            block_bytes = fw_data[i : i + BLOCK_SIZE]  # noqa
            ser.write(block_bytes)

            try:
                if block_count < FW_FLASH_BLOCKS:
                    verify_resp(ser, BootloaderResponseCode.AppBlockInstallOK)
                else:
                    verify_resp(ser, BootloaderResponseCode.EEPROMBlockInstallOK)
            except AssertionError:
                ser.close()
                raise CmdFailedError(f"Install failed at block {block_count+1}")

            i += BLOCK_SIZE
            block_count += 1
            progress.update(task, advance=len(block_bytes))

    try:
        verify_resp(ser, BootloaderResponseCode.AppInstallOK)
    except AssertionError:
        ser.close()
        raise CmdFailedError("Image Failed to Install")

    logger.info("Image Installed")
    return b"", b""


class Port:
    def __init__(self, device_serial: str, baudrate=115200, log_level=logging.INFO):
        self.device_serial = device_serial
        self.baudrate = baudrate
        self.ser = None

        # Set up logger
        self.logger = logging.getLogger(f"{device_serial}_log")
        self.logger.info(f"Ready to connect to device on serial {self.device_serial}")

    def active(self) -> bool:
        # If not connected, try to connect to serial device
        if not self.ser:
            try:
                ser = Serial(self.device_serial, baudrate=self.baudrate, timeout=0.1)
                ser.reset_input_buffer()
                self.ser = ser
                self.logger.info(f"Connection opened on {self.device_serial}")
            except (SerialException, OSError):
                pass
        return bool(self.ser)

    def read_msg(self) -> Optional[bytes]:
        if not self.active():
            return None

        try:
            msg = self.ser.read()
            if msg != b"":
                return msg
            return None
        except (SerialException, OSError):
            self.close()
            return None

    def send_msg(self, msg: bytes) -> bool:
        if not self.active():
            return False

        try:
            self.ser.write(msg)
            return True
        except (SerialException, OSError):
            self.close()
            return False

    def close(self):
        self.logger.warning(f"Connection closed on {self.device_serial}")
        self.ser = None

