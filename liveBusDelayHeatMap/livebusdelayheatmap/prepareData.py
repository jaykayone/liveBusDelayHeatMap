import requests
import sys
import datetime

from shapely.geometry import Point

from geoalchemy2.shape import from_shape
from sqlalchemy import create_engine
from models import BusDelay, Station
from sqlalchemy.orm import sessionmaker
from requests_futures.sessions import FuturesSession
from concurrent.futures import ThreadPoolExecutor
from ConfigParser import SafeConfigParser


class BusStopDelay:
    def __init__(self, id, name, geom):
        self.id = id
        self.name = name
        self.geom = geom
        self.delays = []
        pass

    def set_delay(self, line, delay, number, departure, destination):
        array = [line, delay, number, departure, destination]
        self.delays.append(array)

    def __str__(self):
        print "id: %s" % self.id
        print "name: %s" % self.name
        print "geom: %s" % self.geom
        print "delays: %s" %self.delays


class DataPreparer:
    def __init__(self, init=True, config_file='../production.ini'):
        parser = SafeConfigParser()
        parser.read(config_file)
        engine = create_engine(parser.get('app:main', 'sqlalchemy.url'))#, echo=True)
        self.Session = sessionmaker(bind=engine)
        self.busStopArray = {}
        self.__get_bus_stops()
        if init:
            self.__push_bus_stops_to_postgis()
        self.__updateStationTags()
        self.latestUpdateStartTime = None
    pass

    def __push_bus_stops_to_postgis(self):
        print "pushing to postgis"

        session = self.Session()
        session.query(Station).delete()
        i=0
        for id in self.busStopArray:
            d = self.busStopArray[id]
            stop = Station(name=d.name,id=d.id,geom= from_shape(d.geom, srid=4326))
            session.add(stop)
            i+=1
            #if i % 100 == 0:
            #    session.commit()
        session.commit()
        print "pushing to postgis -- finished"

    def __updateStationTags(self):
        session = self.Session()
        for id in session.query(BusDelay.id).distinct():
            session.query(Station).filter(Station.id == id).update({'has_delaydata': True})
        session.commit()

    def __get_bus_stops(self):
        url = "https://api.tfl.lu/stations.geojson"
        data = requests.get(url).json()
        i = 0
        for feature in data["features"]:
            geom = Point(feature["geometry"]["coordinates"])
            name = feature["properties"]["name"]
            id = feature["properties"]["id"]
            bsd = BusStopDelay(id,name,geom)
            self.busStopArray[id] = (bsd)
            i += 1
            #if i > 1000:
            #    break

    def get_delays_dict(self):
        return self.busStopArray

    def compute_delays_sync(self):
        i = 0
        for stop in self.busStopArray:
            if i % 100 == 0:
                print i
            i += 1
            url = "https://api.tfl.lu/departures/%s" % stop
            info = self.busStopArray[stop]
            liveInfo = requests.get(url).json()
            for course in liveInfo:
                if course["delay"] > 0:
                    info.set_delay(course["line"],
                                   course["delay"])

    def compute_delays_async(self,shortlist=False):
        urls = []
        stops=[]
        array=[]
        if shortlist:
            session = self.Session()

            for rec in session.query(Station).filter(Station.has_delaydata == True) :
                array.append(rec.id)
        else:
            array = self.busStopArray
        for stop in array:
            stops.append(stop)
            urls.append("https://api.tfl.lu/departures/%s" % stop)
        size = 25
        future_session =  FuturesSession(executor=ThreadPoolExecutor(max_workers=size))
        responses = []
        for u in urls:
            r = future_session.get(u)
            responses.append(r)
        print "-- starting the querying for %s requests" % len(urls)
        print datetime.datetime.now()
        self.latestUpdateStartTime = datetime.datetime.now()

        print "requesting in parallel with size % s" % size
        #results = grequests.map(rs, size = size)
        results = []
        for resp in responses:
            results.append(resp.result())
        print datetime.datetime.now()
        print "-- finished the querying"

        ct = 0
        for result in results:
            if result:
                ct += 1
        print "got %s responses" % ct

        j = 0
        for result in results:
            id = stops[j]
            j += 1
            if not result or len(result.content) == 0:
                del self.busStopArray[id]
                continue
            live_info = result.json()
            k = 0
            for course in live_info:
                if int(course["delay"]) > 0:
                    self.busStopArray[id].set_delay(course["line"],
                                                    course["delay"],
                                                    course["number"],
                                                    course["departure"],
                                                    course["destination"])
                    k += 1
            if k == 0:
                del self.busStopArray[id]

    def write_to_postgis(self):
        session = self.Session()
        i = 0
        for id in self.busStopArray:
                f = self.busStopArray[id]
                for d in f.delays:
                    delay = BusDelay()
                    delay.id = f.id
                    delay.name = f.name
                    delay.line = d[0]
                    delay.delay = d[1]/60
                    delay.geom = from_shape(f.geom, srid=4326)
                    delay.time = self.latestUpdateStartTime
                    delay.number = d[2]
                    delay.departure = datetime.datetime.fromtimestamp(d[3])
                    delay.destination = d[4]
                    session.add(delay)
                i += 1
                if i % 500 == 0:
                    print "committing after %s" % i
                    session.commit()
        session.commit()


if __name__ == "__main__":
    dp = None

    _config_file = '../production.ini'
    if sys.argv[1]:
        config_file = sys.argv[1]
    # FULL DB UPDATE == TRUE?
    if sys.argv[2] == 'True':
        dp = DataPreparer(init=True, config_file=_config_file)
        dp.compute_delays_async(shortlist=False)
    # FULL DB UPDATE == FALSE
    else:
        dp = DataPreparer(init=False, config_file=_config_file)
        dp.compute_delays_async(shortlist=True)
    d = dp.get_delays_dict()
    c = 0
    for id in d:
                f = d[id]
                for delay in f.delays:
                    c+=1
    print c

    dp.write_to_postgis()
