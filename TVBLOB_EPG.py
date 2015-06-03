#!/usr/bin/python

# Parsing del .json e creazione dei comandi sqlite3 per inserire in BB

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

#~ print(infil)

bc = js["schedule"]["day"].get("broadcasts")

if not bc:
    print("Nessun Programma Disponibile per", js["schedule"]["service"]["title"])
    sys.exit(1)

print(js["schedule"]["service"]["title"])

conn = sqlite3.connect('epg.v2.sqlite')
c = conn.cursor()

for bc in js["schedule"]["day"]["broadcasts"]["broadcast"]:
    #~ print(bc["start"])
    #~ print(bc["end"])
    #~ print(bc["duration"])
    pr = bc["programme"]
    #~ print(pr["@type"])
    #~ print(pr["pid"])
    #~ print(unidecode(pr["title"]))
    #~ print(unidecode(pr["display_titles"]["title"]))
    #~ print(unidecode(pr["display_titles"]["subtitle"]))
    #~ print(unidecode(pr["short_synopsis"]))
    pp = pr.get("programme")
    #~ if pp:
        #~ print(pp["@type"])
        #~ print(pp["pid"])
        #~ print(unidecode(pp["title"]))

    pid = pr["pid"]

    channel_name = js["schedule"]["service"]["title"]
    p = ( channel_name, )
    c.execute('SELECT id FROM channel WHERE name = ?', p)
    row = c.fetchone()
    channel = row[0]
    #~ print(channel_name, channel)

    pend = bc["end"]
    end_date = int(datetime.datetime.strptime(pend.split('+')[0], '%Y-%m-%dT%H:%M:%S').strftime("%s"))
    end_date = end_date / 60

    line = pr["display_titles"].get("title")
    if line:
        title = unidecode(line)
        title = title.title()
    else:
        title = 'Titolo Non Disponibile'

    line = pr["display_titles"].get("subtitle")
    if line:
        subtitle = unidecode(line)
    else:
        subtitle = None

    description = None
    ptype = None
    year = None
    country = None
    bid = None
    parental = None

    if pp:
        serie = pp["pid"]
    else:
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

    duration = bc["duration"]

    p = ( pid, channel, end_date, title, subtitle, serie, duration )
    #~ print(p)

    c.execute('INSERT INTO show(id,channel,end_date,title,subtitle,serie,duration) \
                VALUES(?,?,?,?,?,?,?)', p )

    #~ print("")

conn.commit()
conn.close()



# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

