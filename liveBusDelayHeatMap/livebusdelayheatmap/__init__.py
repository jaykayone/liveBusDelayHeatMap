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

        # drop the newly created tables and replace them by views (did not find how to do this otherwise, but works)
    s0a = text("""drop view v_bus_delays_concat""")
    s0b = text("""create or replace view v_bus_delays_concat as
select *, '<tr><td> ' || line || '</td><td>' || destination || '</td><td>' || delay ||
'min</td><td>' || to_char(departure,'HH24:MI') || '</td></tr>' as formatted from busdelays order by formatted asc;""")
    s1a = text("""drop table v_bus_average_delays_by_line;""")
    s1b = text("""drop view v_bus_average_delays_by_line;""")
    s1c = text("""create or replace view v_bus_average_delays_by_line as
                select id,time,geom,name,line,avg(delay) as mean_delay,
                string_agg(formatted ,'') as formatted_delay_info,
                avg(delay)/ 5 as weight from v_bus_delays_concat
                group by (id,time,geom,name,line);""")

    s2a = text("""drop table v_bus_average_delays;""")
    s2b = text("""drop view v_bus_average_delays;""")
    s2c = text("""create or replace view v_bus_average_delays as
                  select id,time,geom,name,avg(delay) as mean_delay,
                  string_agg(formatted ,'') as formatted_delay_info , avg(delay)/ 5 as weight from v_bus_delays_concat
                  group by (id,time,geom,name);""")
    i1 = text("""CREATE INDEX bus_average_delays_idx ON busdelays (id,time,geom,name);""")
    i2 = text("""CREATE INDEX bus_average_delays_by_line_idx ON busdelays (id,time,geom,name,line);""")
    c = engine.connect()
    try:
        c.execute(s2b)
    except:
        pass
    try:
        c.execute(s1b)
    except:
        pass
    try:
        c.execute(s0a)
    except:
        pass
    try:
        c.execute(s0b)
    except:
        pass
    try:
        c.execute(s1a)
    except:
        pass

    try:
        c.execute(s1c)
    except:
        pass

    try:
        c.execute(s2a)
    except:
        pass
    try:
        c.execute(s2c)
    except:
        pass
    try:
        c.execute(i1)
    except:
        pass
    try:
        c.execute(i2)
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
