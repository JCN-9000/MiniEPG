#!/usr/bin/python

"""
# Legge JSON file creato da cutandpasta.it epg.xml e aggiorna DB sqlite
# Vedi anche
# http://www.cutandpasta.it
"""

import sys
import datetime
import sqlite3
import json

from unidecode import unidecode

def _channel_name(name):
    """
    Handle inconsistent spelling of channel names
    """
    if name == u'Rete 4':
        newname = u'Rete4'
    elif name == u'Canale 5':
        newname = u'Canale5'
    elif name == u'Italia 1':
        newname = u'Italia1'
    elif name == u'La 5':
        newname = u'La5'
    elif name == u'La7d':
        newname = u'La7D'
    elif name == u'Rai Sport1':
        newname = u'Rai Sport 1'
    elif name == u'Rai Sport2':
        newname = u'Rai Sport 2'
    elif name[0:9] == u'Rai 3 TGR':
        newname = u'Rai 3'
    else:
        newname = name
    return newname

def _mins_since_epoch(datestring):
    """
    Minutes since the Epoch from a given date string
    """
    return int(datetime.datetime.strptime(datestring.split('+')[0],
            '%Y%m%d%H%M%S ').strftime("%s")) / 60

def _text(title):
    """
    Extract text from tag element - if there are multiple elements, use first
    """
    if isinstance(title, dict):
        text = title["#text"]
    elif isinstance(title, list):
        # If there are multiple titles, take first
        # - a better plan would be to check language codes
        text = title[0]["#text"]
    else:
        #        print "Unnexpected Title type: \
        #        Channel={0} Start={1} title={2} class={3}".format(
        #                channel_name, start_date, title, title.__class__)
        text = str(title)
    return text

def main():
    """
    Parse JSON file, update SQLIte DB
    """
    filename = sys.argv[1]

    with open(filename) as data_file:
        jsondata = json.load(data_file)

    prog = jsondata["tv"].get("programme")

    if not prog:
        print "Nessun Programma Disponibile da cutandpasta.it"
        sys.exit(1)

    conn = sqlite3.connect('epg.v2.sqlite')
    cursor = conn.cursor()

    for prog in jsondata["tv"]["programme"]:
        channel_name = _channel_name(prog["@channel"])

        # Load existing channel data from DB
        params = (channel_name,)
        cursor.execute('SELECT id FROM channel WHERE name = ?', params)
        row = cursor.fetchone()
        if not row:
            print "Ignoring unrecognised channel  \"{0}\" ".format(channel_name)
            continue
        channel = row[0]

        # Get start/end dates
        start_date = _mins_since_epoch(prog["@start"])
        end_date = _mins_since_epoch(prog["@stop"])

        params = (channel, end_date)
        cursor.execute('SELECT id FROM show WHERE channel = ? AND end_date= ?',
            params)
        row = cursor.fetchone()
        if row:
            #print 'Entry for show already present, skipping...'
            continue

        # Calculate duration, ignore empty or negative duration entries
        duration = end_date - start_date
        if duration <= 0:
            print 'Ignoring entry with bad duration {0}'.format(
                (channel_name, start_date, end_date, duration))
            continue

        # Generate unique ID from channel + timestamp
        pid = end_date + 100000000 * channel

        ptype = None

        line = _text(prog["title"])
        if line:
            title = unidecode(line)
            if title[0:4] == 'dvd ':
                title = title[4:]
                ptype = 6 # FILM
        else:
            title = 'Titolo Non Disponibile'

        description = None
        if prog.get("desc"):
            description = unidecode(_text(prog["desc"]))
            print "** Desc \'{0}\'".format(description)

        params = (pid, channel, end_date, title, duration, ptype, description)
        #print params
        print unidecode(channel_name), end_date, title, duration

        cursor.execute('INSERT INTO show(id,channel,end_date,title,\
        duration,type,description) \
        VALUES(?,?,?,?,?,?,?)', params)

    conn.commit()
    conn.close()

#
# Main driver
#
if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
