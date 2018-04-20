#!/usr/bin/python

import smtplib
server = smtplib.SMTP('localhost') #, 23)

msg = "Hello!"
server.sendmail("testpy@scalr.com", "lynn@scalr.com", msg)
