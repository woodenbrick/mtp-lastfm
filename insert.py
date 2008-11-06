import string
import sqlite3

def getInfo(line):
    l = string.split(line, ': ')[1][:-1]
    return l

def stripData(data):
    '''Remove times and milliseconds and convert items 5 and 6'''
    data[0] = int(data[0])
    data[5] = int(string.split(data[5], ' ')[0]) / 1000
    data[6] = int(string.split(data[6], ' ')[0])
    return data
count = 0
conn = sqlite3.Connection('./lastfm')
c = sqlite3.Cursor(conn)
f = file('./mtp-tracklisting', 'r')
data = []
for line in f.readlines():
    requiredData = ('Title', 'Artist', 'Album', 
                    'Track number', 'Duration', 'Use count')
    if line.__contains__('Track ID'):
        data = [getInfo(line)]
    if line.startswith('  '):
        for item in requiredData:
            if line.__contains__(item):
                data.append(getInfo(line))
                #what to do?
            #bug: fails with The album leaf???
            #assumes artist is the last 4 data array items and fucks it up
    if len(data) == 7:
        print data
        data = stripData(data)
        #add to database if not in already
        c.execute("""select id, playcount from songs where id=?""", (data[0],))
        i = c.fetchone()
        if i == None:
            print 'song doesnt exist'
            numScrobbles = data[6]
            c.execute("""insert into songs (id, artist, song, 
                                                   album, tracknumber, duration, playcount) values
                                                   (?, ?, ?, ?, ?, ?, ?)""", (data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
            conn.commit()
        else:
            numScrobbles = data[6] - i[1]
            c.execute("""update songs set playcount=? where id=?""", (data[6], data[0]))
        if numScrobbles > 0:
            c.execute("""insert into scrobble (trackid, scrobbles) values (?, ?)""", (data[0], numScrobbles))
            conn.commit()
conn.close()

                 
            
            
            

            
            
    
