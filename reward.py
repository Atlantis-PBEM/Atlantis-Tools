#!/usr/bin/python
#
# reward.py - give the timesreward to a faction
#

import os
import sys
import string

cfgname = sys.argv[1]
config = __import__(cfgname);

infile = open(config.curdir + '/players.in', 'r')
lines = infile.readlines()
infile.close()

try:
    index = lines.index('Faction: '+sys.argv[2]+'\n')
except ValueError:
    sys.exit()

rewarded = 0
index = index + 1
token = string.split(lines[index], None, 1)
while token[0] != 'Faction:':
    if token[0] == 'RewardTimes':
        rewarded = 1
        break
    if index == len(lines)-1:
        lines.append('')
        index = index + 1
        break
    index = index + 1
    token = string.split(lines[index], None, 1)

if token[0] == 'Faction:' and not rewarded:
    lines.insert(index, '')

if not rewarded:
    lines[index] = 'RewardTimes\n'

if not rewarded:
    outfile = open(config.curdir+'/players.tmp', 'w')
    outfile.writelines(lines)
    outfile.close()
    os.unlink(config.curdir+'/players.in')
    os.rename(config.curdir+'/players.tmp', config.curdir+'/players.in')

print 'Gave times reward to faction '+sys.argv[2]
