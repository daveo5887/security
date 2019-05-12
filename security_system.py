import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
import datetime
from send_mail import send_mail, send_tamper_mail
from louie import dispatcher, All
from threading import Timer,Thread
from web_server import WebServer

class SecuritySystem:

  SENSOR = 'sensor'
  SENSOR_2 = 'sensor_2'
  GLASS_BREAK = 'glass_break'
  CONTROLLER = 'controller'
  SYSTEM = 'system'
  SIREN = 'SIREN'

  ALARM_ON_FILE = './alarm_on'

  node_ids = {1 : {"name": "Controller", "type": CONTROLLER},
      255 : {'name': "OpenZWave System", 'type': SYSTEM},
      3 : {'name': "Front Door", 'type': SENSOR},
      27 : {'name': "Living Room Middle Window", 'type': SENSOR_2},
      25 : {'name': "Back Door", 'type': SENSOR},
      5 : {'name': "?", 'type': SENSOR},
      24 : {'name': '2nd Bedroom Window', 'type': SENSOR_2},
      12 : {'name': '2nd Bedroom Glass Break', 'type': GLASS_BREAK},
      13 : {'name': 'Bedroom Glass Break', 'type': GLASS_BREAK},
      14 : {'name': 'Living Room Glass Break', 'type': GLASS_BREAK},
      15 : {'name': 'Living Room Siren', 'type': SIREN},
      17 : {'name': 'Hallway Siren', 'type': SIREN},
      18 : {'name': 'Bedroom Siren', 'type': SIREN},
      19 : {'name': 'Bedroom Window', 'type': SENSOR},
      20 : {'name': "Living Room Cat Tower Window", 'type': SENSOR}
      }

  nodes_in_alarm = set()

  def __init__(self, network):
    self.done = False
    self.network = network
    self.in_alarm_state = False
    self.alarm_on = open(self.ALARM_ON_FILE).readline().rstrip() == 'true'
    if self.alarm_on:
      self.turn_alarm_on()

    self.web_server = WebServer(self)

  def run(self):
    self.web_server_thread = Thread(target=self.web_server.start)
    self.web_server_thread.start()
    for key, value in self.network.nodes[24].get_sensors().iteritems():
      print value.to_dict()
    try:
      while not self.done:
        time.sleep(1)
    except KeyboardInterrupt as e:
      self.stop()
      raise e

  def stop(self):
    self.done = True
    self.web_server.stop()
    #self.web_server_thread.join()

  def turn_alarm_on(self):
    print "Turning alarm on"
    self.in_alarm_state = False
    self.alarm_on = True
    self.turn_sirens_off()

    open(self.ALARM_ON_FILE, 'w').write('true')

    self.nodes_in_alarm.clear()
    for node_id, node_info in self.node_ids.iteritems():
      if node_info['type'] == self.SENSOR or node_info['type'] == self.SENSOR_2:
        if not self.network.nodes[node_id].get_values_by_command_classes()[48].values()[0].data:
          self.nodes_in_alarm.add(node_id)
      elif node_info['type'] == self.GLASS_BREAK:
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
    self.network.nodes[15].set_switch(72057594294386688, True)
    self.network.nodes[17].set_switch(72057594327941120, True)
    self.network.nodes[18].set_switch(72057594344718336, True)
    Timer(30.0, self.turn_sirens_off).start()

  def turn_sirens_off(self):
    print "Turning sirens off"
    self.network.nodes[15].set_switch(72057594294386688, False)
    self.network.nodes[17].set_switch(72057594327941120, False)
    self.network.nodes[18].set_switch(72057594344718336, False)

  def handle_node_event(self, network, node, value):
    if self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.SENSOR and value > 0:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])
    #elif self.node_ids[node.node_id]['type'] != self.SENSOR:
    print('{0} - Louie signal : Node event : {1}. value: {2}'.format(str(datetime.datetime.now()), node, value))

  def handle_scene_event(self, network, node, scene_id):
    if scene_id == 1:
      self.turn_alarm_on()
    elif scene_id == 3:
      self.turn_alarm_off()



###############################################################################################################################################

  def louie_node_update(self, network, node):
      print('Louie signal : Node update : %s.' % node)

  def louie_value_update(self, network, node, value):
    if self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.GLASS_BREAK and value.label=='General' and value.data == 255:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])
    elif self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.SENSOR_2 and value.data == True:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])
    elif self.node_ids[node.node_id] == self.SENSOR:
      if value.label == "Alarm Level" and value.data == 255:
        send_tamper_mail(self.node_ids[node.node_id]['name'])

    print('Louie signal : Value update : %s.' % value)

  def louie_ctrl_message(self, state, message, network, controller):
      print('Louie signal : Controller message : %s.' % message)
