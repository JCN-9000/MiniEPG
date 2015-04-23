#!/bin/bash

# Customize where needed
# Put into a crontab line

cd $HOME/MiniEPG

bash MiniEPG.sh

cp epg.v2.sqlite.zip /var/www
