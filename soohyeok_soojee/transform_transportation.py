import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape

class transform_transportation(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.get_busStops', 'soohyeok_soojee.get_trainStations']
    writes = ['soohyeok_soojee.transform_transportation']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        trainStationsData = repo['soohyeok_soojee.get_trainStations'].find()
        busStopsData = repo['soohyeok_soojee.get_busStops'].find()
        if trial:
            trainStationsData = repo['soohyeok_soojee.get_trainStations'].find().limit(50)
            busStopsData = repo['soohyeok_soojee.get_busStops'].find().limit(800)

        # select town name and coordinates
        neighborhoods = {}
        TransportationAndTown = {}
        for n in neighborhoodData:
            key = n['properties']['Name']
            neighborhoods[key] = n['geometry']
            TransportationAndTown[key] = []

        train = [shape(t['geometry']) for t in trainStationsData]
        bus = [shape(b['geometry']) for b in busStopsData]
        transportation = train + bus
        TransportationLocations = [[point.x,point.y] for point in transportation]
        for point in transportation:
            for name in neighborhoods:
                if point.within(shape(neighborhoods[name])):
                    TransportationAndTown[name] += [[point.x,point.y]]

        result = {'coordinates': TransportationLocations, 'TransportationAndTown': TransportationAndTown}

        repo.dropCollection("transform_transportation")
        repo.createCollection("transform_transportation")
        repo['soohyeok_soojee.transform_transportation'].insert_many([result])
        repo['soohyeok_soojee.transform_transportation'].metadata({'complete':True})
        print(repo['soohyeok_soojee.transform_transportation'].metadata())

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:soohyeok_soojee#transform_transportation', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_train = doc.entity('dat:soohyeok_soojee#get_trainStations', {prov.model.PROV_LABEL:'get_trainStations', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_bus = doc.entity('dat:soohyeok_soojee#get_busStops', {prov.model.PROV_LABEL:'get_busStops', prov.model.PROV_TYPE:'ont:DataSet'})

        get_transform_transportation = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transform_transportation, this_script)
        doc.usage(get_transform_transportation, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_transform_transportation, resource_train, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_transform_transportation, resource_bus, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        transform_transportation = doc.entity('dat:soohyeok_soojee#transform_transportation', {prov.model.PROV_LABEL:'transform_transportation', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(transform_transportation, this_script)
        doc.wasGeneratedBy(transform_transportation, get_transform_transportation, endTime)
        doc.wasDerivedFrom(transform_transportation, resource_neighborhoods, get_transform_transportation, get_transform_transportation, get_transform_transportation)
        doc.wasDerivedFrom(transform_transportation, resource_train, get_transform_transportation, get_transform_transportation, get_transform_transportation)
        doc.wasDerivedFrom(transform_transportation, resource_bus, get_transform_transportation, get_transform_transportation, get_transform_transportation)
        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# transform_transportation.execute()
# doc = transform_transportation.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
