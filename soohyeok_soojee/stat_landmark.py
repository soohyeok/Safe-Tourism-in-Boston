import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape
import numpy as np

class stat_landmark(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.kmeans_landmark']
    writes = ['soohyeok_soojee.stat_landmark']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        Coordinates = repo['soohyeok_soojee.kmeans_landmark'].find()[0]['Coordinates']

        def average(x):
            return sum(x)/len(x)

        def distance(a,b):
            (x1,y1) = a
            (x2,y2) = b
            return ((x1-x2)**2 + (y1-y2)**2)**.5

        neighborhoods = {}
        for n in neighborhoodData:
            key = n['properties']['DISTRICT']
            neighborhoods[str(key)] = [shape(n['geometry']).centroid.x, shape(n['geometry']).centroid.y]

        avg = {}
        for name in Coordinates:
            center = neighborhoods[name]
            points = Coordinates[name]
            if Coordinates[name] != []:
                dist = [distance(center, p) for p in points]
                avg[name] = average(dist)

        result = [avg]

        repo.dropCollection("stat_landmark")
        repo.createCollection("stat_landmark")
        repo['soohyeok_soojee.stat_landmark'].insert_many(result)
        repo['soohyeok_soojee.stat_landmark'].metadata({'complete':True})
        print(repo['soohyeok_soojee.stat_landmark'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#stat_landmark', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_kmeans = doc.entity('dat:soohyeok_soojee#kmeans_landmark', {prov.model.PROV_LABEL:'kmeans_landmark', prov.model.PROV_TYPE:'ont:DataSet'})
        get_stat = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stat, this_script)
        doc.usage(get_stat, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_stat, resource_kmeans, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        stat = doc.entity('dat:soohyeok_soojee#stat_landmark', {prov.model.PROV_LABEL:'stat_landmark', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(stat, this_script)
        doc.wasGeneratedBy(stat, get_stat, endTime)
        doc.wasDerivedFrom(stat, resource_neighborhoods, get_stat, get_stat, get_stat)
        doc.wasDerivedFrom(stat, resource_kmeans, get_stat, get_stat, get_stat)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# stat_landmark.execute()
# doc = stat_landmark.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
