#!/bin/bash
# Watchdog: auto-restart training on process crash ONLY.
# Requires .training_active marker (created when user starts training).
# Does NOT auto-start on system reboot (marker cleared on reboot).

MARKER="/home/jimovo/Desktop/FURP/FURP-2026-YicongNing-RLNavigationForAMR/src/experiments/baseline_pointnav/.training_active"

if [ -f "$MARKER" ] && ! pgrep -f "habitat_baselines.run" > /dev/null; then
    cd /home/jimovo/Desktop/FURP/FURP-2026-YicongNing-RLNavigationForAMR/src/experiments/baseline_pointnav
    nohup bash -c 'while true; do ./train.sh; sleep 5; done' > train.log 2>&1 &
    echo "$(date): Training restarted (crash recovery)" >> watchdog.log
fi
