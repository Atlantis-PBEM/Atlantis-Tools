#!/usr/bin/python
#
# updatelast.py - updates the LastOrders: value for each faction
#
# In normal atlantis this is handled by the game engine if an orders
# file exists, but since we (by default) copy over the last turns template
# for orders, we need to track it in the script.
# Wyreth atlantis (and the 4.0.5 code tree) have a gamedef which lets
# the game work properly in this format.
#

import os
import sys
import string

cfgname = sys.argv[1]
config = __import__(cfgname);

infile = open(config.curdir + '/players.in', 'r')
lines = infile.readlines()
infile.close()

pfile = open(config.curdir + '/players.in', 'r')
line = pfile.readline()
turn = 0
while line != '':
    token = string.split(line);
    if token[0] == 'TurnNumber:':
        turn = string.atoi(token[1])
        break
    line = pfile.readline()
pfile.close()

try:
    index = lines.index('Faction: '+sys.argv[2]+'\n')
except ValueError:
    sys.exit()

found = 0
index = index + 1
token = string.split(lines[index], None, 1)
while token[0] != 'Faction:':
    if token[0] == 'LastOrders:':
        found = 1
        break
    if index == len(lines)-1:
        lines.append('')
        index = index + 1
        break
    index = index + 1
    token = string.split(lines[index], None, 1)

if token[0] == 'Faction:' and not found:
    lines.insert(index, '')

lines[index] = 'LastOrders: '+`turn`+'\n'

outfile = open(config.curdir+'/players.tmp', 'w')
outfile.writelines(lines)
outfile.close()
os.unlink(config.curdir+'/players.in')
os.rename(config.curdir+'/players.tmp', config.curdir+'/players.in')

print 'Updated last orders recieved for faction '+sys.argv[2]
