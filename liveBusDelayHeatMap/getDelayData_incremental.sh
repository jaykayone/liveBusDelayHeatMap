#!/bin/bash
export TZ=Europe/Luxembourg
cd /app/liveBusDelayHeatMap/liveBusDelayHeatMap/livebusdelayheatmap/
/app/env/bin/python prepareData.py ../production.ini False
