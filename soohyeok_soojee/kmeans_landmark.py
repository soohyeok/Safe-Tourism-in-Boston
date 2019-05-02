import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot

class kmeans_landmark(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.transform_landmark']
    writes = ['soohyeok_soojee.kmeans_landmark']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        LandmarkAndTown = repo['soohyeok_soojee.transform_landmark'].find()[0]['LandmarkAndTown']
        neighborhoods = {}
        for n in neighborhoodData:
            key = n['properties']['DISTRICT']
            neighborhoods[str(key)] = n['geometry']

        data = [point for name in LandmarkAndTown for point in LandmarkAndTown[name]]

        # kmean plot
        kmeans = KMeans(n_clusters=5).fit(data)
        data = np.array(data)
        # pyplot.scatter(data[:,0], data[:,1], c=kmeans.labels_)
        # pyplot.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], marker='x', c='red')
        # pyplot.show()

        centroid = [[x[0],x[1]] for x in kmeans.cluster_centers_]
        towns = [name for name in neighborhoods for point in centroid if Point(point).within(shape(neighborhoods[name]))]
        result = {'centroid': centroid, 'towns':towns, 'Coordinates': LandmarkAndTown}

        repo.dropCollection("kmeans_landmark")
        repo.createCollection("kmeans_landmark")
        repo['soohyeok_soojee.kmeans_landmark'].insert_many([result])
        repo['soohyeok_soojee.kmeans_landmark'].metadata({'complete':True})
        print(repo['soohyeok_soojee.kmeans_landmark'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#kmeans_landmark', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_landmark = doc.entity('dat:soohyeok_soojee#transform_landmark', {prov.model.PROV_LABEL:'transform_landmark', prov.model.PROV_TYPE:'ont:DataSet'})
        get_kmeans = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_kmeans, this_script)
        doc.usage(get_kmeans, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_kmeans, resource_landmark, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        kmeans = doc.entity('dat:soohyeok_soojee#kmeans_landmark', {prov.model.PROV_LABEL:'kmeans_landmark', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(kmeans, this_script)
        doc.wasGeneratedBy(kmeans, get_kmeans, endTime)
        doc.wasDerivedFrom(kmeans, resource_neighborhoods, get_kmeans, get_kmeans, get_kmeans)
        doc.wasDerivedFrom(kmeans, resource_landmark, get_kmeans, get_kmeans, get_kmeans)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# kmeans_landmark.execute()
# doc = kmeans_landmark.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
