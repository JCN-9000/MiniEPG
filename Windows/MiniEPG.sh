#!/bin/bash

## WINDOWS Vwerision
## Uses Gow as Unix System

## Proxy Settings if behind firewall
#PU='--proxy-user=USER'
#PP='--proxy-password=PASS'
#export HTTP_PROXY=http://ITTRN1S8PX02.fiatauto.com:8080/
PU=
PP=

# Path to zip compatible Program
UNZIP='C:\Progra~1\7-Zip\7z.exe'
ZIP='C:\Progra~1\7-Zip\7z.exe'

DO_TVB=0
DO_CNP=0
DO_RYC=1

[ -f epg.v2.sqlite.zip ] || wget $PU $PP http://epgadmin.tvblob.com/static/epg.v2.sqlite.zip
$UNZIP x -y epg.v2.sqlite.zip

echo "-- SQL per EPG BBox" > MiniEPG-prima.sql
echo "-- Operazioni Preliminari" >> MiniEPG-prima.sql
echo "-- " >> MiniEPG-prima.sql

echo "DROP INDEX 'show_idx' ;"        >> MiniEPG-prima.sql
echo "DELETE FROM show ;"             >> MiniEPG-prima.sql
echo "-- PRAGMA journal_mode = MEMORY; " >> MiniEPG-prima.sql
echo "-- BEGIN TRANSACTION; "            >> MiniEPG-prima.sql
./sqlite3.exe epg.v2.sqlite < MiniEPG-prima.sql

if [ $DO_TVB -eq 1 ]
then
	echo "Download EPG da TVBLOB"
# Download http://epgadmin.tvblob.com/api/services
# Loop in keys and get EPG
	[ -f services.xml ] || wget $PU $PP -O services.xml http://epgadmin.tvblob.com/api/services
	python xml2json.py -t xml2json --pretty -o services.json services.xml

	grep key services.json | tr -d '",' | while read Key Channel
	do
	#    echo $Channel
		wget $PU $PP  -O $Channel.0.xml http://epgadmin.tvblob.com/api/$Channel/programmes/schedules/today
		[ -f $Channel.0.xml  ] && python xml2json.py -t xml2json -o $Channel.0.json $Channel.0.xml && rm $Channel.0.xml
		[ -f $Channel.0.json ] && python TVBLOB_EPG.py $Channel.0.json ; rm $Channel.0.json
		wget $PU $PP  -O $Channel.1.xml http://epgadmin.tvblob.com/api/$Channel/programmes/schedules/tomorrow
		[ -f $Channel.1.xml  ] && python xml2json.py -t xml2json -o $Channel.1.json $Channel.1.xml && rm $Channel.1.xml 
		[ -f $Channel.1.json ] && python TVBLOB_EPG.py $Channel.1.json ; rm $Channel.1.json

	done
fi


#
# Download CutAndPasta EPG xml file and use to complement tvblob data 
#
if [ $DO_CNP -eq 1 ]
then
	echo "Download EPG da CutAndPasta"
	rm -f cnp-epg.xml cnp-epg.json
	wget $PU $PP -q -O cnp-epg.xml http://www.cutandpasta.it/xmltvita/epg.xml
	[ -f cnp-epg.xml ] && python xml2json.py -t xml2json -o cnp-epg.json cnp-epg.xml && python XMLTV_EPG.py cnp-epg.json
fi

#
# manage rytec_clouditaly_xmltv
#

echo "Download EPG da CloudItaly"
# get zip with pointers 
if [ ! -f files_crossepg_last.zip ]
then
    wget $PU $PP -q -N http://clouditaly.tk/files/files_crossepg_last.zip
    $UNZIP x files_crossepg_last.zip
    mv "files_crossepg(revD2)/rytec_clouditaly_xmltv.conf" .
    rm -rf "files_crossepg(revD2)/"
fi

if [ -f rytec_clouditaly_xmltv.conf ]
then
    if [ ! -f rytec_clouditaly_xmltv.sh ]
    then
# Cleanup file
		grep -v description rytec_clouditaly_xmltv.conf > rytec_clouditaly_xmltv.sh
#        sed -i -e 's/=/=''/' rytec_clouditaly_xmltv.conf
#        sed -i -e 's/$/"/' rytec_clouditaly_xmltv.conf
#        sed -i -s 's/^"$//' rytec_clouditaly_xmltv.conf
#        cp rytec_clouditaly_xmltv.conf rytec_clouditaly_xmltv.sh
    fi

# Download XMLTV EPG - Only if it has changed since last time.
    source rytec_clouditaly_xmltv.sh
    wget $PU $PP -q -N $epg_url_0 || wget -q -N $epg_url_1

# Expand and load into DB
    if [ -f rytecxmltvItaly.gz ]
    then
        rm rytecxmltvItaly.json
        gzip -cd rytecxmltvItaly.gz > rytecxmltvItaly.xml
        touch -r rytecxmltvItaly.gz rytecxmltvItaly.xml
        python xml2json.py -t xml2json -o  rytecxmltvItaly.json rytecxmltvItaly.xml
        python XMLTV_EPG.py rytecxmltvItaly.json 
		#| tee rytecxmltvItaly.log
    fi
fi



echo "-- SQL per EPG BBox" > MiniEPG-dopo.sql
echo "-- Operazioni di Conclusione" >> MiniEPG-dopo.sql
echo "-- " >> MiniEPG-dopo.sql
echo "UPDATE show SET is_premiere=0, is_hd=0, is_premium=0, is_live=0, is_lis=0, is_subtitled=0 ;" >> MiniEPG-dopo.sql
echo "-- END TRANSACTION; "              >> MiniEPG-dopo.sql
echo 'CREATE INDEX "show_idx" ON show (channel ASC, end_date ASC, type ASC);' >> MiniEPG-dopo.sql
./sqlite3.exe epg.v2.sqlite < MiniEPG-dopo.sql


$ZIP u epg.v2.sqlite.zip epg.v2.sqlite





# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

