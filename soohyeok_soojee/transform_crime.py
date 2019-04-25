import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape

class transform_crime(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.get_crimeData']
    writes = ['soohyeok_soojee.transform_crime']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        crimeData = repo['soohyeok_soojee.get_crimeData'].find().limit(2000)
        if trial:
            crimeData = repo['soohyeok_soojee.get_crimeData'].find().limit(150)

        # select town name and coordinates
        neighborhoods = {}
        CrimeAndTown = {}
        for n in neighborhoodData:
            key = n['properties']['Name']
            neighborhoods[key] = n['geometry']
            CrimeAndTown[key] = []

        CrimeLocations = []
        for c in crimeData:
            location = c['Location'][1:-1]
            if location != '0.00000000, 0.00000000':
                location2 = tuple(map(float, location.split(',')))
                CrimeLocations.append([location2[1], location2[0]])

        # group crime data by town
        for point in CrimeLocations:
            for name in neighborhoods:
                if Point(point).within(shape(neighborhoods[name])):
                    CrimeAndTown[name] += [point]


        result = {'coordinates': CrimeLocations, 'CrimeAndTown': CrimeAndTown}

        repo.dropCollection("transform_crime")
        repo.createCollection("transform_crime")
        repo['soohyeok_soojee.transform_crime'].insert_many([result])
        repo['soohyeok_soojee.transform_crime'].metadata({'complete':True})
        print(repo['soohyeok_soojee.transform_crime'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#transform_crime', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_crime = doc.entity('dat:soohyeok_soojee#get_crimeData', {prov.model.PROV_LABEL:'get_crimeData', prov.model.PROV_TYPE:'ont:DataSet'})
        get_transform_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transform_crime, this_script)
        doc.usage(get_transform_crime, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_transform_crime, resource_crime, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        transform_crime = doc.entity('dat:soohyeok_soojee#transform_crime', {prov.model.PROV_LABEL:'transform_crime', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(transform_crime, this_script)
        doc.wasGeneratedBy(transform_crime, get_transform_crime, endTime)
        doc.wasDerivedFrom(transform_crime, resource_neighborhoods, get_transform_crime, get_transform_crime, get_transform_crime)
        doc.wasDerivedFrom(transform_crime, resource_crime, get_transform_crime, get_transform_crime, get_transform_crime)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# transform_crime.execute()
# doc = transform_crime.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
