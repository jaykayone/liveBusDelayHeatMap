FROM grahamdumpleton/mod-wsgi-docker:python-2.7
RUN apt-get update && apt-get install -y python-pip virtualenv git
ENV appdir /app
##CREATE VIRTUAL ENV
RUN mkdir -p ${appdir}
RUN cd ${appdir} && virtualenv env
#INSTALL WSSECURITY STUFF
RUN echo alias ll=\'ls -lisa\' >> ~/.bashrc
RUN /bin/bash -c "source ${appdir}/env/bin/activate && pip install --upgrade pip && pip install --upgrade setuptools"
RUN git clone https://github.com/jaykayone/liveBusDelayHeatMap.git
COPY app.wsgi /app/app.wsgi
RUN /bin/bash -c "source ${appdir}/env/bin/activate && pip install -r ${appdir}/liveBusDelayHeatMap/liveBusDelayHeatMap/requirements.txt"
RUN /bin/bash -c "source ${appdir}/env/bin/activate && cd ${appdir}/liveBusDelayHeatMap/liveBusDelayHeatMap && python setup.py install"
RUN chown -R whiskey: ${appdir} && chmod a+x ${appdir}/app.wsgi && chmod 400 ${appdir}/geojson_reprojector/production.ini

#DEFINE ENTRYPOINT
ENTRYPOINT mod_wsgi-docker-start ${appdir}/app.wsgi --user=www-data --group=root --python-path=${appdir}/env/lib/python2.7/site-packages/
EXPOSE 80