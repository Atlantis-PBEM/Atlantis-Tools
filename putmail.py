#!/usr/bin/python
#
# putmail - a function to send text to a mail address
#
# This application takes a file and sends to a specified
# address using SMTP
#
# Inputs: recipient subject filename_of_body
#
# Outputs: errorlevel on failure
#

#
# Module requirements
#

import sys
import socket
import smtplib

cfgname = sys.argv[1];
config = __import__(cfgname);


#
# main process
#

if len(sys.argv) < 5 or len(sys.argv) == 6 or len(sys.argv) > 7:
    sys.exit('Wrong number of parameters called')

recipient = sys.argv[2]
subject   = sys.argv[3]
filename  = sys.argv[4]

forward = 0
resender = ''
sender = ''
if len(sys.argv) == 7:
    fullsender = sys.argv[5]
    resender = config.sender
    sender = sys.argv[6]
    forward = 1
else:
    fullsender = config.sender
    sender = config.admin
    forward = 0

try:
    bodyfile = open(filename, 'r')
except IOError:
    sys.exit('File not found')

if forward:
    message = 'ReSent-From: '+resender+'\nReSent-To: '+recipient+'\n'
    skip = bodyfile.readline()
else:
    message = 'From: '+fullsender+'\nTo: '+recipient+'\n'
    message = message + 'Sender: '+fullsender+'\n'
    message = message + 'Reply-To: '+fullsender+'\n'
    message = message + 'Subject: '+subject+'\n\n'


body = bodyfile.read()
bodyfile.close()

message = message+body

try:
    mailserver = smtplib.SMTP(config.smtpserver)
except socket.error:
    sys.exit('SMTP server not found')

try:    
    mailserver.sendmail(sender, recipient, message)
except smtplib.SMTPRecipientsRefused:
    pass
mailserver.quit()

sys.exit()
