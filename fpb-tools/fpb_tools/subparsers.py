from pathlib import Path
from typing import Dict, Type

from tap import Tap

subparsers: Dict[str, Type[Tap]] = {}


class fpbTap(Tap):
    def __init_subclass__(cls, cmd: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if cmd is not None:
            subparsers[cmd] = cls


class BuildParser(fpbTap):
    design: Path  # path to the design repo (likely in designs/)
    name: str  # tag name of the Docker image
    image: str = "fpb"  # name of the Docker image


class SubparserBuildEnv(BuildParser, cmd="build.env"):
    """Build the environment"""

    docker_dir: Path = Path(
        "docker_env"
    )  # path to the docker env within the design repo
    dockerfile: str = "build_image.Dockerfile"  # name of the dockerfile


class SubparserBuildFirmware(BuildParser, cmd="build.firmware"):
    """Build a car and paired fob pair"""

    firmware_file: str  # name of the car output files
    firmware_folder: Path  # directory to mount to output built car to
    src_code: Path = Path("car")  # path to the car directory in the design repo


class SubparserDevLoadHW(fpbTap, cmd="device.load_firmware"):
    """Load a firmware onto the device"""

    firmware_folder: Path  # path to the device build directory
    firmware_file: str  # name of the device
    serial_port: str  # specify the serial port
