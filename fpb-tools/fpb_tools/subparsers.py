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


class BuildDevParser(BuildParser):
    """Build a device"""

    deployment: str  # name of the deployment


class SubparserBuildCarFobPair(BuildDevParser, cmd="build.car_fob_pair"):
    """Build a car and paired fob pair"""

    car_name: str  # name of the car output files
    car_out: Path  # directory to mount to output built car to
    car_id: int  # ID of the car to build
    car_in: Path = Path("car")  # path to the car directory in the design repo


class SubparserDevLoadHW(fpbTap, cmd="device.load_hw"):
    """Load a firmware onto the device"""

    dev_in: Path  # path to the device build directory
    dev_name: str  # name of the device
    dev_serial: str  # specify the serial port



class SubparserDevBridge(fpbTap, cmd="device.bridge"):
    """Start a serial-to-socket bridge"""

    bridge_id: int  # Bridge ID to set up
    dev_serial: str  # serial port to open
