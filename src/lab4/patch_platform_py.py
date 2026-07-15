#!/usr/bin/env python3
"""
Patch Kit Python platform.py to handle conda-forge sys.version format.

Problem: Kit Python 3.12 platform.py expects CPython version format:
    "3.12.13 (main, Mar 5 2026, 16:50:00) [GCC 14.3.0]"
But conda-forge prepends packaging info:
    "3.12.13 | packaged by conda-forge | (main, ...) [GCC ...]"
The regex can't match the pipe-delimited package info, causing:
    ValueError: failed to parse CPython sys.version

This patch inserts a line to strip the "| packaged by ... |" segment
before regex matching.
"""

import os
import sys

PLATFORM_PY = os.path.expanduser("~/isaacsim/kit/python/lib/python3.12/platform.py")

PATCH_LINE = (
    '    # Strip conda packaging info (e.g. "| packaged by conda-forge |")'
    " from version string\n"
)
CODE_LINE = (
    "    sys_version = re.sub(r'\\s*\\| packaged by [^|]+\\|\\s*',"
    " ' ', sys_version)\n"
)

MARKER = "sys_version_parser = re.compile("


def main():
    if not os.path.isfile(PLATFORM_PY):
        print(f"ERROR: {PLATFORM_PY} not found.")
        return 1

    with open(PLATFORM_PY) as f:
        lines = f.readlines()

    # Check if already patched
    for line in lines:
        if "packaged by" in line:
            print("platform.py is already patched.")
            return 0

    # Find insertion point and insert
    inserted = False
    new_lines = []
    for line in lines:
        if not inserted and line.startswith(MARKER):
            new_lines.append(PATCH_LINE)
            new_lines.append(CODE_LINE)
            inserted = True
        new_lines.append(line)

    if not inserted:
        print(f"ERROR: Could not find '{MARKER}' in {PLATFORM_PY}.")
        return 1

    with open(PLATFORM_PY, "w") as f:
        f.writelines(new_lines)

    print(f"Patch applied successfully to {PLATFORM_PY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
