#!/usr/bin/env python3
"""Quick verification script for Isaac Lab installation.

Usage:
    conda activate env_isaaclab
    python src/lab4/verify_install.py
"""

import sys


def check_import(name, package=None):
    """Try importing a package and report status."""
    try:
        mod = __import__(package if package else name)
        version = getattr(mod, "__version__", "?")
        print(f"  [OK] {name:30s} v{version}")
        return True
    except ImportError as e:
        print(f"  [FAIL] {name:30s} — {e}")
        return False


def main():
    print("=" * 60)
    print("Isaac Lab Installation Verification")
    print("=" * 60)

    # Python info
    print(f"\nPython: {sys.version}")
    print(f"Executable: {sys.executable}")

    # Core dependencies
    print("\n--- Core Dependencies ---")
    all_ok = True
    all_ok &= check_import("torch")
    all_ok &= check_import("gymnasium")
    all_ok &= check_import("numpy")

    # Isaac Lab extensions
    print("\n--- Isaac Lab Extensions ---")
    extensions = [
        "isaaclab",
        "isaaclab_tasks",
        "isaaclab_rl",
        "isaaclab_assets",
        "isaaclab_visualizers",
        "isaaclab_contrib",
        "isaaclab_experimental",
        "isaaclab_newton",
        "isaaclab_physx",
        "isaaclab_ov",
        "isaaclab_ovphysx",
        "isaaclab_ppisp",
        "isaaclab_mimic",
        "isaaclab_teleop",
    ]
    for ext in extensions:
        all_ok &= check_import(ext)

    # Isaac Sim
    print("\n--- Isaac Sim ---")
    try:
        from isaacsim import SimulationApp
        if SimulationApp is not None:
            print(f"  [OK] isaacsim.SimulationApp — OK")
        else:
            print(f"  [FAIL] isaacsim.SimulationApp is None")
            all_ok = False
    except Exception as e:
        print(f"  [FAIL] isaacsim.SimulationApp — {e}")
        all_ok = False

    # Environment variables
    print("\n--- Environment Variables ---")
    import os
    for var in ["ISAAC_PATH", "EXP_PATH", "CARB_APP_PATH", "ISAACLAB_PATH"]:
        val = os.environ.get(var, "")
        if val:
            print(f"  [OK] {var}={val}")
        else:
            print(f"  [WARN] {var} not set")
            all_ok = False

    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("All checks passed! Isaac Lab is ready.")
    else:
        print("Some checks FAILED. Review errors above.")
    print("=" * 60)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
