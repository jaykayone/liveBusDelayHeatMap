from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )
from papyrus.renderers import GeoJSON

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    
    try:
        #create the tables if they do not yet exist
        Base.metadata.create_all(engine)
    pass:
        pass
    
    config.add_renderer('geojson', GeoJSON())
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('latest', '/latest')
    config.add_route('data_for_timestamp', '/data_for_timestamp')
    config.add_route('data_for_timestamp_and_line', '/data_for_timestamp/:line')
    config.add_route('timestamps', '/timestamps')
    config.add_route('lines_for_timestamp', '/lines_for_timestamp')

    config.scan()
    return config.make_wsgi_app()
