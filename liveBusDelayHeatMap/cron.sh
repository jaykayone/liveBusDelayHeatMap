#!/bin/sh
sh /app/getDelayData_full.sh
/usr/sbin/cron -f
