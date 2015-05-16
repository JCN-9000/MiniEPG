#!/bin/bash

[ -f AddChannels.sql ] && echo "Channels already there" && exit 1

cat > AddChannels.sql <<EOD
DELETE FROM channel where id BETWEEN 400 and 500 ;
INSERT INTO channel VALUES(401,'Giallo','29.516.16','',38,0,'Europe/Rome',0);
INSERT INTO channel VALUES(402,'TOPcrime','272.905.2150','',39,0,'Europe/Rome',0);
INSERT INTO channel VALUES(403,'Boing','272.905.145','',40,0,'Europe/Rome',0);
INSERT INTO channel VALUES(404,'Cartoonito','272.905.147','',46,0,'Europe/Rome',0);
INSERT INTO channel VALUES(405,'Super!','29.514.106','',47,0,'Europe/Rome',0);
INSERT INTO channel VALUES(406,'LaEFFE','8572.31000.5','',50,0,'Europe/Rome',0);
INSERT INTO channel VALUES(407,'TGCOM24','272.940.4014','',51,0,'Europe/Rome',0);
INSERT INTO channel VALUES(408,'DMAX','29.516.50','',52,0,'Europe/Rome',0);
INSERT INTO channel VALUES(409,'Focus TV','8572.31000.25','',56,0,'Europe/Rome',0);
INSERT INTO channel VALUES(410,'Fine Living','272.905.154','',49,0,'Europe/Rome',0);
INSERT INTO channel VALUES(411,'Marco Polo','29.514.102/29.514.75','',61,0,'Europe/Rome',0);
INSERT INTO channel VALUES(412,'Nuvolari','29.514.101/29.514.85','',65,0,'Europe/Rome',0);
INSERT INTO channel VALUES(413,'Alice','29.514.70','',221,0,'Europe/Rome',0);
INSERT INTO channel VALUES(414,'Leonardo','29.514.105/29.514.80','',222,0,'Europe/Rome',0);
INSERT INTO channel VALUES(415,'HSE24','29.516.22','',37,0,'Europe/Rome',0);
INSERT INTO channel VALUES(416,'Agon','29.516.10','',33,0,'Europe/Rome',0);
EOD

unzip -o epg.v2.sqlite.zip
sqlite3 epg.v2.sqlite < AddChannels.sql
zip -u epg.v2.sqlite.zip epg.v2.sqlite

echo "Channels Added"
exit 0
