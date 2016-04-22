from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    BusDelay,
    Station
)




@view_config(route_name='home', renderer='templates/index.pt')
def home(request):
    return {}


@view_config(route_name='latest', renderer='geojson')
def latest(request):
    try:
        latest_time = DBSession.query(BusDelay).order_by(BusDelay.time.desc()).first()
        delays = DBSession.query(BusDelay).filter(BusDelay.time == latest_time.time).all()

    except DBAPIError:
        return Response("a problem occured", content_type='text/plain', status_int=500)
    return {'type':'FeatureCollection','features': delays}
