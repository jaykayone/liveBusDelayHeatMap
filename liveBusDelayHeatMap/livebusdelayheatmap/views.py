from pyramid.response import Response
from pyramid.view import view_config
import dateutil.parser

from sqlalchemy.exc import DBAPIError
from sqlalchemy import and_

from .models import (
    DBSession,
    BusDelay
)



## TODO: BETTER STYLING
## TODO: timestamp formatting
## TODO: Add UI for LINE AND TIME
## TODO: LOG TO CONTAINER

@view_config(route_name='home', renderer='templates/index.pt')
def home(request):
    return {'timestamps': timestamps(None),
            'lines': lines_for_timestamp(None),
            'a': 'a'}


@view_config(route_name='data_for_timestamp', renderer='geojson')
def data_for_timestamp(request):
    try:
        d = dateutil.parser.parse(request.params['datetime'])
        delays = DBSession.query(BusDelay).filter(BusDelay.time == d).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}

@view_config(route_name='data_for_timestamp_and_line', renderer='geojson')
def data_for_timestamp_and_line(request):
    try:
        d = dateutil.parser.parse(request.params['datetime'])
        l = request.matchdict['line']
        delays = DBSession.query(BusDelay).filter(and_(BusDelay.time == d, BusDelay.line == l)).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}

@view_config(route_name='timestamps', renderer='json')
def timestamps(request):
    try:
        ts = DBSession.query(BusDelay.time).group_by(BusDelay.time).all()
        out = []
        for t in ts:
            out.append(t[0].isoformat())
    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'timestamps': sorted(out)}
    
@view_config(route_name='latest', renderer='geojson')
def latest(request):
    try:
        latest_time = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first()
        if latest_time:
            delays = DBSession.query(BusDelay).filter(BusDelay.time == latest_time.time).all()
        else:
            delays = {}

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}


@view_config(route_name='latest_for_line', renderer='geojson')
def latest_for_line(request):
    try:
        l = request.matchdict['line']
        latest_time = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first()
        delays = DBSession.query(BusDelay).filter(and_(BusDelay.time == latest_time.time, BusDelay.line == l)).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type': 'FeatureCollection', 'features': delays}

@view_config(route_name='lines_for_timestamp', renderer='json')
def lines_for_timestamp(request):
    try:
        try:
            d = dateutil.parser.parse(request.params['datetime'])
        except:
            d = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first().time
        lines = DBSession.query(BusDelay.line).filter(BusDelay.time == d).group_by(BusDelay.line).all()
        output=[]
        for l in lines:
            output.append(l[0])
    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'lines': sorted(output, key=int)}
