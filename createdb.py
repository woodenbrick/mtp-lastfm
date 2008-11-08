#One run only, creates a new db for last.fm scrobbles

import sqlite3
import os
try:
    os.remove('./lastfm')
except(OSError):
    print 'path doesnt exist'
if not os.path.exists('./lastfm'):
    conn = sqlite3.Connection('./lastfm')
    cursor = conn.cursor()
    query = ['''
    CREATE TABLE IF NOT EXISTS `scrobble` (
  `trackid` int(8) NOT NULL,
  `scrobbles` int(4) NOT NULL
)''', '''

CREATE TABLE IF NOT EXISTS `songs` (
  `trackid` int(8) NOT NULL,
  `artist` varchar(255) NOT NULL,
  `song` varchar(255) NOT NULL,
  `album` varchar(255) NOT NULL,
  `tracknumber` int(2) NOT NULL,
  `duration` int(6) NOT NULL,
  `usecount` int(6) NOT NULL,
  PRIMARY KEY  (`trackid`)
)''', '''

CREATE TABLE IF NOT EXISTS `users` (
  `id` varchar(2) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`)
)''']
    print 'Creating Tables'
    for q in query:
        print q
        cursor.execute(q)
        conn.commit()
    conn.close()
    