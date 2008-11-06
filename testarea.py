#import sqlite3
#
#conn = sqlite3.Connection('./lastfm')
#c = conn.cursor()
#c.execute('select * from songs')
#for i in c:
#    print i
#c.execute('select * from scrobble')
#for i in c:
#    print i
#conn.close()
import string
def getInfo(line):
    l = string.split(line, ': ')[1][:-1]
    return l

def stripData(data):
    '''Remove times and milliseconds and convert items 5 and 6'''
    data[0] = int(data[0])
    data[5] = int(string.split(data[5], ' ')[0]) / 1000
    data[6] = int(string.split(data[6], ' ')[0])
    return data

newFile = file('./temporaryList', 'w')
mtpList = file('./mtp-tracklisting', 'r')
data = []
requiredData = ('Track ID', 'Title', 'Artist', 'Album', 
                    'Track number', 'Duration', 'Use count', 'Filetype')

for line in mtpList.readlines():
    for item in requiredData:
        if line.__contains__(item):
            if item == 'Track ID':
                data = []
            data.append(getInfo(line))
            #bug: fails with The album leaf???
            #assumes artist is the last 4 data array items and fucks it up
    if len(data) == 8:
        print data[5]
        if data[7].__contains__('Audio'):
            data = stripData(data)
            data = '1' + str(data)
            print data
            newFile.write(data)
            newFile.flush()
newFile.close()
mtpList.close()