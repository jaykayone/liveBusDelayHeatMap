
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from geoalchemy2 import Geometry

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
import geoalchemy2.functions as geofunc

from papyrus.geo_interface import GeoInterface


DBSession = scoped_session(sessionmaker())
Base = declarative_base()


class Station(Base):
    __tablename__ = 'stations'
    gid = Column(Integer, primary_key=True)
    id = Column(Integer)
    name = Column(String)
    geom = Column(Geometry('POINT', srid=4326))
    time = Column(DateTime, index=True)
    has_delaydata = Column(Boolean)


class BusDelay(GeoInterface,Base):
    __tablename__ = 'busdelays'
    gid = Column(Integer, primary_key=True)
    id = Column(Integer)
    name = Column(String)
    line = Column(String,index=True)
    delay = Column(Float)
    geom = Column(Geometry('POINT', srid=4326))
    time = Column(DateTime, index=True)


class BusAverageDelayPerLine(GeoInterface, Base):
    __tablename__ = 'v_bus_average_delays_by_line'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    line = Column(String)
    mean_delay = Column(Float)
    weight = Column(Float)
    geom = Column(Geometry('POINT', srid=4326))
    time = Column(DateTime, index=True)


class BusAverageDelay(GeoInterface, Base):
    __tablename__ = 'v_bus_average_delays'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    mean_delay = Column(Float)
    weight = Column(Float)
    geom = Column(Geometry('POINT', srid=4326))
    time = Column(DateTime, index=True)
