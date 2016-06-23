import smtplib
import time

def send_mail(node_name):
  fromaddr = 'daveochromebox@gmail.com'
  toaddrs  = ['daveo5887@gmail.com', 'ssterli2@gmail.com']
  current_time = time.strftime("%d/%m/%Y %H:%M:%S")
  message = "Alarm set off by " + node_name + " at time " + current_time

  msg = "\r\n".join([
        "From: daveochromebox@gmail.com",
        "To: daveo5887@gmail.com,ssterli2@gmail.com",
        "Subject: Security System Alarm",
        "",
        message
        ])

  username = 'daveochromebox@gmail.com'
  password = 'Gadzook123'
  server = smtplib.SMTP('smtp.gmail.com:587')
  server.ehlo()
  server.starttls()
  server.login(username,password)
  server.sendmail(fromaddr, toaddrs, msg)
  server.quit()

def send_tamper_mail(node_name): 
  fromaddr = 'daveochromebox@gmail.com'
  toaddrs  = ['daveo5887@gmail.com', 'ssterli2@gmail.com']
  current_time = time.strftime("%d/%m/%Y %H:%M:%S")
  message = "Security System Sensor " + node_name + " has fallen off or been removed."

  msg = "\r\n".join([
        "From: daveochromebox@gmail.com",
        "To: daveo5887@gmail.com,ssterli2@gmail.com",
        "Subject: Security System Issue",
        "",
        message
        ])

  username = 'daveochromebox@gmail.com'
  password = 'Gadzook123'
  server = smtplib.SMTP('smtp.gmail.com:587')
  server.ehlo()
  server.starttls()
  server.login(username,password)
  server.sendmail(fromaddr, toaddrs, msg)
  server.quit()
