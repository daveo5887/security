#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

This file is part of **python-openzwave** project https://github.com/OpenZWave/python-openzwave.
    :platform: Unix, Windows, MacOS X
    :sinopsis: openzwave wrapper

.. moduleauthor:: bibi21000 aka Sébastien GALLET <bibi21000@gmail.com>

License : GPL(v3)

**python-openzwave** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**python-openzwave** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with python-openzwave. If not, see http://www.gnu.org/licenses.

"""

import logging
import sys, os

#logging.getLogger('openzwave').addHandler(logging.NullHandler())
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

#logger = logging.getLogger('openzwave')

import openzwave
from security_system import SecuritySystem
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
from louie import dispatcher, All

device="/dev/ttyACM0"
log="Info"

for arg in sys.argv:
    if arg.startswith("--device"):
        temp,device = arg.split("=")
    elif arg.startswith("--log"):
        temp,log = arg.split("=")
    elif arg.startswith("--help"):
        print("help : ")
        print("  --device=/dev/yourdevice ")
        print("  --log=Info|Debug")

#Define some manager options
options = ZWaveOption(device, \
  config_path="/home/pi/workspace/open-zwave-control-panel/config", \
  user_path=".", cmd_line="--logging false")
options.set_log_file("OZW_Log.log")
options.set_append_log_file(True)
options.set_console_output(True)
options.set_save_log_level("Info")
#options.set_save_log_level('Info')
options.set_logging(True)
options.lock()

#Create a network object
network = ZWaveNetwork(options, log=None)

print "------------------------------------------------------------"
print "Waiting for driver : "
print "------------------------------------------------------------"
for i in range(0,300):
    if network.state>=network.STATE_STARTED:
        print " done"
        break
    else:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.0)
if network.state<network.STATE_STARTED:
    print "."
    print "Can't initialise driver! Look at the logs in OZW_Log.log"
    quit(1)
print "------------------------------------------------------------"
print "Use openzwave library : %s" % network.controller.ozw_library_version
print "Use python library : %s" % network.controller.python_library_version
print "Use ZWave library : %s" % network.controller.library_description
print "Network home id : %s" % network.home_id_str
print "Controller node id : %s" % network.controller.node.node_id
print "Controller node version : %s" % (network.controller.node.version)
print "Nodes in network : %s" % network.nodes_count
print "------------------------------------------------------------"
print "Waiting for network to become ready : "
print "------------------------------------------------------------"
for i in range(0,300):
    if network.state>=network.STATE_AWAKED:
        print " done"
        break
    else:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1.0)
if not network.state >= network.STATE_AWAKED:
    print "."
    print "Can't start network! Look at the logs in OZW_Log.log"
    quit(2)

print "------------------------------------------------------------"
print "Nodes in network : %s" % network.nodes_count
print "------------------------------------------------------------"

security_system = SecuritySystem(network)
dispatcher.connect(security_system.handle_node_event, ZWaveNetwork.SIGNAL_NODE_EVENT)
dispatcher.connect(security_system.handle_scene_event, ZWaveNetwork.SIGNAL_SCENE_EVENT)
dispatcher.connect(security_system.louie_node_update, ZWaveNetwork.SIGNAL_NODE)
dispatcher.connect(security_system.louie_value_update, ZWaveNetwork.SIGNAL_VALUE)
dispatcher.connect(security_system.louie_ctrl_message, ZWaveController.SIGNAL_CONTROLLER)

try:
  security_system.run()
except KeyboardInterrupt:
  pass

print
print "------------------------------------------------------------"
print "Stop network"
print "------------------------------------------------------------"
network.stop()
