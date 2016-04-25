FROM grahamdumpleton/mod-wsgi-docker:python-2.7
RUN apt-get update && apt-get install -y python-pip virtualenv git libpq-dev libproj-dev libgeos-dev libgdal-dev
ENV appdir /app
WORKDIR /app
##CREATE VIRTUAL ENV
RUN mkdir -p ${appdir}
RUN cd ${appdir} && virtualenv env
#INSTALL WSSECURITY STUFF
RUN echo alias ll=\'ls -lisa\' >> ~/.bashrc
RUN /bin/bash -c "source ${appdir}/env/bin/activate && pip install --upgrade pip && pip install --upgrade setuptools"
RUN git clone https://github.com/jaykayone/liveBusDelayHeatMap.git
COPY app.wsgi /app/app.wsgi
COPY getDelayData_full.sh /app/getDelayData_full.sh
COPY getDelayData_incremental.sh /app/getDelayData_incremental.sh
RUN /bin/bash -c "chmod o+x *.sh"
RUN /bin/bash -c "source ${appdir}/env/bin/activate && pip install -r ${appdir}/liveBusDelayHeatMap/liveBusDelayHeatMap/requirements.txt"
RUN /bin/bash -c "source ${appdir}/env/bin/activate && cd ${appdir}/liveBusDelayHeatMap/liveBusDelayHeatMap && python setup.py install"
COPY production.ini ${appdir}/liveBusDelayHeatMap/liveBusDelayHeatMap/production.ini
RUN chown -R whiskey: ${appdir} && chmod a+x ${appdir}/app.wsgi && chmod 400 ${appdir}/liveBusDelayHeatMap/liveBusDelayHeatMap/production.ini

#DEFINE ENTRYPOINT
ENTRYPOINT mod_wsgi-docker-start ${appdir}/app.wsgi --user=www-data --group=root --python-path=${appdir}/env/lib/python2.7/site-packages/
EXPOSE 80
