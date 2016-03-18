#!/bin/bash
# Windows

[ -f AddChannels.sql ] && echo "Channels already there" && exit 1

UNZIP='C:\Progra~1\7-Zip\7z.exe'
ZIP='C:\Progra~1\7-Zip\7z.exe'
SQLITE3='./sqlite3.exe'
UNZIP_OPT='x -y'
ZIP_OPT='u'

cat > AddChannels.sql <<EOD
DELETE FROM channel where id BETWEEN 400 and 500 ;
INSERT INTO channel VALUES(401,'Giallo','29.516.16','',38,0,'Europe/Rome',0);
INSERT INTO channel VALUES(402,'TOPcrime','272.905.2150','',39,0,'Europe/Rome',0);
INSERT INTO channel VALUES(403,'Boing','272.905.145','',40,0,'Europe/Rome',0);
INSERT INTO channel VALUES(404,'Cartoonito','272.905.147','',46,0,'Europe/Rome',0);
INSERT INTO channel VALUES(405,'Super!','29.514.106','',47,0,'Europe/Rome',0);
INSERT INTO channel VALUES(407,'TGCOM24','272.940.4014','',51,0,'Europe/Rome',0);
INSERT INTO channel VALUES(408,'DMAX','29.516.50','',52,0,'Europe/Rome',0);
INSERT INTO channel VALUES(409,'Focus TV','8572.31000.25','',56,0,'Europe/Rome',0);
INSERT INTO channel VALUES(410,'Fine Living','272.905.154','',49,0,'Europe/Rome',0);
INSERT INTO channel VALUES(411,'Marco Polo','29.514.102/29.514.75','',61,0,'Europe/Rome',0);
INSERT INTO channel VALUES(412,'Nuvolari','29.514.101/29.514.85','',60,0,'Europe/Rome',0);
INSERT INTO channel VALUES(413,'Alice','29.514.70','',221,0,'Europe/Rome',0);
INSERT INTO channel VALUES(414,'Leonardo','29.514.105/29.514.80','',62,0,'Europe/Rome',0);
INSERT INTO channel VALUES(415,'HSE24','29.516.22','',37,0,'Europe/Rome',0);
INSERT INTO channel VALUES(416,'Agon','29.516.10','',33,0,'Europe/Rome',0);
INSERT INTO channel VALUES(417,'RTL 102.5 TV','29.516.21','',36,0,'Europe/Rome',0);
INSERT INTO channel VALUES(418,'Gazzetta TV','29.514.50','',59,0,'Europe/Rome',0);
INSERT INTO channel VALUES(419,'Rai Scuola','318.2.8564','',146,0,'Europe/Rome',0);
INSERT INTO channel VALUES(420,'Paramount Channel','8572.31000.3','',50,0,'Europe/Rome',0);
INSERT INTO channel VALUES(421,'Sky TG24','8572.31000.5','',50,0,'Europe/Rome',0);
EOD

$UNZIP $UNZIP_OPT epg.v2.sqlite.zip
$SQLITE3 epg.v2.sqlite < AddChannels.sql
$ZIP $ZIP_OPT epg.v2.sqlite.zip epg.v2.sqlite

echo "Channels Added"
exit 0
