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
      7 : {'name': '2nd Bedroom Window', 'type': SENSOR}
      }



  def __init__(self, network):
    self.done = False
    self.network = network
    self.in_alarm_state = False
    self.alarm_on = 

  def run(self):
    while not self.done:
      time.sleep(1)

  def stop(self):
    self.done = True

  def reset_alarm(self):
    self.in_alarm_state = False

  def handle_node_event(self, network, node, value):
    if not self.in_alarm_state and self.node_ids[node.node_id]['type'] == self.SENSOR and value > 0:
      self.in_alarm_state = True
      send_mail(self.node_ids[node.node_id]['name'])
    else:
      print('Louie signal : Node event : {0}. value: {1}'.format(node, value))

  def louie_node_update(network, node):
      print('Louie signal : Node update : %s.' % node)

  def louie_value_update(network, node, value):
      print('Louie signal : Value update : %s.' % value)

  def louie_ctrl_message(state, message, network, controller):
      print('Louie signal : Controller message : %s.' % message)
