#!/usr/bin/python
#
# Times maker
#

#
# I have available a number of files, with the names of
# times.* and rumor.*. I need to fold all of these files
# in together to form a text file. The rumor files need
# to be submitted randomly, and the times files in any
# order. There is also an editorial file.
#

#
# the text output will be limited to 70 # characters per line.
# The lines will be managed in memory first, before being written.
#

import string
import os
import sys

cfgname = sys.argv[1];
config = __import__(cfgname);

# This function adds some text to a line. If the line would
# exceed 70 characters because of this addition, the line 
# is broken and a new line started
def addtotext(instring, text):
    line = len(text)-1
    column = len(text[line])
    if (column+len(instring)) > 70:
        text[line] = text[line]+'\n';
        text.append('')
        line = line+1
    if text[line] == '':
		text[line] = instring
    else:
        text[line] = text[line]+' '+instring

# This function takes a file handle and handles all the text contained in it
def processfile(infile, text):
    lines = infile.readlines()

    #
    # we assume the first non blank line is the header
    #

    first = 0
    while string.strip(lines[first]) == '':
        first = first+1

    #
    # we assume the last non blank line is the signature
    #

    last = len(lines)-1
    while string.strip(lines[last]) == '':
        last = last-1


    while first != last:
        text.append(lines[first]);
#        if string.strip(lines[first]) == '':
#            text.append('\n\n')
#            text.append('')
#        else:
#            words = string.split(lines[first])
#            for i in range(len(words)):
#                addtotext(words[i], text)
#            text.append('\n')
#            text.append('')
        first = first+1

#    words = string.split(lines[first])
#    for i in range(len(words)):
#        addtotext(words[i], text)
    text.append(lines[first])

    text.append('\n')
    text.append('----------------------------------------------------------------------\n')
    text.append('')


# main process

files = os.listdir(config.curdir)
files.sort()
files.reverse()

articles = []
articles.append('')

doeditorial = 0
for i in range(0, 9999):
    gotit = 1
    try:
        index = files.index('editorial.'+`i`)
    except ValueError:
        gotit = 0
    if gotit == 1:
        doeditorial = 1
        break

if doeditorial:
    articles.append('----------------------------------------------------------------------\n')
    articles.append('-'+string.center('****ADMINISTRIVIA****',68)+'-\n')
    articles.append('----------------------------------------------------------------------\n')
    articles.append('')
    for i in range(0, 9999):
        gotit = 1
        try:
            index = files.index('editorial.'+`i`)
        except ValueError:
            gotit = 0
        if gotit == 1:
            print 'Processing editorial.'+`i`
            infile = open(config.curdir+'/editorial.'+`i`, 'r')
            processfile(infile, articles)
    articles.append('\n')
    articles.append('\n')

articles.append('----------------------------------------------------------------------\n')
articles.append('-'+string.center('****NEWS ARTICLES****',68)+'-\n')
articles.append('----------------------------------------------------------------------\n')
articles.append('')
havenews = 0
for i in range(0, 9999):
    gotit = 1
    try:
        index = files.index('times.'+`i`)
    except ValueError:
        gotit = 0
    if gotit == 1:
        infile = open(config.curdir+'/times.'+`i`)
        print 'Processing times.'+`i`
        processfile(infile, articles)
        havenews = 1

if havenews == 0:
    articles.append('No news articles submitted.\n')
    articles.append('----------------------------------------------------------------------\n')

articles.append('\n')
articles.append('\n')
articles.append('----------------------------------------------------------------------\n')
articles.append('-'+string.center('****RUMORS****',68)+'-\n')
articles.append('----------------------------------------------------------------------\n')
articles.append('')
haverumors = 0
for i in range(0, 9999):
    gotit = 1
    try:
        index = files.index('rumor.'+`i`)
    except ValueError:
        gotit = 0
    if gotit == 1:
        print 'Processing rumor.'+`i`
        infile = open(config.curdir+'/rumor.'+`i`)
        processfile(infile, articles)
        haverumors = 1

if haverumors == 0:
    articles.append('No rumors submitted.\n')
    articles.append('----------------------------------------------------------------------\n')

players = open(config.curdir + '/players.in', 'r')
line = players.readline()
while line != '':
    token = string.split(line)
    if token[0] == 'TurnNumber:':
        turn = string.atoi(token[1])+1
        break
    line = players.readline()

players.close()
if turn%12 == 1:
    caption = 'January'
elif turn%12 == 2:
    caption = 'February'
elif turn%12 == 3:
    caption = 'March'
elif turn%12 == 4:
    caption = 'April'
elif turn%12 == 5:
    caption = 'May'
elif turn%12 == 6:
    caption = 'June'
elif turn%12 == 7:
    caption = 'July'
elif turn%12 == 8:
    caption = 'August'
elif turn%12 == 9:
    caption = 'September'
elif turn%12 == 10:
    caption = 'October'
elif turn%12 == 11:
    caption = 'November'
elif turn%12 == 0:
    caption = 'December'
caption = caption+', Year '
caption = caption+`(turn-1)/12+1`

#
# Write out the result
#

times = open(config.curdir+'/times.txt', 'w')
times.write('**********************************************************************\n')
times.write('****'+string.center('The '+config.gamename+' Times', 62)+'****\n')
times.write('**********************************************************************\n')
times.write('****'+string.center(caption+' Edition', 62)+'****\n');
times.write('**********************************************************************\n')
times.write('\n')
times.write('\n')
times.writelines(articles)
times.close()
