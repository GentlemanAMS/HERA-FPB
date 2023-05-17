#!/usr/bin/python3 -u

import json
import argparse
from pathlib import Path
import random
import secrets 

def main():
    # parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--eeprom-file", type=Path, required=True)
    args = parser.parse_args()

    with open(args.eeprom_file, "wb") as fp:
        fp.write(("."*2048).encode())


if __name__ == "__main__":
    main()
