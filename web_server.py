import cherrypy

class WebServer:

  ALARM_HTML_FILE = './web/alarm.html'

  def __init__(self, security_system):
    self.security_system = security_system
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 9000})

  def start(self):
      cherrypy.quickstart(self)

  def stop(self):
    cherrypy.engine.exit()
    print "HTTP Server Stopped"

  @cherrypy.expose
  def status(self):
    if self.security_system.alarm_on:
      return "Alarm is On"
    else:
      return "Alarm is Off"

  @cherrypy.expose
  def turn_on(self):
    self.security_system.turn_alarm_on()
    return "Alarm turned on"

  @cherrypy.expose
  def turn_off(self):
    self.security_system.turn_alarm_off()
    return "Alarm turned off"

