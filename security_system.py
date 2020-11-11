import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.scene import ZWaveScene
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
import datetime
from send_mail import send_mail, send_tamper_mail, send_smoke_alarm_mail
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
  SHOCK = 'SHOCK'
  SMOKE_ALARM = 'SMOKE_ALARM'
  SMOKE_ALARM_STATES = {1: 'Smoke', 2: 'CO', 12: 'Test', 13: 'idle'}

  ALARM_ON_FILE = './alarm_on'

  node_ids = {1 : {"name": "Controller", "type": CONTROLLER},
              5 : {'name': "Front Door", 'type': SENSOR},
              6 : {'name': "Back Door", 'type': SENSOR},
              255 : {'name': "OpenZWave System", 'type': SYSTEM},
              7 : {'name': "Laundry Room Window", 'type': SENSOR},
              8 : {'name': 'Office Small Window', 'type': SENSOR_2},
              13 : {'name': 'Entryway Siren', 'type': SIREN},
              14 : {'name': 'Living Room Siren', 'type': SIREN},
              15 : {'name': 'Bedroom Siren', 'type': SIREN},
              3 : {'name': 'Dining Room Window', 'type': SENSOR},
              9 : {'name': "Office Big Window", 'type': SENSOR},
#             28 : {'name': "Back Window Shock Detector", 'type': SHOCK},
#             29 : {'name': "Back Door Shock Detector", 'type': SHOCK},
              11 : {'name': "Master Bedroom Window", 'type': SENSOR_2},
              12 : {'name': "Second Bedroom Window", 'type': SENSOR},
              4 : {'name': "Living Room Right Window", 'type': SENSOR_2},
              10 : {'name': "Living Room Left Window", 'type': SENSOR_2},
              16 : {'name': "Bedroom Smoke Alarm", 'type': SMOKE_ALARM, 'state': 'idle'},
              17 : {'name': "Entryway Smoke Alarm", 'type': SMOKE_ALARM, 'state': 'idle'},
              18 : {'name': "Office Smoke Alarm", 'type': SMOKE_ALARM, 'state': 'idle'},
              19 : {'name': "Living Room Smoke Alarm", 'type': SMOKE_ALARM, 'state': 'idle'},
              20 : {'name': "Second Bedroom Smoke Alarm", 'type': SMOKE_ALARM, 'state': 'idle'},
              21 : {'name': "Office Desk Window Break", 'type': SHOCK},
              22 : {'name': "Office Breaker Window Break", 'type': SHOCK},
              23 : {'name': "Dining Room Window Break", 'type': SHOCK},
              24 : {'name': "Living Room Window Break", 'type': SHOCK},
              25 : {'name': "Second Bedroom Window Break", 'type': SHOCK},
              26 : {'name': "Primary Bedroom Window Break", 'type': SHOCK},
              27 : {'name': "Front Bathroom Window Break", 'type': SHOCK},
              28 : {'name': "Kitchen Window Break", 'type': SHOCK}
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
    self.network.nodes[13].set_switch(72057594260832256, True)
    self.network.nodes[14].set_switch(72057594277609472, True)
    self.network.nodes[15].set_switch(72057594294386688, True)
    Timer(30.0, self.turn_sirens_off).start()

  def turn_sirens_off(self):
    print "Turning sirens off"
    self.network.nodes[13].set_switch(72057594260832256, False)
    self.network.nodes[14].set_switch(72057594277609472, False)
    self.network.nodes[15].set_switch(72057594294386688, False)

  def handle_smoke_alarm(self, node):
    alarm_type = self.node_ids[node.node_id]['state']
    print "Smoke alarm went off: " + alarm_type
    send_smoke_alarm_mail(self.node_ids[node.node_id]['name'], alarm_type)

  def handle_node_event(self, network, node, value):
    print('{0} - Louie signal : Node event : {1}. value: {2}'.format(str(datetime.datetime.now()), node, value))
    if self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.SENSOR and value > 0:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])
    elif self.alarm_on and not self.in_alarm_state and self.node_ids[node.node_id]['type'] == self.SHOCK and value > 0:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])

  def handle_scene_event(self, network, node, scene_id):
    if scene_id == 1:
      self.turn_alarm_on()
    elif scene_id == 3:
      self.turn_alarm_off()



###############################################################################################################################################

  def louie_node_update(self, network, node):
      print('Louie signal : Node update : %s.' % node)

  def louie_value_update(self, network, node, value):
    print('Louie signal : Value update : %s.' % value)
    if self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.GLASS_BREAK and value.label=='General' and value.data == 255:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])
    elif self.alarm_on and not self.in_alarm_state and node.node_id in self.nodes_in_alarm and self.node_ids[node.node_id]['type'] == self.SENSOR_2 and value.data == True:
      self.in_alarm_state = True
      self.turn_sirens_on()
      send_mail(self.node_ids[node.node_id]['name'])
    elif self.node_ids[node.node_id]['type'] == self.SENSOR:
      if value.label == "Alarm Level" and value.data == 255:
        send_tamper_mail(self.node_ids[node.node_id]['name'])
    elif self.node_ids[node.node_id]['type'] == self.SMOKE_ALARM:
      if value.label == "Alarm Type":
        self.node_ids[node.node_id]['state'] = self.SMOKE_ALARM_STATES[value.data]
      if self.node_ids[node.node_id]['state'] in ['Smoke', 'CO', 'Test'] and value.label == "Alarm Level" and value.data == 255:
        self.handle_smoke_alarm(node)


  def louie_ctrl_message(self, state, message, network, controller):
      print('Louie signal : Controller message : %s.' % message)
