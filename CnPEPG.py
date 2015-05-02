#!/usr/bin/python

#
# Legge JSON file creato da cutandpasta.it epg.xml e aggiorna DB sqlite
#
# http://www.cutandpasta.it
#

import sys
import getopt
import datetime
import sqlite3
import json

from pprint import pprint
from unidecode import unidecode

infil = sys.argv[1]

with open(infil) as data_file:
    js = json.load(data_file)

bc = js["tv"].get("programme")

if not bc:
    print "Nessun Programma Disponibile per", js["schedule"]["service"]["title"]
    sys.exit(1)

conn = sqlite3.connect('epg.v2.sqlite')
c = conn.cursor()

for bc in js["tv"]["programme"]:
    cn = bc["@channel"]
    
    # Handle inconsistent spelling of channel names
    if cn == u'Rete 4':
        channel_name = u'Rete4'
    elif cn == u'Canale 5':
        channel_name = u'Canale5'
    elif cn == u'Italia 1':
        channel_name  = u'Italia1'
    else:
        channel_name = cn
    
    # Load existing channel data from DB
    p = ( channel_name, )
    c.execute('SELECT id FROM channel WHERE name = ?', p)
    row = c.fetchone()
    if not row:
        #       print "Ignoring unrecognised channel  \"{0}\" ".format(channel_name)
        continue
    channel = row[0]
  
    # Get start/end dates (used later for duration)
    pstart = bc["@start"]
    start_date = int(datetime.datetime.strptime(pstart.split('+')[0], '%Y%m%d%H%M%S ').strftime("%s"))
    start_date = start_date / 60
    
    pend = bc["@stop"]
    end_date = int(datetime.datetime.strptime(pend.split('+')[0], '%Y%m%d%H%M%S ').strftime("%s"))
    end_date = end_date / 60

    duration = end_date - start_date

    pid = end_date + 100000000 * channel

#assert not isinstance(lst, basestring)

    title = bc["title"]
    if isinstance(title,  dict):
        line = title["#text"]
    elif isinstance(title,  list):
        line is title[0]["#text"]
    else:
        print "Title is niether list nor dict! Channel={0} Start={1} title={2} class={3}".format(channel_name, start_date, title,  title.__class__)
        line = str(title)
        
    if line:
        title = unidecode(line)
    else:
        title = 'Titolo Non Disponibile'

    subtitle = None
    description = None
    ptype = None
    year = None
    country = None
    bid = None
    parental = None
    serie = None
    replica = None

    is_premiere = 0
    is_hd = 0
    is_premium = 0
    is_live = 0
    is_lis = 0
    is_subtitled = 0

    subtitle_page = None
    imdb_id = None
    twitter = None
    season = None
    episode = None
    thumbnail_url = None

    
    p = ( pid, channel, end_date, title, subtitle, serie, duration )
    print p
    #~ print p

#   c.execute('INSERT INTO show(id,channel,end_date,title,subtitle,serie,duration) \
#                VALUES(?,?,?,?,?,?,?)', p )

    #~ print ""

conn.commit()
conn.close()



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

