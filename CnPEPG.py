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
    #~ print bc["start"]
    #~ print bc["end"]
    #~ print bc["duration"]
    #pr = bc["programme"]
    
    #~ print pr["@type"]
    #~ print pr["pid"]
    #~ print unidecode(pr["title"])
    #~ print unidecode(pr["display_titles"]["title"])
    #~ print unidecode(pr["display_titles"]["subtitle"])
    #~ print unidecode(pr["short_synopsis"])
   # pp = pr.get("programme")
    #~ if pp:
        #~ print pp["@type"]
        #~ print pp["pid"]
        #~ print unidecode(pp["title"])

    #pid = pr["pid"]

    #channel_name = js["schedule"]["service"]["title"]
    cn = bc["@channel"]
    
    if cn == u'Rete 4':
 #       print 'Replacing Rete 4 with Rete4'
        channel_name = u'Rete4'
    elif cn == u'Canale 5':
 #       print 'Replacing Canale 5 with Canale5'
        channel_name = u'Canale5'
    elif cn == u'Italia 1':
  #      print 'Replacing Italia 1 with Italia1'
        channel_name  = u'Italia1'
    else:
        channel_name = cn
        
    #print 'Channel="'+channel_name+'"'
    
    
    
    p = ( channel_name, )
    c.execute('SELECT id FROM channel WHERE name = ?', p)
    row = c.fetchone()
    if not row:
 #       print "Channel name \"{0}\" not found in sqlite DB, next...".format(channel_name)
        continue
    
    channel = row[0]
    #~ print channel_name, channel
    pstart = bc["@start"]
    start_date = int(datetime.datetime.strptime(pstart.split('+')[0], '%Y%m%d%H%M%S ').strftime("%s"))
    start_date = start_date / 60
    
    pend = bc["@stop"]
    end_date = int(datetime.datetime.strptime(pend.split('+')[0], '%Y%m%d%H%M%S ').strftime("%s"))
    end_date = end_date / 60

    #line = pr["display_titles"].get("title")
    line = bc["title"]["#text"]

    if line:
        title = unidecode(line)
    else:
        title = 'Titolo Non Disponibile'

#    line = pr["display_titles"].get("subtitle")
#    if line:
#        subtitle = unidecode(line)
#    else:
    subtitle = None

    description = None
    ptype = None
    year = None
    country = None
    bid = None
    parental = None

#    if pp:
#        serie = pp["pid"]
#    else:
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

    #duration = bc["duration"]
    duration = end_date - start_date

    #p = ( pid, channel, end_date, title, subtitle, serie, duration )
    p = (channel_name,  title,  end_date,  duration)
    print p
    #~ print p

#    c.execute('INSERT INTO show(id,channel,end_date,title,subtitle,serie,duration) \
#                VALUES(?,?,?,?,?,?,?)', p )

    #~ print ""

conn.commit()
conn.close()



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

