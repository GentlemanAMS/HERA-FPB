#!/usr/bin/python3 -u

# @file gen_secret
# used to generate different encryption key, passwords and seed

import json
import argparse
from pathlib import Path
import random

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--car-id", type=int)
    parser.add_argument("--pair-pin", type=str)
    parser.add_argument("--secret-file", type=Path)
    parser.add_argument("--header-file", type=Path)
    parser.add_argument("--paired", action="store_true")
    parser.add_argument("--eeprom-file", type=Path)
    args = parser.parse_args()

    with open(args.eeprom_file, "wb") as fp:
        fp.write(("."*2048).encode())

if __name__ == "__main__":
    main()
