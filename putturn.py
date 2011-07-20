#!/usr/bin/python
#
# putturn - a function to send the turn to a mail address
# This is similar to putmail, except it adds a next turn header
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
import string

#
# main process
#

if len(sys.argv) != 5:
    sys.exit('Wrong number of parameters called')

cfgname = sys.argv[1];
config = __import__(cfgname);

recipient = sys.argv[2]
subject   = sys.argv[3]
filename  = sys.argv[4]

fullsender = config.sender

try:
    bodyfile = open(filename, 'r')
except IOError:
    sys.exit('File not found')

try:
    turnfile = open(config.htmldir+'/turn.dat', 'r')
    turndue = turnfile.readline();
    turndue = string.strip(turndue);
    gturndue = turnfile.readline();
    gturndue = string.strip(gturndue);
except IOError:
    sys.exit('File not found')

message = 'From: '+fullsender+'\nTo: '+recipient+'\n'
message = message + 'Sender: '+fullsender+'\n'
message = message + 'Reply-To: '+fullsender+'\n'
message = message + 'Subject: '+subject+'\n\n'

message = message + '\n;\n; Next turn runs:\n'
message = message + ';     '+turndue+'\n'
message = message + ';     '+gturndue+'\n\n'

body = bodyfile.read()
bodyfile.close()

message = message+body

try:
    mailserver = smtplib.SMTP(config.smtpserver)
except socket.error:
    sys.exit('SMTP server not found')

try:
    mailserver.sendmail(config.admin, recipient, message)
except smtplib.SMTPRecipientsRefused:
    pass
mailserver.quit()

sys.exit()
