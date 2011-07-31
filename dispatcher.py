#!/usr/bin/python
#
# dispatcher.py
#

import sys
import os
import time
import string
import getpass
import tempfile
import random
import fcntl

def Rename(oldname, newname):
    f = open(oldname, 'r')
    f1 = open(newname, 'w')
    s = f.readline()
    while s != '':
        f1.write(s)
        s = f.readline()
    f.close()
    f1.close()
    os.remove(oldname)

cfgname = sys.argv[1]

idx = string.find(cfgname, '-owner')
send_owner = 0
if idx != -1:
    cfgname = cfgname[0:idx]
    send_owner = 1

if send_owner == 0:
    idx = string.find(cfgname, '-gm')
    if idx != -1:
        cfgname = cfgname[0:idx]
        send_owner = 1

if send_owner == 0:
    idx = string.find(cfgname, '-admin')
    if idx != -1:
        cfgname = cfgname[0:idx]
        send_owner = 1

print cfgname + '\n'

try:
    config = __import__(cfgname)
except ImportError:
    sys.exit(67)

# Okay.  First thing to do is check for a lock file and if one exists
# block until we can lock it.   The runturn script will also lock and
# unlock this file to prevent new orders from showing up while the turn
# is running.

# Okay create the lock file
lfile = open(config.lockfile, 'w')
fcntl.flock(lfile.fileno(), fcntl.LOCK_EX)

# If we got here, we have lockage!

log = open(config.logfile, 'a')

# OK.  Create a temporary file name and copy all of stdin into it
tfile = tempfile.mktemp()
ofile = open(tfile, 'w')
ofile1 = open(config.curdir+'/turnmail.log', 'a')
line = '-'
fromaddy=None
fullfrom=None
replyto=None
error=None
while line != '':
    # We'll pick off the email address here too
    line = sys.stdin.readline()
    token = string.split(line, None, 1)
    if (error == None) and (len(token) > 1):
        if token[0] == 'From:':
            if fromaddy == None:
                fullfrom = token[1]
                fromaddy = token[1]
                if string.find(fromaddy, '<') != -1:
                    token = string.split(fromaddy, '<', 1)
                    fromaddy = token[1]
                    token = string.split(fromaddy, '>', 1)
                    fromaddy = token[0]
                if string.find(fromaddy, '(') != -1:
                    token = string.split(fromaddy, '(', 1)
                    fromaddy = token[0]
                fromaddy = string.strip(fromaddy)
                fullfrom = string.strip(fullfrom)
                mdaemon = string.lower(fromaddy)
                if string.find(mdaemon, 'mailer-daemon') != -1:
                    error = 1
        if string.lower(token[0]) == 'reply-to:':
            if replyto == None:
                replyto = token[1]
                fromaddy = token[1]
                fullfrom = token[1]
                if string.find(fromaddy, '<') != -1:
                    token = string.split(fromaddy, '<', 1)
                    fromaddy = token[1]
                    token = string.split(fromaddy, '>', 1)
                    fromaddy = token[0]
                if string.find(fromaddy, '(') != -1:
                    token = string.split(fromaddy, '(', 1)
                    fromaddy = token[1]
                    token = string.split(fromaddy, ')', 1)
                    fromaddy = token[0]
            fromaddy = string.strip(fromaddy)
            fullfrom = string.strip(fullfrom)
    ofile.write(line)
    ofile1.write(line)
ofile.close()
ofile1.close()

str = string.lower(fromaddy);
if string.find(str, cfgname+'@'+config.machine)  != -1:
    error = 1

if error != None:
    os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "System Error Message" '+tfile)
    sys.exit()

if fromaddy == None:
    log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+' No from address found\n')
    os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "Failed to find From address" '+tfile)
    sys.exit()

if send_owner:
    log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  sent an email to the gm\n')
    os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "Admin email" '+tfile+' \''+fullfrom+'\''+' '+fromaddy)
    sys.exit()

# We are recieving our input from stdin
try:
    source = open(tfile, 'r')
except IOError:
    sys.stderr.write('Can not open '+tfile+' for reading\n')
    sys.exit()


#
# loop through source until we find a valid command line
#

none   = 0
orders = 1
times  = 2
rumor  = 3
resend = 4
create = 5
diplo  = 6
remind = 7

commandtype = none

line = '?'
gotit = 0
faction = ''
spassword = ''
while line != '':
    line = source.readline()
    token = string.split(line)
    if len(token) > 0:
        tester = string.lower(token[0])
        if tester == '#atlantis':
            commandtype = orders
            gotit = 1
        if tester == '#times':
            commandtype = times
            gotit = 1
        if tester == '#press':
            commandtype = times
            gotit = 1
        if tester == '#rumor':
            commandtype = rumor
            gotit = 1
        if tester == '#rumour':
            commandtype = rumor
            gotit = 1
        if tester == '#rumors':
            commandtype = rumor
            gotit = 1
        if tester == '#rumours':
            commandtype = rumor
            gotit = 1
        if tester == '#resend':
            commandtype = resend
            gotit = 1
        if tester == '#remind':
            commandtype = remind
            gotit = 1
        if tester == '#create':
            commandtype = create
            gotit = 1
        if tester == '#email':
            commandtype = diplo
            gotit = 1
        if commandtype != none:
            if commandtype == diplo:
                if len(token) < 2:
                    gotit = 0
                else:
                    faction = token[1]
            elif commandtype == create:
                token = string.split(line, '"')
                if len(token) < 4:
                    gotit = 0
                else:
                    faction = token[1]
                    spassword = token[3]
            else:
                if len(token) < 3:
                    if len(token) == 2:
                        faction = token[1]
                        spassword = '"none"'
                    else:
                        gotit = 0
                else:
                   faction = token[1]
                   spassword = string.join(token[2:], " ")
            break
    token = None

if gotit == 0:
    log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+' ('+fromaddy+') No valid commands found\n')
    os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "Failed to find valid commands" '+tfile)
    os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+fromaddy+'" "Failed to find valid commands" '+tfile)
    sys.exit()

if commandtype != create and commandtype != diplo:
    newtempfilename = tempfile.mktemp()
    outfile = open(newtempfilename, 'w')
    if commandtype != orders:
        line = source.readline()
    while line != '':
        newline = string.replace(line, '=20', ' ')
        newline = string.replace(newline, '=', ' ')
        newline = string.rstrip(newline)
        testline = string.strip(newline);
        if commandtype == orders:
            if newline != '':
                outfile.write(newline)
                outfile.write('\n')
        else:
            if len(newline) > 0:
                if string.lower(testline)[0:4] != '#end':
                    outfile.write(newline)
                    outfile.write('\n')
            else:
                outfile.write('\n')
        if string.lower(testline)[0:4] == '#end':
            break
        line = source.readline()
    source.close()
    #
    # loop through the player list until we find the matching faction
    #
    players = open(config.curdir+'/players.in', 'r')
    factionname = None
    email = None
    password = None
    line = '?'
    gotit = 0
    while line != '':
        line = players.readline()
        token = string.split(line)
        if len(token) > 0:
            if token[0] == 'Faction:':
                if token[1] == faction:
                    # we have a match!
                    factionname = None
                    email = None
                    password = None
                    while email == None or password == None:
                        line = players.readline()
                        line = string.strip(line)
                        token = None
                        token = string.split(line, None, 1)
                        if token[0] == 'Name:':
                            factionname = token[1]
                        if token[0] == 'Email:':
                            email = token[1]
                        if token[0] == 'Password:':
                            password = token[1]
                    password = '"'+password+'"'
                    if password != spassword:
                        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+' ('+fromaddy+') incorrect password for faction '+faction+'\n')
                        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+email+'" "Password incorrect" '+tfile)
                        sys.exit()
                    break

    players.close()

    if factionname == None:
        os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "No faction given" '+tfile)
        os.system(config.scriptdir+'/putmail.py '+cfgname+' '+fromaddy+' "No faction given" '+tfile)
        sys.exit()

    if commandtype == times:
        # write the faction name at the end of the file
        outfile.write('\n\n[Article submitted by '+factionname+']\n')
    outfile.close()

    #
    # put the file in the right directory
    #

    if commandtype == orders:
        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  submitting orders from faction '+faction+'\n')
        try:
            os.unlink(config.curdir+'/orders.'+faction)
        except OSError:
            pass

        Rename(newtempfilename, config.curdir+'/orders.'+faction)

        # Update the players 'LastOrders' info
        os.system(config.scriptdir+'/updatelast.py '+cfgname+' '+faction);

        #
        # run the syntax checker against the order
        #
        val = os.system(config.gameexe+' check '+config.curdir+'/orders.'+faction+' '+config.curdir+'/check.'+faction)
        if val != 0:
            os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "Error checking orders" '+config.curdir+'/check.'+faction)
            os.system(config.scriptdir+'/putmail.py '+cfgname+' '+email+' "Error checking orders" '+config.curdir+'/check.'+faction)
            try:
                os.unlink(config.curdir+'/check.'+faction)
            except OSError:
                pass;
            sys.exit()

        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+email+'" "Checked orders" '+config.curdir+'/check.'+faction)
        os.unlink(config.curdir+'/check.'+faction)

    if commandtype == times:
        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  submitting times article from faction '+faction+'\n')
        files = os.listdir(config.curdir)
        number = 0
        while gotit == 0:
            number = random.randint(0, 9999)
            gotit = 0
            try:
                index = files.index('times.'+`number`)
            except ValueError:
                gotit = 1
        Rename(newtempfilename, config.curdir+'/times.'+`number`)
        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+email+'" "Times article submitted" '+config.curdir+'/times.'+`number`)
        os.system(config.scriptdir+'/reward.py '+cfgname+' '+faction)

    if commandtype == rumor:
        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  submitting rumor from faction '+faction+'\n')
        files = os.listdir(config.curdir)
        number = 0
        while gotit == 0:
            number = random.randint(0, 9999)
            gotit = 0
            try:
                index = files.index('rumor.'+`number`)
            except ValueError:
                gotit = 1
        Rename(newtempfilename, config.curdir+'/rumor.'+`number`)
        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+email+'" "Rumor submitted" '+config.curdir+'/rumor.'+`number`)

    if commandtype == resend:
        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  resending last report for faction '+faction+'\n')
        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+email+'" "Turn Report resend" '+config.prevdir+'/report.'+faction)

    if commandtype == remind:
        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  reminded of last commands submitted faction '+faction+'\n')
        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+email+'" "Turn Commands reminder" '+config.curdir+'/orders.'+faction)

elif commandtype == create:
    log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  creating new faction '+ faction+'\n')
    source.close()
    players = open(config.curdir+'/players.in', 'a')
    players.write('Faction: new\n')
    players.write('Name: '+faction+'\n')
    players.write('Password: '+spassword+'\n')
    players.write('Email: '+fromaddy+'\n')
    players.write('SendTimes: 1\n')
    players.write('Template: long\n')
    players.close()
    # os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+fromaddy+'" "Faction created" '+tfile)
    os.system(config.scriptdir+'/putmail.py '+cfgname+' '+config.admin+' "New Faction created" '+tfile)
    users = None;
    try:
        users = open(config.curdir+'/users', 'a')
    except IOError:
        sys.stderr.write('Cannot open '+tfile+' for reading\n')
    if users != None:
        users.write(fromaddy+' : |ECHOPOST|\n');
        users.close();
    os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+fromaddy+'" "Welcome to '+config.gamename+'" '+config.filedir+'/welcome.txt')
elif commandtype == diplo:
    source.close()
    units = open(config.curdir+'/units.txt', 'r')
    line = '?'
    realfaction = None
    while line != '':
        line = units.readline()
        line = string.strip(line)
        token = string.split(line, ':')
        if len(token) > 1:
            if token[0] == faction:
                # We have a match
                realfaction = token[1]
                break
    units.close()
    if realfaction == None:
        os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+fromaddy+'" "No such unit for diplomatic mail" '+tfile)
        log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  attempted to send a diplomatic email to nonexistant unit '+ faction+'\n')
    else:
        players = open(config.curdir+'/players.in', 'r')
        line = '?'
        forward = None
        while line != '':
            line = players.readline()
            token = string.split(line)
            if len(token) > 0:
                if token[0] == 'Faction:':
                    if token[1] == realfaction:
                        # We have a match
                        while forward == None:
                            line = players.readline()
                            line = string.strip(line)
                            token = string.split(line, None, 1)
                            if token[0] == 'Email:':
                                forward = token[1]
                        break
        players.close()
        if forward != None:
            log.write(time.strftime("[%m/%d/%Y %H:%M:%S]", time.localtime(time.time()))+'('+fromaddy+')  sent a diplomatic email to unit '+ faction+' of faction '+realfaction+'\n')
            os.system(config.scriptdir+'/putmail.py '+cfgname+' "'+forward+'" "Diplomatic email" '+tfile+' \''+fullfrom+'\''+' '+fromaddy)


if commandtype == resend or commandtype == remind:
    os.unlink(newtempfilename)
os.unlink(tfile)
lfile.close()
