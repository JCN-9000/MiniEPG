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

def _type(scat):
    """
    Handle categorization
    Needs some reworking on case management ( upper, lower, title ... )
    """

    xml_types = {
    'Altri Eventi Sportivi': 7,
    'Animazioni': 16,
    'Approfondimento': 0,
    'Attualita\'': 6,
    'Avventura' : 0,
    'Azione' : 0,
    'Biografico' : 0,
    'Cartone animato' : 16,
    'Cartoon' : 16,
    'Comico' : 0,
    'Commedia' : 0,
    'Concerto' : 17,
    'Cucina e Sapori' : 29,
    'Cultura' : 24,
    'Dibattito' : 0,
    'Di Montaggio' : 0,
    'Divulgazione Scientifico/Culturale' : 0,
    'Docu-Fiction' : 0,
    'Documentari' : 12,
    'Documentario' : 12,
    'Documentaristico' : 12,
    'Docu-Soap' : 15,
    'Docutainment' : 12,
    'Drammatico' : 0,
    'Fantascienza' : 0,
    'Fantastico/Favolistico' : 0,
    'Fiction' : 0,
    'Film' : 6,
    'Film TV' : 6,
    'Funzione Religiosa' : 25,
    'Game show' : 14,
    'Game Show/Quiz' : 14,
    'Giallo' : 0,
    'Guerra' : 0,
    'Horror' : 0,
    'Intrattenimento' : 3,
    'Manifestazione Sportiva' : 7,
    'Mondo e tendenze' : 4,
    'Musica' : 17,
    'Natura/Ambiente/Etnologia' : 0,
    'News' : 2,
    'Novelas' : 8,
    'Poliziesco' : 0,
    'Programma di servizio' : 0,
    'Programma musicale' : 17,
    'Programmi culturali' : 24,
    'Programmi religiosi' : 25,
    'Reality' : 19,
    'Real TV' : 19,
    'Religione' : 25,
    'Riassunto telenovelas' : 8,
    'Rotocalco' : 0,
    'Rubrica attualita\' sportiva' : 7,
    'Rubrica autopromozionale' : 0,
    'Rubrica di attualita\'' : 2,
    'Rubrica di servizio' : 0,
    'Salute' : 26,
    'Sentimentale' : 0,
    'Serie' : 9,
    'Shopping' : 21,
    'Sit-com' : 22,
    'Sitcom' : 22,
    'Soap' : 15,
    'Soap opera' : 15,
    'Spionaggio' : 20,
    'Sport' : 7,
    'Storico' : 0,
    'Talk show' : 11,
    'Telefilm' : 9,
    'Telenovela' : 8,
    'Telegiornale' : 2,
    'Telegiornale sportivo' : 2,
    'Telegiornali' : 2,
    'Thriller' : 0,
    'Turismo/geografia/etnologia' : 0,
    'Varieta\'' : 0,
    'Western' : 0,
    }

    typ=None

    if scat:
        #~ print scat
        if isinstance(scat,list):
            cat = scat[0].get("#text")
        else:
            cat = scat.get("#text")
        cat=cat.split('<')[0]

        xtyp = xml_types.get(cat.title())
        if xtyp:
            typ=xtyp

        #~ print typ, cat
    return typ

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
    elif name == u'Tv2000':
        newname = u'Tv 2000'
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
            if title[0:4] == u'dvd ':
                title = title[4:]
                ptype = 6 # FILM
            elif title[0:20] == u'Recensione del film ':
                title = title[20:]
                ptype = 6 # FILM
            elif title[0:11] == u'Soundtrack ':
                title = title[11:]
                ptype = 6
        else:
            title = 'Titolo Non Disponibile'
        
        typ = _type(prog.get("category"))
        if typ:
            if not ptype:
                ptype = typ

        description = None
        if prog.get("desc"):
            description = unidecode(_text(prog["desc"]))
            #print "** Desc \'{0}\'".format(description)

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
