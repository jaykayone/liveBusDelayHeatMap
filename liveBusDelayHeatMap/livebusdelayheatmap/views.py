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
    t = request.params.get('timestamp', None)
    l = request.params.get('line', None)

    return {'timestamps': timestamps(None),
            'lines': lines_for_timestamp(None),
            'a': 'a',
            'selected_timestamp': t,
            'selected_line': l}


@view_config(route_name='data', renderer='geojson')
def data(request):
    t = request.params.get('timestamp', None)
    l = request.params.get('line', None)
    if l == 'all':
        l = None
    try:
        if t and not l:
            print "bazinga"
            d = dateutil.parser.parse(t)
            delays = DBSession.query(BusDelay).filter(BusDelay.time == d).all()
        elif t and l:
            d = dateutil.parser.parse(t)
            delays = DBSession.query(BusDelay).filter(and_(BusDelay.time == d, BusDelay.line == l)).all()
        elif not t and l:
            delays = DBSession.query(BusDelay).filter(BusDelay.line == l).all()
        else:
            latest_time = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first()
            if latest_time:
                delays = DBSession.query(BusDelay).filter(BusDelay.time == latest_time.time).all()
            else:
                delays = {}

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type': 'FeatureCollection', 'features': delays}


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


@view_config(route_name='lines', renderer='json')
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
    return {'lines': sorted(output)}
