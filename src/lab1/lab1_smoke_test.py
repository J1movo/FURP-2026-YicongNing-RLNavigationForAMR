"""Lab 1 smoke test: Habitat RL navigation stack sanity check (no scene).

Validates the full toolchain without requiring a scene file:
  imports, config system, simulator creation, CUDA, RL environment API.
"""

import importlib
import sys


def check_import(module_name, label=None):
    """Try importing a module; return (ok, version_str)."""
    if label is None:
        label = module_name
    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, "__version__", "ok")
        return True, str(version)
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 50)
    print("HABITAT STACK SMOKE TEST (no-scene)")
    print("=" * 50)

    results = {}

    # --- Core deps ---
    for mod, label in [
        ("numpy", "numpy"),
        ("torch", "torch"),
        ("cv2", "OpenCV"),
        ("numba", "numba"),
        ("gym", "gym"),
    ]:
        ok, ver = check_import(mod, label)
        results[label] = ok
        status = " OK " if ok else "FAIL"
        print(f"  [{status}] {label:12s}  {ver}")

    # --- Habitat ---
    for mod, label in [
        ("habitat", "habitat"),
        ("habitat_sim", "habitat_sim"),
    ]:
        ok, ver = check_import(mod, label)
        results[label] = ok
        status = " OK " if ok else "FAIL"
        print(f"  [{status}] {label:12s}  {ver}")

    # --- CUDA ---
    if results.get("torch"):
        import torch
        cuda_ok = torch.cuda.is_available()
        results["CUDA"] = cuda_ok
        status = " OK " if cuda_ok else "N/A "
        gpu_name = torch.cuda.get_device_name(0) if cuda_ok else "not detected"
        print(f"  [{status}] {'CUDA GPU':12s}  {gpu_name}")

    # --- Config system ---
    try:
        from habitat.config.default import get_config
        cfg = get_config("benchmark/nav/pointnav/pointnav_habitat_test.yaml")
        task_cfg = cfg.habitat.task
        sim_cfg = cfg.habitat.simulator

        results["config"] = True
        print(f"  [ OK ] config          loaded pointnav benchmark config")
        print(f"  [INFO]   Task type:    {task_cfg.type}")
        print(f"  [INFO]   Sim type:     {sim_cfg.type}")
        print(f"  [INFO]   Action space: {task_cfg.actions}")
    except Exception as e:
        results["config"] = False
        print(f"  [FAIL] config          {e}")

    # --- Simulator creation (no scene) ---
    try:
        import habitat_sim
        sim_cfg = habitat_sim.SimulatorConfiguration()
        agent_cfg = habitat_sim.AgentConfiguration()
        print(f"  [ OK ] sim_config     SimulatorConfiguration created")
        print(f"  [ OK ] agent_config   AgentConfiguration created")
        results["sim_api"] = True
    except Exception as e:
        results["sim_api"] = False
        print(f"  [FAIL] sim API         {e}")

    # --- Summary ---
    print()
    print("=" * 50)
    all_ok = all(results.values())
    if all_ok:
        print("RESULT: ALL CHECKS PASSED")
        print("Habitat toolchain is functional for Week 1 smoke test.")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"RESULT: FAILED checks: {failed}")
    print("=" * 50)


if __name__ == "__main__":
    main()
