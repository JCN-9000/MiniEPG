#!/usr/bin/python

"""
# Legge JSON file n format XMLTV e aggiorna DB sqlite
# Vedi anche
# http://www.cutandpasta.it
# http://sat.alfa-tech.net/clouditaly/rytecxmltvItaly.gz
"""

import sys
import datetime
import sqlite3
import json

from unidecode import unidecode


def _type(scat):
    """
    Handle categorization
    Needs some reworking on case management ( upper, lower, title ... )
    Need to assign/invent categories to undefined ones.
    """

    with open("types.json") as types_file:
        js = json.load(types_file)

    typ = None

    if scat:
        #~ print(scat)
        if isinstance(scat, list):
            cat = scat[0].get("#text")
        else:
            cat = scat.get("#text")
        cat = cat.split('<')[0]

        xtyp = js["xml_types"].get(cat.title())
        if xtyp:
            typ = xtyp

        #~ print(typ, cat)
    return typ


def _channel_name(name, aliases):
    """
    Handle inconsistent spelling of channel names
    """
    newname = aliases.get(name)
    return name if not newname else newname


def _mins_since_epoch(datestring):
    """
    Minutes since the Epoch from a given date string
    """
#    return int(datetime.datetime.strptime(datestring.split('+')[0],
#            '%Y%m%d%H%M%S ').strftime("%s")) / 60
    epoch = datetime.datetime(1970, 1, 1)
    sometime = datetime.datetime.strptime(datestring.split('+')[0],
                                          '%Y%m%d%H%M%S ')
# Ora Solare
#    return ((sometime - epoch).total_seconds() - 60*60) / 60
# Ora Legale
#    return ((sometime - epoch).total_seconds() - 120*60) / 60
# GMT
    return (sometime - epoch).total_seconds() / 60


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
        #        print( "Unnexpected Title type: \
        #        Channel={0} Start={1} title={2} class={3}".format(
        #                channel_name, start_date, title, title.__class__))
        text = str(title)
    return text


def _CleanupTitle(tit):
    tit = tit.replace('Film ', '', 1)
    tit = tit.replace('Telefilm ', '', 1)
    tit = tit.replace('Xxvii', 'XXVII')
    tit = tit.replace('Xxvi',  'XXVI')
    tit = tit.replace('Xxv',   'XXV')
    tit = tit.replace('Xxiv',  'XXIV')
    tit = tit.replace('Xxiii', 'XXIII')
    tit = tit.replace('Xxii',  'XXII')
    tit = tit.replace('Xxi',   'XXI')
    tit = tit.replace('Xx ',   'XX')
    tit = tit.replace('Xix',   'XIX')
    tit = tit.replace('Xviii', 'XVIII')
    tit = tit.replace('Xvii',  'XVII')
    tit = tit.replace('Xvi',   'XVI')
    tit = tit.replace('Xv',    'XV')
    tit = tit.replace('Xiv',   'XIV')
    tit = tit.replace('Xiii',  'XIII')
    tit = tit.replace('Xii',   'XII')
    tit = tit.replace('Xi',    'XI')
    tit = tit.replace('Ix',    'IX')
    tit = tit.replace('Viii',  'VIII')
    tit = tit.replace('Vii',   'VII')
    tit = tit.replace('Vi',    'VI')
    tit = tit.replace('Iv',    'IV')
    tit = tit.replace('Iii',   'III')
    tit = tit.replace('Ii',    'II')
    tit = tit.replace('Tgcom', 'TGCOM')
    tit = tit.replace('Tgr',   'TGR')
    tit = tit.replace('Tg',    'TG')
    tit = tit.replace('Wwe',   'WWE')
    tit = tit.replace('Wta',   'WTA')
    tit = tit.replace('Mtv',   'MTV')
##    tit = unidecode(tit).replace('\\','')
    tit = tit.replace('\\', '')
    return tit


def _load_file_as_json(file_):
    jcontent = None
    with open(file_) as f:
        jcontent = json.load(f)
    return jcontent


def main():
    """
    Parse JSON file, update SQLIte DB
    """
    filename = sys.argv[1]
    jsondata = _load_file_as_json(filename)
    prog = jsondata["tv"].get("programme")
    if not prog:
        print("Nessun Programma Disponibile in ", filename)
        sys.exit(1)

    # Load external alias file: aliases.json
    jaliases = _load_file_as_json('aliases.json')
    aliases = jaliases['aliases']

    conn = sqlite3.connect('epg.v2.sqlite')
    cursor = conn.cursor()

    chskip = ()
    chkeep = ()
    for prog in jsondata["tv"]["programme"]:
        channel_name = _channel_name(prog["@channel"], aliases)

        # Load existing channel data from DB
        params = (channel_name,)
        cursor.execute('SELECT id FROM channel WHERE name = ?', params)
        row = cursor.fetchone()
        if not row:
            if channel_name not in chskip:
                print("Ignoring unrecognised channel  \"{0}\" ".format(channel_name))
                chskip = channel_name
            continue
        if channel_name not in chkeep:
            print("Analisi dati EPG del canale   \"{0}\" ".format(channel_name))
            chkeep = channel_name

        channel = row[0]

        # Get start/end dates
        start_date = _mins_since_epoch(prog["@start"])
        end_date = _mins_since_epoch(prog["@stop"])

# Hint:
# Also get duration from DB and check if current start date is equal to DB start date
# meaning same show with different duration. Check delta duration < 10 min.
# Or check current end date between 13 min from DB end date: more or less same show

        params = (channel, end_date)
        cursor.execute('SELECT id FROM show WHERE channel = ? AND end_date= ?',
                       params)
        row = cursor.fetchone()
        if row:
            #print('Entry for show already present, skipping...')
            continue

        # Calculate duration, ignore empty or negative duration entries
        duration = end_date - start_date
        if duration <= 0:
            print('Ignoring entry with bad duration {0}'.format(
                (channel_name, start_date, end_date, duration)))
            continue

        # Generate unique ID from channel + timestamp
        pid = end_date + 100000000 * channel

        ptype = None

        line = _text(prog["title"])
        if line:
            title = unidecode(line)
            if title[0:4] == u'dvd ':
                title = title[4:]
                ptype = 6  # FILM
            elif title[0:20] == u'Recensione del film ':
                title = title[20:]
                ptype = 6  # FILM
            elif title[0:11] == u'Soundtrack ':
                title = title[11:]
                ptype = 6
        else:
            title = 'Titolo Non Disponibile'
        title = title.title()
        title = _CleanupTitle(title)

        typ = _type(prog.get("category"))
        if typ:
            if not ptype:
                ptype = typ

        description = None
        if prog.get("desc"):
            description = unidecode(_text(prog["desc"]))
            #print("** Desc \'{0}\'".format(description))

        params = (pid, channel, end_date, title, duration, ptype, description)
        #~ print(params)
        #~ print(unidecode(channel_name), end_date, title, duration)
        #~ print(".", end=" ")

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

