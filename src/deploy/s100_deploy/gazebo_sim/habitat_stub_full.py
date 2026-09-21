"""
Minimal habitat / magnum stub for loading PointNavResNetPolicy.

Strategy: Pre-populate sys.modules with the habitat_baselines PACKAGE
(not module) so its __init__.py never executes, then let Python find
sub-modules on disk.  Also stub the specific dead-code modules that
directly import magnum/habitat_sim.

This avoids the cascading import chains triggered by
habitat_baselines/__init__.py (ppo_trainer → multi_agent → hrl → rearrange
→ magnum).

Usage (before ANY habitat / habitat_baselines import):
    import habitat_stub_full
    habitat_stub_full.install()
"""

import sys
import types
from pathlib import Path


def install():
    """Install all stubs. Idempotent."""
    _stub_magnum_modules()
    _stub_rearrange_entry_points()
    _pre_stub_habitat_baselines()
    _pre_stub_habitat_baselines_common()


# ---------------------------------------------------------------------------
# 1. Pre-stub habitat so its __init__.py never runs
# ---------------------------------------------------------------------------

_HABITAT_DIR = str(
    Path(__file__).resolve().parent.parent.parent
    / "habitat-lab"
    / "habitat-lab"
    / "habitat"
)

_HABITAT_BASELINES_COMMON_DIR = str(
    Path(__file__).resolve().parent.parent.parent
    / "habitat-lab"
    / "habitat-baselines"
    / "habitat_baselines"
    / "common"
)


def _pre_stub_habitat():
    """Create a minimal habitat package in sys.modules so __init__.py
    never runs.  Its __init__.py imports vector_env → gym → gym_wrapper
    → rearrange_sim → magnum, which is all dead code for PointNav."""
    name = "habitat"
    if name in sys.modules:
        return
    mod = types.ModuleType(name)
    mod.__path__ = [_HABITAT_DIR]
    mod.__file__ = _HABITAT_DIR + "/__init__.py"

    # Provide stub VectorEnv so habitat_baselines/common/env_factory.py
    # (imported via common/__init__.py → VectorEnvFactory) doesn't crash.
    # We use simple dummy classes since PointNav never instantiates them.
    class _StubVectorEnv:
        pass

    mod.VectorEnv = _StubVectorEnv
    mod.ThreadedVectorEnv = _StubVectorEnv
    mod.__all__ = []

    sys.modules[name] = mod


def _pre_stub_habitat_baselines_common():
    """Pre-stub habitat_baselines.common so its __init__.py (which imports
    VectorEnvFactory → VectorEnv → magnum chain) never runs.  We keep
    __path__ so sub-modules like baseline_registry are findable on disk."""
    name = "habitat_baselines.common"
    if name in sys.modules:
        return
    mod = types.ModuleType(name)
    mod.__path__ = [_HABITAT_BASELINES_COMMON_DIR]
    mod.__file__ = _HABITAT_BASELINES_COMMON_DIR + "/__init__.py"
    sys.modules[name] = mod


# ---------------------------------------------------------------------------
# 2. Pre-stub habitat_baselines so its __init__.py never runs
# ---------------------------------------------------------------------------

_HABITAT_BASELINES_DIR = str(
    Path(__file__).resolve().parent.parent.parent
    / "habitat-lab"
    / "habitat-baselines"
    / "habitat_baselines"
)


def _pre_stub_habitat_baselines():
    """Create a minimal habitat_baselines package in sys.modules.

    We set __path__ to the real directory so sub-modules
    (rl.ddppo.policy.resnet_policy) can be found, but we DON'T let
    Python execute __init__.py, which would pull in the entire trainer
    stack → multi_agent → hrl → rearrange → magnum.
    """
    name = "habitat_baselines"
    if name in sys.modules:
        return

    mod = types.ModuleType(name)
    mod.__path__ = [_HABITAT_BASELINES_DIR]
    mod.__file__ = _HABITAT_BASELINES_DIR + "/__init__.py"

    # Minimal __all__ so code that does `from habitat_baselines import X`
    # doesn't crash — but that code path shouldn't be hit for PointNav.
    mod.__all__ = []

    sys.modules[name] = mod


# ---------------------------------------------------------------------------
# 2. Stub modules that directly import magnum / habitat_sim at module level
# ---------------------------------------------------------------------------


def _stub_magnum_modules():
    """These files have unconditional `import magnum` / `import habitat_sim`
    at the top.  They are dead code for PointNav inference."""

    # --- instance_image_nav_task (imports habitat_sim) ---
    _stub("habitat.tasks.nav.instance_image_nav_task", InstanceImageGoalSensor=(
        type("InstanceImageGoalSensor", (), {"cls_uuid": "instance_imagegoal"})
    ))

    # --- object_state_machine (imports magnum) ---
    _stub("habitat.sims.habitat_simulator.object_state_machine",
          ObjectStateMachine=type("ObjectStateMachine", (), {}))

    # --- env_batch_renderer (imports magnum) ---
    _stub("habitat.core.batch_rendering.env_batch_renderer",
          EnvBatchRenderer=type("EnvBatchRenderer", (), {}))


# ---------------------------------------------------------------------------
# 3. Stub rearrange entry points that are called from habitat's own
#    __init__.py / registration.py without try/except protection
# ---------------------------------------------------------------------------


def _stub_rearrange_entry_points():
    """habitat/tasks/registration.py calls _try_register_rearrange_task()
    and habitat/datasets/registration.py imports from datasets/rearrange.
    These functions lack try/except and will crash if magnum is missing.

    Additionally, gym_wrapper.py imports add_perf_timing_func from
    habitat.tasks.rearrange.rearrange_sim, which imports magnum."""

    # rearrange task registration (package + __init__)
    _stub_pkg("habitat.tasks.rearrange",
              _try_register_rearrange_task=lambda: None)

    # rearrange_sim — imports magnum at module level
    _stub("habitat.tasks.rearrange.rearrange_sim",
          add_perf_timing_func=_make_add_perf_timing_func())

    # datasets/rearrange registration
    _stub_pkg("habitat.datasets.rearrange",
              _try_register_rearrangedatasetv0=lambda: None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stub(name: str, **attrs):
    """Register a plain stub module if not already in sys.modules."""
    if name in sys.modules:
        return
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod


def _stub_pkg(name: str, **attrs):
    """Register a stub PACKAGE (module with __path__)."""
    if name in sys.modules:
        return
    mod = types.ModuleType(name)
    mod.__path__ = []
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod


def _make_add_perf_timing_func():
    from functools import wraps

    def add_perf_timing_func(name=None):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            return wrapper

        return decorator

    return add_perf_timing_func
