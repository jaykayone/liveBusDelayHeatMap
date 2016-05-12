#!/bin/bash
export TZ=Europe/Luxembourg
date
cd /app/liveBusDelayHeatMap/liveBusDelayHeatMap/livebusdelayheatmap
/app/env/bin/python prepareData.py ../production.ini True
