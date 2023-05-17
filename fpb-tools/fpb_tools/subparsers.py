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


class SubparserBuildFirmware(BuildParser, cmd="build.build_firmware"):
    """Build Firmware"""

    filename: str  # name of the firmware output files
    folder: Path  # directory to mount to output built firmware files to
    src_path: Path = Path("car")  # path to the source directory in the design repo


class SubparserDevLoadHW(fpbTap, cmd="device.load_hw"):
    """Load a firmware onto the device"""

    folder: Path  # path to the device build directory
    filename: str  # name of the device
    serial_port: str  # specify the serial port

