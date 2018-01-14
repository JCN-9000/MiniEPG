#!/bin/bash

## Linux Version
## Uses Standard Unix System

## Proxy Settings if behind firewall
#PU='--proxy-user=USER'
#PP='--proxy-password=PASS'
#export HTTP_PROXY=http://PROXY:PORT/
PU=
PP=

# Path to zip compatible Program
UNZIP='/usr/bin/unzip'
UNZIP_OPT='-o'
ZIP='/usr/bin/zip'
ZIP_OPT='-u'
WGET_OPT="-q $PU $PP"
SQLITE3='/usr/bin/sqlite3'
PYTHON='python'

DO_TVB=0
DO_CNP=0
DO_RYT=1

#[ -f epg.v2.sqlite.zip ] || wget $WGET_OPT http://epgadmin.tvblob.com/static/epg.v2.sqlite.zip
#$UNZIP $UNZIP_OPT epg.v2.sqlite.zip

#
# If we have an old zip file use it?
#
#[ -f epg.v2.sqlite.zip ] && $UNZIP $UNZIP_OPT epg.v2.sqlite.zip

# (Re)create empty DB 
rm -f epg.v2.sqlite
$SQLITE3 epg.v2.sqlite < create-empty-db.sql

echo "-- SQL per EPG BBox" > MiniEPG-prima.sql
echo "-- Operazioni Preliminari" >> MiniEPG-prima.sql
echo "-- " >> MiniEPG-prima.sql

echo "DROP INDEX 'show_idx' ;"        >> MiniEPG-prima.sql
echo "DELETE FROM show ;"             >> MiniEPG-prima.sql
echo "-- PRAGMA journal_mode = MEMORY; " >> MiniEPG-prima.sql
echo "-- BEGIN TRANSACTION; "            >> MiniEPG-prima.sql
$SQLITE3 epg.v2.sqlite < MiniEPG-prima.sql

if [ $DO_TVB -eq 1 ]
then
    echo "Download EPG da TVBLOB"
# Download http://epgadmin.tvblob.com/api/services
# Loop in keys and get EPG
    [ -f services.xml ] || wget $WGET_OPT -O services.xml http://epgadmin.tvblob.com/api/services
    $PYTHON xml2json.py -t xml2json --pretty -o services.json services.xml

    grep key services.json | tr -d '",' | while read Key Channel
    do
#    echo $Channel
        wget $WGET_OPT -O $Channel.0.xml http://epgadmin.tvblob.com/api/$Channel/programmes/schedules/today
        [ -f $Channel.0.xml  ] && $PYTHON xml2json.py -t xml2json -o $Channel.0.json $Channel.0.xml && rm $Channel.0.xml
        [ -f $Channel.0.json ] && $PYTHON TVBLOB_EPG.py $Channel.0.json ; rm $Channel.0.json
        wget $WGET_OPT -O $Channel.1.xml http://epgadmin.tvblob.com/api/$Channel/programmes/schedules/tomorrow
        [ -f $Channel.1.xml  ] && $PYTHON xml2json.py -t xml2json -o $Channel.1.json $Channel.1.xml && rm $Channel.1.xml 
        [ -f $Channel.1.json ] && $PYTHON TVBLOB_EPG.py $Channel.1.json ; rm $Channel.1.json

    done
fi

#
# Download CutAndPasta EPG xml file and use to complement tvblob data 
#
if [ $DO_CNP -eq 1 ]
then
    echo "Download EPG da CutAndPasta"
    rm -f cnp-epg.xml cnp-epg.json
    wget $WGET_OPT -O cnp-epg.xml http://www.cutandpasta.it/xmltvita/epg.xml
    [ -f cnp-epg.xml ] && $PYTHON xml2json.py -t xml2json -o cnp-epg.json cnp-epg.xml && $PYTHON XMLTV_EPG.py cnp-epg.json
fi

#
# manage rytec_clouditaly_xmltv
#

if [ $DO_RYT -eq 1 ]
then

#    epg_url_0=http://www.vuplus-community.net/rytec/rytecIT_Basic.xz
    epg_url_0=http://rytecepg.ipservers.eu/epg_data/rytecIT_Basic.xz

    echo "!!! Downloading $epg_url_0"
    wget $WGET_OPT -N $epg_url_0 
    echo "!!! Done"


# Expand and load into DB
    if [ -f rytecIT_Basic.xz ]
    then
	    echo "!!! Processing file rytecIT_Basic.xz"
	    xzcat rytecIT_Basic.xz > rytecxmltvItaly.xml 
	    touch -r rytecIT_Basic.xz rytecxmltvItaly.xml
	    $PYTHON xml2json.py -t xml2json -o  rytecxmltvItaly.json rytecxmltvItaly.xml
	    $PYTHON XMLTV_EPG.py rytecxmltvItaly.json | tee rytecxmltvItaly.log
	    #mv rytecxmltvItaly.xz rytecxmltvItaly.xz.old
	    mv rytecIT_Basic.xz rytecIT_Basic.xz.old
    else
	    echo "!!! No file rytecxmltvItaly.gz"
    fi
fi


echo "-- SQL per EPG BBox" > MiniEPG-dopo.sql
echo "-- Operazioni di Conclusione" >> MiniEPG-dopo.sql
echo "-- " >> MiniEPG-dopo.sql
echo "UPDATE show SET is_premiere=0, is_hd=0, is_premium=0, is_live=0, is_lis=0, is_subtitled=0 ;" >> MiniEPG-dopo.sql
echo "-- END TRANSACTION; "              >> MiniEPG-dopo.sql
echo 'CREATE INDEX "show_idx" ON show (channel ASC, end_date ASC, type ASC);' >> MiniEPG-dopo.sql
$SQLITE3 epg.v2.sqlite < MiniEPG-dopo.sql


$ZIP $ZIP_OPT epg.v2.sqlite.zip epg.v2.sqlite





# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

