from pyramid.response import Response
from pyramid.view import view_config
from natsort import natsort
import dateutil.parser

from sqlalchemy.exc import DBAPIError
from sqlalchemy import and_
from sqlalchemy import func


from .models import (
    DBSession,
    BusDelay,
    BusAverageDelay,
    BusAverageDelayPerLine
)



## TODO: BETTER STYLING
## TODO: timestamp formatting
## TODO: Add UI for LINE AND TIME
## TODO: LOG TO CONTAINER

@view_config(route_name='home', renderer='templates/index.pt')
def home(request):
    t = request.params.get('timestamp', None)
    if t is None:
        ts = timestamps(None)
        print ts
        t = sorted(ts["timestamps"], reverse=True)[0]
    l = request.params.get('line', None)
    print timestamps(None)
    return {'timestamps': timestamps(None),
            'lines': lines_for_timestamp(None),
            'a': 'a',
            'selected_timestamp': t,
            'selected_line': l}


@view_config(route_name='data', renderer='geojson')
def data(request):
    t = request.params.get('timestamp', None)
    l = request.params.get('line', None)
    ## We made a try to group by location and id, but geometry does not seem to be group_by_able
    ## We could calculate mean delay per station ID but not include the geom in the result
    g = request.params.get('grouped', False)
    ##

    if l == 'all':
        l = None
    try:
        if t and not l:
            d = dateutil.parser.parse(t)
            if not g:
                delays = DBSession.query(BusDelay).filter(BusDelay.time == d).all()
            else:
                delays = DBSession.query(BusAverageDelay).filter(BusDelay.time == d).all()
        elif t and l:
            d = dateutil.parser.parse(t)
            if not g:
                delays = DBSession.query(BusDelay).filter(and_(BusDelay.time == d, BusDelay.line == l)).all()
            else:
                delays = DBSession.query(BusAverageDelayPerLine).filter(and_(BusAverageDelayPerLine.time == d,
                                                                             BusAverageDelayPerLine.line == l)).all()

        elif not t and l:
            if not g:
                delays = DBSession.query(BusDelay).filter(BusDelay.line == l).all()
            else:
                delays = DBSession.query(BusAverageDelayPerLine).filter(BusAverageDelayPerLine.line == l).all()
        else:
            latest_time = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first()
            if latest_time:
                if not g:
                    delays = DBSession.query(BusDelay).filter(BusDelay.time == latest_time.time).all()
                else:
                    delays = DBSession.query(BusAverageDelay).filter(BusAverageDelay.time == latest_time.time).all()
            else:
                delays = {}

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type': 'FeatureCollection', 'features': delays}


@view_config(route_name='timestamps', renderer='json')
def timestamps(request):
    try:
        ts = DBSession.query(BusDelay.time).group_by(BusDelay.time).all()
        out = {}
        for t in ts:
            out[t[0].isoformat()] = t[0].strftime('%d.%m.%Y %H:%M')
    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'timestamps': out}


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
    return {'lines': natsort(output)}
