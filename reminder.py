#!/usr/bin/python
#
# reminder.py - sends out a reminder to any factions that haven't
# submitted orders yet.
# Intended to be triggered from crontab
#

import os
import sys
import string
import fcntl
import socket
import smtplib

cfgname = sys.argv[1]
config = __import__(cfgname)

datfile = open(config.htmldir + '/turn.dat', 'r')
curtime = datfile.readline()
gmttime = datfile.readline()
datfile.close()

curtime = string.strip(curtime)
gmttime = string.strip(gmttime)

# Wait for any pending email to finish
lfile = open(config.lockfile, 'w')
fcntl.flock(lfile.fileno(), fcntl.LOCK_EX)

#
# check all the factions to see which ones haven't submitted orders
#
players = open(config.curdir+'/players.in', 'r')
line = players.readline()
while line != '':
    token = string.split(line, None, 1)
    if len(token) > 0:
        if token[0] == 'Faction:':
            faction = token[1]
            faction = string.rstrip(faction)
            if faction != 'new':
                line = players.readline()
                while line != '':
                    token = string.split(line, None, 1)
                    if token[0] == 'Email:':
                        email = string.strip(token[1])
                        if email != 'NoAddress':
                            ordersfile = config.curdir+'/orders.'+faction
                            if not os.access(ordersfile, os.F_OK):
                                print 'No orders for '+faction+'. Sending reminder.'
                                header = 'From: '+config.sender+'\n'
                                header = header + 'Sender: '+config.sender+'\n'
                                header = header + 'Reply-To: '+config.sender+'\n'
                                header = header + 'To: '+email+'\n'
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

                                mailserver.sendmail(config.sender, email, message)
                                mailserver.quit()
                        break
                    line = players.readline()
    line = players.readline()
    
lfile.close()
sys.exit();
