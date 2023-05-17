import logging

import docker
import docker.errors
from docker.utils import tar
from pathlib import Path

from fpb_tools.utils import run_shell, get_logger, zip_step_returns, HandlerRet
from fpb_tools.device import FW_FLASH_SIZE, FW_EEPROM_SIZE
from fpb_tools.subparsers import (
    SubparserBuildEnv,
    SubparserBuildFirmware,
)


async def env(
    design: Path,
    name: str,
    image: str = SubparserBuildEnv.image,
    docker_dir: Path = SubparserBuildEnv.docker_dir,
    dockerfile: str = SubparserBuildEnv.dockerfile,
    logger: logging.Logger = None,
) -> HandlerRet:
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"Building image {tag}")

    # Add build directory to context
    build_dir = design.resolve() / docker_dir
    dockerfile_name = build_dir / dockerfile
    with open(dockerfile_name, "r") as df:
        dockerfile = ("Dockerfile", df.read())
    dockerfile = tar(build_dir, dockerfile=dockerfile)

    # run docker build
    client = docker.from_env()
    try:
        _, logs_raw = client.images.build(
            tag=tag, fileobj=dockerfile, custom_context=True,
        )
    except docker.errors.BuildError as e:
        logger.error(f"Docker build error: {e}")
        for log in e.build_log:
            if "stream" in log and log["stream"].strip():
                logger.error(log["stream"].strip())
        raise
    logger.info(f"Built image {tag}")

    logs = "".join([d["stream"] for d in list(logs_raw) if "stream" in d])
    logging.debug(logs)
    return logs.encode(), b""


async def build_firmware(
    design: Path,
    name: str,
    filename: str,
    folder: Path,
    src_path: Path = SubparserBuildFirmware.src_path,
    image: str = SubparserBuildFirmware.image,
    logger: logging.Logger = None,
) -> HandlerRet:
    """
    Build Firmware
    """

    # Image information
    tag = f"{image}:{name}"
    logger = logger or get_logger()
    logger.info(f"Building firmware {filename}")

    # Build Firmware
    output = await make_dev(
        image=image,
        name=name,
        design=design,
        firmware_file=filename,
        src_in=src_path,
        firmware_folder=folder,
        make_target="target_firmware",
        logger=logger,
    )

    return zip_step_returns([output])




async def make_dev(
    image: str,
    name: str,
    design: str,
    firmware_file: str,
    src_in: Path,
    firmware_folder: Path,
    make_target: str,
    logger: logging.Logger,
) -> HandlerRet:
    """
    Build device firmware
    """
    tag = f"{image}:{name}"

    # Setup full container paths
    bin_path = f"/firmware_folder/{firmware_file}.bin"
    elf_path = f"/firmware_folder/{firmware_file}.elf"
    eeprom_path = f"/firmware_folder/{firmware_file}.eeprom"
    src_in = (design / src_in).resolve()
    firmware_folder = firmware_folder.resolve()

    # Create output directory
    if not firmware_folder.exists():
        logger.info(f"Making output directory {firmware_folder}")
        firmware_folder.mkdir()

    # Compile
    output = await run_shell(
        "docker run"
        f' -v "{str(src_in)}":/src_in:ro'
        f' -v "{str(firmware_folder)}":/firmware_folder'
        " --workdir=/root"
        f" {tag} /bin/bash -c"
        ' "'
        " cp -r /src_in/. /root/ &&"
        f" make {make_target}"
        f" BIN_PATH={bin_path}"
        f" ELF_PATH={elf_path}"
        f" EEPROM_PATH={eeprom_path}"
        '"'
    )

    logger.info(f"Built device {firmware_file}")

    # Package image, eeprom, and secret
    logger.info(f"Packaging image for device {firmware_file}")
    bin_path = firmware_folder / f"{firmware_file}.bin"
    eeprom_path = firmware_folder / f"{firmware_file}.eeprom"
    image_path = firmware_folder / f"{firmware_file}.img"

    package_device(
        bin_path,
        eeprom_path,
        image_path
    )

    logger.info(f"Packaged device {firmware_file} image")

    return output


def package_device(
    bin_path: Path,
    eeprom_path: Path,
    image_path: Path,
):
    """
    Package a device image for use with the bootstrapper

    Accepts up to 64 bytes (encoded in hex) to insert as a secret in EEPROM
    """
    # Read input bin file
    bin_data = bin_path.read_bytes()

    # Pad bin data to max size
    image_bin_data = bin_data.ljust(FW_FLASH_SIZE, b"\xff")

    # Read EEPROM data
    eeprom_data = b""

    # Pad EEPROM to max size
    image_eeprom_data = eeprom_data.ljust(FW_EEPROM_SIZE, b"\xff")

    # Create phys_image.bin
    image_data = image_bin_data + image_eeprom_data

    # Write output binary
    image_path.write_bytes(image_data)
