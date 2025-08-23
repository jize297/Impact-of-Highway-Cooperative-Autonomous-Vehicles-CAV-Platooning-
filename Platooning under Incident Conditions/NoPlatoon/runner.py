#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

if "SUMO_HOME" not in os.environ:
    sys.exit("❌ please set the SUMO_HOME environment variable")
tools = os.path.join(os.environ["SUMO_HOME"], "tools")
sys.path.append(tools)

import traci
from traci.exceptions import FatalTraCIError
import sumolib
import simpla
from simpla import SimplaException

USE_GUI    = 'nogui' not in sys.argv
SUMO_BIN   = 'sumo-gui' if USE_GUI else 'sumo'
SUMO_CFG   = 'M50_simulation.sumocfg'
NET_FILE   = 'M50network.net.xml.gz'
SIMPLA_CFG = 'simpla.cfg.xml'
END_TIME   = 28800        # simulation end time (seconds)

# ─── Lane Closure Parameters ──────────────────────────────────────────
CLOSED_LANES = [
    "106130759-AddedOffRampEdge_3",
    "328393125-AddedOnRampEdge_3",
    "615002705#0_1",
    "615002705#0_3",
]
BLOCK_BEGIN  = 27000          # closure start time (s)
BLOCK_END    = 27900          # closure end time (s)
DISALLOWED   = ["private", "passenger", "truck", "bus", "taxi", "coach",
                "delivery", "trailer", "motorcycle", "evehicle", "vip",
                "army", "hov", "custom1", "custom2"]

# ────────────────────── Start SUMO ‑ Simpla ─────────────
sumo_cmd = [
    sumolib.checkBinary(SUMO_BIN),
    "-c", SUMO_CFG,
    "--net-file", NET_FILE,
    "--step-length", "0.2",
    "--xml-validation.routes", "never",
]
logging.info("🚦 starting SUMO: %s", " ".join(sumo_cmd))
try:
    traci.start(sumo_cmd)
except Exception as e:
    logging.error("❌ failed to start SUMO: %s", e)
    sys.exit(1)

# try:
#     logging.info("🔧 loading Simpla configuration: %s", SIMPLA_CFG)
#     simpla.load(SIMPLA_CFG)
# except SimplaException as e:
#     logging.error("❌ failed to load Simpla: %s", e)
#     traci.close()
#     sys.exit(1)

# ────────────────────── Main Loop ─────────────────────────
original_allowed = {}   # {lane_id: [classes…]}
lanes_closed     = set()

try:
    while traci.simulation.getTime() < END_TIME:
        sim_time = traci.simulation.getTime()

        # Record original allowed classes for closed lanes
        for lane in CLOSED_LANES:
            if lane not in original_allowed:
                original_allowed[lane] = traci.lane.getAllowed(lane)

        # Close lanes at the specified time
        if sim_time >= BLOCK_BEGIN and not lanes_closed:
            for lane in CLOSED_LANES:
                traci.lane.setDisallowed(lane, DISALLOWED)
                logging.info("⛔ %.1f s: closing %s", sim_time, lane)
            lanes_closed.update(CLOSED_LANES)

        # Restore lanes at the specified time
        if sim_time >= BLOCK_END and lanes_closed:
            for lane in CLOSED_LANES:
                traci.lane.setAllowed(lane, original_allowed[lane])
                logging.info("✅ %.1f s: unblocking %s", sim_time, lane)
            lanes_closed.clear()

        traci.simulationStep() 
except FatalTraCIError as e:
    logging.warning("⚠️ TraCI connection reset (SUMO may have exited): %s", e)
except Exception as e:
    logging.error("❌ error occurred during simulation: %s", e)
finally:
    logging.info("🛑 simulation ended, actual time: %.2f seconds",
                 traci.simulation.getTime())
    traci.close()
