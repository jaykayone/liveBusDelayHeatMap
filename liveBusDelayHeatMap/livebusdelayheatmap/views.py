from pyramid.response import Response
from pyramid.view import view_config
from datetime import datetime
import dateutil.parser

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    BusDelay,
    Station
)


## TODO: CRONJOB FOR PREPAREDATA
## TODO: INSTALL POSTGIS IN CONTAINER
## TODO: ADD LOGIC TO CHOOSE TIMESTAMP AND LINE
## TODO: BETTER STYLING

@view_config(route_name='home', renderer='templates/index.pt')
def home(request):
    return {}


@view_config(route_name='data_for_timestamp', renderer='geojson')
def data_for_timestamp(request):
    try:
        d = dateutil.parser.parse(request['date'])
        delays = DBSession.query(BusDelay).filter(BusDelay.time == d).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}

@view_config(route_name='data_for_timestamp_and_line', renderer='geojson')
def data_for_timestamp_and_line(request):
    try:
        d = dateutil.parser.parse(request['date'])
        l = request['line']
        delays = DBSession.query(BusDelay).filter(BusDelay.time == d and BusDelay.line == line).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}

@view_config(route_name='timestamps', renderer='json')
def timestamps(request):
    try:
       ts = DBSession.query(BusDelay).group_by(BusDelay.time).all()
    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'timestamps':ts}
    
@view_config(route_name='latest', renderer='geojson')
def latest(request):
    try:
        latest_time = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first()
        delays = DBSession.query(BusDelay).filter(BusDelay.time == latest_time.time).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}

@view_config(route_name='lines_for_timestamp', renderer='json')
def lines_for_timestamp(request):
    try:
        d = dateutil.parser.parse(request['date'])
        lines = DBSession.query(BusDelay).filter(BusDelay.time == d).group_by(BusDelay.line).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'lines': lines}
