#!/usr/bin/env python3
"""Set hciattach_opi's Bluetooth address to 3C:7A:AA:28:1D:FE.

The running BossTV binary encodes that address as a 20-byte instruction
sequence at file offset 0x110b0 (sprd_config_init overwrites the ini).
The copy under files/ and packages/bsp/rk3399 is a different build: it
does not contain that sequence, and stores 10:11:12:13:14:15 as six
data bytes (at 0x26e84 in that build). This script patches whichever
pattern is present and leaves the file alone if it is already patched.
"""
import sys
from pathlib import Path

BOARD_OFF = 0x110b0
BOARD_OLD = bytes.fromhex("a08282526042a272801600b92002825280320079")
BOARD_NEW = bytes.fromhex("c0bf83520045b572801600b9408f875280320079")
DATA_OLD = bytes.fromhex("101112131415")
DATA_NEW = bytes.fromhex("3c7aaa281dfe")


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "/usr/local/bin/hciattach_opi")
    data = bytearray(path.read_bytes())
    if data[BOARD_OFF:BOARD_OFF + 20] == BOARD_NEW:
        print(f"already patched at {BOARD_OFF:#x} in {path}")
        return
    if data[BOARD_OFF:BOARD_OFF + 20] == BOARD_OLD:
        data[BOARD_OFF:BOARD_OFF + 20] = BOARD_NEW
        path.write_bytes(data)
        print(f"patched 20-byte immediate at {BOARD_OFF:#x} in {path}")
        return
    idx = data.find(DATA_OLD)
    if idx >= 0 and data.find(DATA_OLD, idx + 1) < 0:
        data[idx:idx + 6] = DATA_NEW
        path.write_bytes(data)
        print(f"patched 6-byte address at {idx:#x} in {path}")
        return
    if DATA_NEW in bytes(data) and DATA_OLD not in bytes(data):
        print(f"address bytes already set in {path}")
        return
    sys.exit(f"unrecognized hciattach_opi: {path}")


if __name__ == "__main__":
    main()
