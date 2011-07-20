#! /usr/bin/python
#
# run turn
#

import sys
import string
import os
import fcntl

cfgname = sys.argv[1]
config = __import__(cfgname)

# Wait for any pending email processes to finish
print "Checking for lockfile"
lfile = open(config.lockfile, 'w')
fcntl.flock(lfile.fileno(), fcntl.LOCK_EX)
print "Gained lock"

#
# first we want to copy over the previous turn templates for any player
# who failed to submit orders
#
if config.copy_template:
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
                            token[1] = string.rstrip(token[1])
                            if token[1] != 'NoAddress':
                                newfile = config.curdir+'/orders.'+faction
                                if not os.access(newfile, os.F_OK):
                                    oldfile = config.prevdir+'/report.'+faction
                                    print 'No orders for '+faction+'. Copying template'
                                    os.system('cp '+oldfile+' '+newfile)
                            break
                        line = players.readline()
        line = players.readline()
    

#
# first we create the Times
#
os.system(config.scriptdir + '/times.py '+cfgname)

#
# next we store away the previous turn
#

os.chdir(config.gamedir)

archivedir = ''

doprevious = 1
#doprevious = 0

os.chdir(config.curdir)

val = os.system(config.gameexe + ' run')
if val != 0:
    print "Error processing turn!!!!!!";
    sys.exit();

#
# we now prepare to send the mail
#

try:
    players = open('players.out')
except IOError:
    sys.exit()

sendscript = open(config.scriptdir + '/send'+cfgname+'reports.py', 'w')
sendscript.write('#!/usr/bin/python\n\n')
sendscript.write('import os\nimport '+cfgname+'\n\n')
factions = open(config.curdir + '/factions.txt', 'w')
users = open(config.curdir + '/users', 'w')

users.write(config.admin + " : |ADMIN|SUPERADMIN|MODERATOR|CCERRORS|REPORTS|ECHOPOST|\n")
users.write(config.sender + " : |VACATION|PREAPPROVE|\n")


# read through to get the first faction
line = players.readline()
turntext = ''
while line != '':
    faction = ''
    name    = ''
    token = string.split(line)
    if len(token) > 0:
        if token[0] == 'TurnNumber:':
            # create the turnnumber string
            turn = string.atoi(string.rstrip(token[1]))
            turntext = 'Year '
            turntext = turntext+`(turn-1)/12+1`+', '
            if turn%12 == 1:
                turntext = turntext+'January'
            elif turn%12 == 2:
                turntext = turntext+'February'
            elif turn%12 == 3:
                turntext = turntext+'March'
            elif turn%12 == 4:
                turntext = turntext+'April'
            elif turn%12 == 5:
                turntext = turntext+'May'
            elif turn%12 == 6:
                turntext = turntext+'June'
            elif turn%12 == 7:
                turntext = turntext+'July'
            elif turn%12 == 8:
                turntext = turntext+'August'
            elif turn%12 == 9:
                turntext = turntext+'September'
            elif turn%12 == 10:
                turntext = turntext+'October'
            elif turn%12 == 11:
                turntext = turntext+'November'
            elif turn%12 == 0:
                turntext = turntext+'December'
        if token[0] == 'Faction:':
            # we have a faction, now to find the email address
            faction = string.strip(token[1])
            line = players.readline()
            email = 'NoAddress'
            times = 0
            while line != '':
                token = string.split(line, None, 1)
                if token[0] == 'Name:':
                    name = string.strip(token[1])
                    name = string.replace(name, '`', '\`')
                    name = string.replace(name, "'", "\'")
                    name = string.replace(name, '"', '\\\\"')
                if token[0] == 'Email:':
                    email = string.strip(token[1])
                    factions.write(name+', '+email+'\n')
                    if email != 'NoAddress':
                        users.write(email+' : |ECHOPOST|\n')
                if token[0] == 'SendTimes:':
                    times = string.atoi(token[1])
                    if email != 'NoAddress':
                        sendscript.write('os.system('+cfgname+'.scriptdir + "')
                        sendscript.write('/putturn.py '+cfgname+' \\"'+email+'\\" \\"'+config.gamename+' report for '+name+', '+turntext+'\\" report.'+faction)
                        sendscript.write('")\n')
                        if times:
                            sendscript.write('os.system('+cfgname+'.scriptdir + "')
                            sendscript.write('/putmail.py '+cfgname+' \\"'+email+'\\" \\"'+config.gamename+' Times, '+turntext+'\\" times.txt')
                            sendscript.write('")\n')
                    break
                line = players.readline()
    line = players.readline()

players.close()
sendscript.close()
factions.close()
users.close()
os.chmod(config.scriptdir + '/send'+cfgname+'reports.py', 0777)


print "Updating turn data."
os.system(config.scriptdir + '/updateturn.py '+cfgname)
print "Sending reports."
os.system(config.scriptdir + '/send'+cfgname+'reports.py')

print "Copying times."
os.system('cp '+config.curdir+'/times.txt '+config.htmldir+'/times/times.'+`turn-1`);

os.chdir(config.gamedir)

try:
    players = open(config.prevdir + '/players.in', 'r')
except IOError:
    doprevious = 0

if doprevious == 1:
    line = players.readline()
    while line != '':
        token = string.split(line)
        if token[0] == 'TurnNumber:':
            turn = string.atoi(token[1])
            break
        line = players.readline()

    players.close()

    print 'Storing turn '+`turn`

    archivedir = config.archdir + 'turn'+string.zfill(`turn`,5)
    os.rename(config.prevdir , archivedir)
    
print "Rebuilding current directory."
#
# create a new 'Current' directory
#
os.rename(config.curdir, config.prevdir)
os.mkdir(config.curdir)

#
# move the new .out files to .in
#
os.rename(config.prevdir+'/game.out', config.curdir+'/game.in')
os.rename(config.prevdir+'/players.out', config.curdir+'/players.in')
os.rename(config.prevdir+'/factions.txt', config.curdir+'/factions.txt')
os.rename(config.prevdir+'/users', config.curdir+'/users')

os.chdir(config.curdir)
print "Building units.txt."
os.system(config.gameexe + ' mapunits >/dev/null')

if archivedir != '':
    print "Archiving last turn."
    os.system('tar -zcf "'+archivedir+'.tgz" "'+archivedir+'"')

# I have marked this section out, as I will delete this only manually at first

#    list = os.listdir(archivedir)
#    for i in range(len(list)):
#        os.unlink(archivedir+'/'+list[i])
#    os.rmdir(archivedir)

# Remove the lock file
lfile.close()
