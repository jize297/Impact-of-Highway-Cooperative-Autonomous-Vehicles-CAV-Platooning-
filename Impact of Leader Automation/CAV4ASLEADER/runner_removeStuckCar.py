#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


if "SUMO_HOME" not in os.environ:
    sys.exit("❌ configure the SUMO_HOME environment variable")
tools = os.path.join(os.environ["SUMO_HOME"], "tools")
sys.path.append(tools)

import traci
from traci.exceptions import FatalTraCIError
import sumolib
import simpla
from simpla import SimplaException


USE_GUI = 'nogui' not in sys.argv
SUMO_BINARY = 'sumo-gui' if USE_GUI else 'sumo'
SUMO_CFG = 'M50_simulation.sumocfg'
NET_FILE = 'M50network.net.xml.gz'
SIMPLA_CFG = 'simpla.cfg.xml'
END_TIME = 28800  # set simulation end time (seconds)

# build launch command
sumo_cmd = [
    sumolib.checkBinary(SUMO_BINARY),
    '-c', SUMO_CFG,
    '--net-file', NET_FILE,
    '--step-length', '0.2',
    '--xml-validation.routes', 'never'
]

# invoke SUMO
logging.info("🚦 Starting SUMO: %s", " ".join(sumo_cmd))
try:
    traci.start(sumo_cmd)
except Exception as e:
    logging.error("❌ Failed to start SUMO: %s", e)
    sys.exit(1)

# load Simpla
try:
    logging.info("🔧 Loading Simpla configuration: %s", SIMPLA_CFG)
    simpla.load(SIMPLA_CFG)
except SimplaException as e:
    logging.error("❌ Failed to load Simpla: %s", e)
    traci.close()
    sys.exit(1)

# main loop runs until end time
try:
    while traci.simulation.getTime() < END_TIME:
        traci.simulationStep()
except FatalTraCIError as e:
    logging.warning("⚠️ TraCI connection reset (SUMO may have exited): %s", e)
except Exception as e:
    logging.error("❌ Simulation runtime error: %s", e)
finally:
    sim_time = traci.simulation.getTime()
    logging.info("🛑 Simulation ended, actual time: %.2f seconds", sim_time)
    traci.close()
