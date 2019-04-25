import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape

class transform_landmark(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.get_landmarks']
    writes = ['soohyeok_soojee.transform_landmark']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        landmarkData = repo['soohyeok_soojee.get_landmarks'].find()
        if trial:
            landmarkData = repo['soohyeok_soojee.get_landmarks'].find().limit(700)

        # select town name and coordinates
        neighborhoods = {}
        LandmarkAndTown = {}
        for n in neighborhoodData:
            key = n['properties']['Name']
            neighborhoods[key] = n['geometry']
            LandmarkAndTown[key] = []

        coordinates = [shape(l['geometry']) for l in landmarkData]
        LandmarkLocations = [[point.centroid.x, point.centroid.y] for point in coordinates]

        for point in coordinates:
            for name in neighborhoods:
                if point.centroid.within(shape(neighborhoods[name])):
                    LandmarkAndTown[name] += [[point.centroid.x, point.centroid.y]]

        result = {'coordinates':LandmarkLocations, 'LandmarkAndTown': LandmarkAndTown}

        repo.dropCollection("transform_landmark")
        repo.createCollection("transform_landmark")
        repo['soohyeok_soojee.transform_landmark'].insert_many([result])
        repo['soohyeok_soojee.transform_landmark'].metadata({'complete':True})
        print(repo['soohyeok_soojee.transform_landmark'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#transform_landmark', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_landmark = doc.entity('dat:soohyeok_soojee#get_landmarks', {prov.model.PROV_LABEL:'get_landmarks', prov.model.PROV_TYPE:'ont:DataSet'})
        get_transform_landmark = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transform_landmark, this_script)
        doc.usage(get_transform_landmark, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_transform_landmark, resource_landmark, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        transform_landmark = doc.entity('dat:soohyeok_soojee#transform_landmark', {prov.model.PROV_LABEL:'transform_landmark', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(transform_landmark, this_script)
        doc.wasGeneratedBy(transform_landmark, get_transform_landmark, endTime)
        doc.wasDerivedFrom(transform_landmark, resource_neighborhoods, get_transform_landmark, get_transform_landmark, get_transform_landmark)
        doc.wasDerivedFrom(transform_landmark, resource_landmark, get_transform_landmark, get_transform_landmark, get_transform_landmark)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# transform_landmark.execute()
# doc = transform_landmark.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
