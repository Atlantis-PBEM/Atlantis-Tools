#!/usr/bin/python
#
# updateturn.py - create a small data file which details the times of the
# next turn run.
#

import os
import sys
import string
import time

cfgname = sys.argv[1]
config = __import__(cfgname);

datfile = open(config.htmldir + '/turn.dat', 'w')

day = time.localtime(time.time())
newday = list(day)
newday[3] = config.turn_time[0]
newday[4] = config.turn_time[1]
newday[5] = 0

if config.frequency == 1:
    newday[2] = newday[2]+7
elif config.frequency == 2:
    if day[6] == config.first_day:
        newday[2] = newday[2] + 3
    else:
        newday[2] = newday[2] + 4
elif config.frequency == 3:
    if day[6] == config.first_day + 4:
        newday[2] = newday[2] + 3
    else:
        newday[2] = newday[2] + 2
elif config.frequency == 7:
        newday[2] = newday[2] + 1
else:
    sys.exit("Don't know how to adjust turn times");

newday2 = time.mktime(newday)
if day[8] == 0:
    tzone = config.time_zone
else:
    tzone = config.time_zone_dst

c = time.ctime(newday2)
c = string.strip(c)
g = time.asctime(time.gmtime(newday2))
g = string.strip(g)
datfile.write(c+' '+tzone+'\n')
datfile.write(g+' GMT\n')
datfile.close()

sys.exit();
