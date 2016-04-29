from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy import text

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
    except:
        pass
    try:
        # drop the newly created tables and replace them by views (did not find how to do this otherwise, but works)
        s1 = text("""drop table v_bus_average_delays_by_line;
                    create view v_bus_average_delays_by_line as
                    select id,time,geom,name,line,avg(delay) as mean_delay, avg(delay)/ 10 as weight from busdelays
                    group by (id,time,geom,name,line);""")
        s2 = text("""drop table v_bus_average_delays;
                    create view v_bus_average_delays as
                    select id,time,geom,name,avg(delay) as mean_delay, avg(delay)/ 10 as weight from busdelays
                    group by (id,time,geom,name);""")
        c = engine.connect()
        c.execute(s1)
        c.execute(s2)
    except:
        pass

    
    config.add_renderer('geojson', GeoJSON())
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('data', '/data')
    config.add_route('timestamps', '/timestamps')
    config.add_route('lines', '/lines')

    config.scan()
    return config.make_wsgi_app()
