#!/usr/bin/env bash
#==========================================================================
# Isaac Lab Conda Deactivation Hook
# Installed at: ~/miniconda3/envs/env_isaaclab/etc/conda/deactivate.d/unsetenv.sh
#
# Restores original environment state when conda env is deactivated.
#==========================================================================

# for Isaac Lab
if [ -n "${_IL_PREV_PYTHONPATH+x}" ]; then
    export PYTHONPATH="$_IL_PREV_PYTHONPATH"
    unset _IL_PREV_PYTHONPATH
fi
if [ -n "${_IL_PREV_LD_LIBRARY_PATH+x}" ]; then
    export LD_LIBRARY_PATH="$_IL_PREV_LD_LIBRARY_PATH"
    unset _IL_PREV_LD_LIBRARY_PATH
fi
if [ -n "${_IL_PREV_PATH+x}" ]; then
    export PATH="$_IL_PREV_PATH"
    unset _IL_PREV_PATH
fi
unset ISAACLAB_PATH
unset ISAAC_PATH
unset EXP_PATH
unset CARB_APP_PATH
unalias isaaclab 2>/dev/null || true
unset RESOURCE_NAME
