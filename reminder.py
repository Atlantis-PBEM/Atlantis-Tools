#!/usr/bin/python
#
# reminder.py - sends out a reminder to the announcement list
# Intended to be triggered from crontab
#

import os
import sys
import string
import time
import fcntl
import socket
import smtplib

cfgname = sys.argv[1]
config = __import__(cfgname);

datfile = open(config.htmldir + '/turn.dat', 'r')
curtime = datfile.readline()
gmttime = datfile.readline()
datfile.close()

curtime = string.strip(curtime)
gmttime = string.strip(gmttime)


# Wait for any pending email to finish
lfile = open(config.lockfile, 'w')
fcntl.flock(lfile.fileno(), fcntl.LOCK_EX)

header = 'From: '+config.sender+'\n'
header = header + 'Sender: '+config.sender+'\n'
header = header + 'Reply-To: '+config.sender+'\n'
header = header + 'To: '+config.announce+'\n'
header = header + 'Subject: Orders Reminder for "'+config.gamename+'"\n\n'

body = 'This is just a friendly reminder that orders for\n'
body = body + '        '+config.gamename+'\n'
body = body + 'need to be submitted by\n'
body = body + '        '+curtime+' ('+gmttime+')\n\n'
body = body + 'If you have already submitted your orders, thank you.\n'

message = header + body

try:
    mailserver = smtplib.SMTP(config.smtpserver)
except socket.error:
    sys.exit('SMTP server not found')

mailserver.sendmail(config.admin, config.announce, message)
mailserver.quit()

lfile.close()
sys.exit();
