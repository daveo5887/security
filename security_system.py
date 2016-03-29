import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
from send_mail import send_mail
from louie import dispatcher, All

class SecuritySystem:

  SENSOR = 'sensor'
  CONTROLLER = 'controller'
  SYSTEM = 'system'

  ALARM_ON_FILE = './alarm_on'

  node_ids = {1 : {"name": "Controller", "type": CONTROLLER},
      255 : {'name': "OpenZWave System", 'type': SYSTEM},
      3 : {'name': "Living Room Right Window", 'type': SENSOR},
      4 : {'name': "Living Room Middle Window", 'type': SENSOR},
      5 : {'name': "Front Door", 'type': SENSOR},
      7 : {'name': '2nd Bedroom Window', 'type': SENSOR},
      11 : {'name': 'Strobe Alarm', 'type': 'ssa1'},
      12 : {'name': '2nd Bedroom Glass Break', 'type': SENSOR},
      13 : {'name': 'Bedroom Glass Break', 'type': SENSOR},
      14 : {'name': 'Living Room Glass Break', 'type': SENSOR}
      }

  nodes_in_alarm = set()

  def __init__(self, network):
    self.done = False
    self.network = network
    self.in_alarm_state = False
    self.alarm_on = open(self.ALARM_ON_FILE).readline().rstrip() == 'true'
    if self.alarm_on:
      self.turn_alarm_on()

  def run(self):
    while not self.done:
      time.sleep(1)

  def stop(self):
    self.done = True

  def turn_alarm_on(self):
    print "Turning alarm on"
    self.in_alarm_state = False
    self.alarm_on = True
    self.turn_sirens_on()
    open(self.ALARM_ON_FILE, 'w').write('true')
    self.nodes_in_alarm.clear()
    for node_id, node_info in self.node_ids.iteritems():
      if node_info['type'] == self.SENSOR:
        if not self.network.nodes[node_id].get_values_by_command_classes()[48].values()[0].data:
          self.nodes_in_alarm.add(node_id)
    print "Nodes in alarm: " + str(self.nodes_in_alarm)
        

  def turn_alarm_off(self):
    print "Turning alarm off"
    self.turn_sirens_off()
    self.in_alarm_state = False
    self.alarm_on = False
    open(self.ALARM_ON_FILE, 'w').write('false')

  def turn_sirens_on(self):
    print "Turning sirens on"
    self.network.nodes[11].set_dimmer(72057594227294209, 1)

  def turn_sirens_off(self):
    print "Turning sirens off"
    self.network.nodes[11].set_dimmer(72057594227294209, 0)

  def handle_node_event(self, network, node, value):
    if self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.SENSOR and value > 0:
      self.in_alarm_state = True
      send_mail(self.node_ids[node.node_id]['name'])
    elif self.node_ids[node.node_id]['type'] != self.SENSOR:
      print('Louie signal : Node event : {0}. value: {1}'.format(node, value))

  def handle_scene_event(self, network, node, scene_id):
    if scene_id == 1:
      self.turn_alarm_on()
    elif scene_id == 3:
      self.turn_alarm_off()



###############################################################################################################################################

  def louie_node_update(network, node):
      print('Louie signal : Node update : %s.' % node)

  def louie_value_update(network, node, value):
      print('Louie signal : Value update : %s.' % value)

  def louie_ctrl_message(state, message, network, controller):
      print('Louie signal : Controller message : %s.' % message)
