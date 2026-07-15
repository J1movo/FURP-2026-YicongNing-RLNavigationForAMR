#!/usr/bin/env bash
#==========================================================================
# Isaac Lab Conda Activation Hook
# Installed at: ~/miniconda3/envs/env_isaaclab/etc/conda/activate.d/setenv.sh
#
# Sets environment variables needed by Isaac Sim and Isaac Lab.
# Only extension paths are loaded here; Kit Python stdlib paths
# are loaded at runtime by isaaclab.sh → setup_conda_env.sh
# (avoids conflict with conda base Python 3.13).
#==========================================================================

# Save previous state for deactivation
: "${_IL_PREV_PYTHONPATH:=${PYTHONPATH-}}"
: "${_IL_PREV_LD_LIBRARY_PATH:=${LD_LIBRARY_PATH-}}"
: "${_IL_PREV_PATH:=${PATH-}}"

# Isaac Lab
export ISAACLAB_PATH="/home/jimovo/Desktop/FURP/IsaacLab"
alias isaaclab="/home/jimovo/Desktop/FURP/IsaacLab/isaaclab.sh"
export RESOURCE_NAME="IsaacSim"

# Isaac Sim paths
ISAACSIM_PATH="/home/jimovo/isaacsim"
export ISAAC_PATH="$ISAACSIM_PATH"
export EXP_PATH="$ISAACSIM_PATH/apps"
export CARB_APP_PATH="$ISAACSIM_PATH/kit"

# LD_LIBRARY_PATH: Kit native libraries (rendering, physics, etc.)
ISAAC_LIBS="$ISAACSIM_PATH:$ISAACSIM_PATH/exts/isaacsim.robot.schema/plugins/lib:$ISAACSIM_PATH/extsDeprecated/isaacsim.robot_motion.lula/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.robot_motion.cumotion/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.robot_motion.pink/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.asset.exporter.urdf/pip_prebundle:$ISAACSIM_PATH/kit:$ISAACSIM_PATH/kit/kernel/plugins:$ISAACSIM_PATH/kit/libs/iray:$ISAACSIM_PATH/kit/plugins:$ISAACSIM_PATH/kit/plugins/bindings-python:$ISAACSIM_PATH/kit/plugins/carb_gfx:$ISAACSIM_PATH/kit/plugins/rtx:$ISAACSIM_PATH/kit/plugins/gpu.foundation"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$ISAAC_LIBS"

# PYTHONPATH: extension and kit module paths (NOT Kit Python stdlib)
ISAAC_PYTHON="$ISAACSIM_PATH/python_packages:$ISAACSIM_PATH/exts/isaacsim.simulation_app:$ISAACSIM_PATH/kit/kernel/py:$ISAACSIM_PATH/kit/plugins/bindings-python:$ISAACSIM_PATH/exts/isaacsim.replicator.episode_recorder/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.replicator.teleop/pip_prebundle:$ISAACSIM_PATH/extsDeprecated/isaacsim.robot_motion.lula/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.robot_motion.cumotion/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.robot_motion.pink/pip_prebundle:$ISAACSIM_PATH/exts/isaacsim.asset.exporter.urdf/pip_prebundle:$ISAACSIM_PATH/extscache/omni.kit.pip_archive-0.0.0+f9bf0dda.lx64.cp312/pip_prebundle:$ISAACSIM_PATH/exts/omni.isaac.core_archive/pip_prebundle:$ISAACSIM_PATH/exts/omni.pip.compute/pip_prebundle:$ISAACSIM_PATH/exts/omni.pip.cloud/pip_prebundle"
export PYTHONPATH="$ISAAC_PYTHON:$PYTHONPATH"

# PATH: add kit binary directory
export PATH="$ISAACSIM_PATH/kit:$PATH"
