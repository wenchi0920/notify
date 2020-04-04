#!/bin/bash

set -x

export LANG=zh_TW.UTF-8

dd=$(/bin/date "+%Y-%m-%d")
logDir="/home/notify/logs"

sudo -u notify mkdir /home/notify/logs /home/loha5/data > /dev/null 2>&1

sudo -u notify crontab /home/notify/docker/crontab.txt
/etc/init.d/cron restart

python3 /home/notify/app.py >> "${logDir}/app-${dd}.log" 2>>"${logDir}/app-${dd}.error"

