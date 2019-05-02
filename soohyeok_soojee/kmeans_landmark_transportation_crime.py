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

class kmeans_landmark_transportation_crime(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.transform_transportation', 'soohyeok_soojee.transform_landmark', 'soohyeok_soojee.transform_crime']
    writes = ['soohyeok_soojee.kmeans_landmark_transportation_crime']

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
        TransportationAndTown = repo['soohyeok_soojee.transform_transportation'].find()[0]['TransportationAndTown']
        CrimeAndTown = repo['soohyeok_soojee.transform_crime'].find()[0]['CrimeAndTown']

        neighborhoods = {}
        merge = {}
        for n in neighborhoodData:
            key = n['properties']['DISTRICT']
            neighborhoods[str(key)] = n['geometry']
            merge[str(key)] = []

        for name in neighborhoods:
            merge[name] = LandmarkAndTown[name] + TransportationAndTown[name]

        def distance(a,b):
            (x1,y1) = a
            (x2,y2) = b
            return ((x1-x2)**2 + (y1-y2)**2)**.5

        for name in CrimeAndTown:
            for point in CrimeAndTown[name]:
                dist = [[distance(point,x)] for x in merge[name]]
                if dist != []:
                    index = np.argmin(dist)
                    p = merge[name][index]
                    merge[name].remove(p)

        data = [point for name in merge for point in merge[name]]

        kmeans = KMeans(n_clusters=5).fit(data)
        data = np.array(data)
        # pyplot.scatter(data[:,0], data[:,1], c=kmeans.labels_)
        # pyplot.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], marker='x', c='red')
        # pyplot.show()

        centroid = [[x[0],x[1]] for x in kmeans.cluster_centers_]
        towns = [name for name in neighborhoods for point in centroid if Point(point).within(shape(neighborhoods[name]))]
        result = {'centroid': centroid, 'towns':towns, 'Coordinates':merge}

        repo.dropCollection("kmeans_landmark_transportation_crime")
        repo.createCollection("kmeans_landmark_transportation_crime")
        repo['soohyeok_soojee.kmeans_landmark_transportation_crime'].insert_many([result])
        repo['soohyeok_soojee.kmeans_landmark_transportation_crime'].metadata({'complete':True})
        print(repo['soohyeok_soojee.kmeans_landmark_transportation_crime'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#kmeans_landmark_transportation_crime', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_landmark = doc.entity('dat:soohyeok_soojee#transform_landmark', {prov.model.PROV_LABEL:'transform_landmark', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_transportation = doc.entity('dat:soohyeok_soojee#transform_transportation', {prov.model.PROV_LABEL:'transform_transportation', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_crime = doc.entity('dat:soohyeok_soojee#transform_crime', {prov.model.PROV_LABEL:'transform_crime', prov.model.PROV_TYPE:'ont:DataSet'})
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
        doc.usage(get_kmeans, resource_transportation, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_kmeans, resource_crime, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        kmeans = doc.entity('dat:soohyeok_soojee#kmeans_landmark_transportation_crime', {prov.model.PROV_LABEL:'crimeRate', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(kmeans, this_script)
        doc.wasGeneratedBy(kmeans, get_kmeans, endTime)
        doc.wasDerivedFrom(kmeans, resource_neighborhoods, get_kmeans, get_kmeans, get_kmeans)
        doc.wasDerivedFrom(kmeans, resource_landmark, get_kmeans, get_kmeans, get_kmeans)
        doc.wasDerivedFrom(kmeans, resource_transportation, get_kmeans, get_kmeans, get_kmeans)
        doc.wasDerivedFrom(kmeans, resource_crime, get_kmeans, get_kmeans, get_kmeans)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# kmeans_landmark_transportation_crime.execute()
# doc = kmeans_landmark_transportation_crime.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
