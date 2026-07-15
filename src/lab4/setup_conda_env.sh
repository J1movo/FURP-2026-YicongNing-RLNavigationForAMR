#!/usr/bin/env bash
#==========================================================================
# Isaac Lab runtime environment script
# Installed at: ~/isaacsim/setup_conda_env.sh
#
# Sourced by isaaclab.sh at runtime to add Kit Python stdlib paths.
# NOT sourced during conda activation (avoids conflict with base Python 3.13).
#==========================================================================

ISAACSIM_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Kit Python 3.12 stdlib — needed for carb, omni, and rendering modules.
# Added at runtime only, after conda activation is complete.
if [ -d "$ISAACSIM_PATH/kit/python/lib/python3.12" ]; then
    export PYTHONPATH="$ISAACSIM_PATH/kit/python/lib/python3.12:$PYTHONPATH"
fi
if [ -d "$ISAACSIM_PATH/kit/python/lib/python3.12/site-packages" ]; then
    export PYTHONPATH="$ISAACSIM_PATH/kit/python/lib/python3.12/site-packages:$PYTHONPATH"
fi
