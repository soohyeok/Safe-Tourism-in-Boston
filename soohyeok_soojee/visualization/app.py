from flask import Flask, jsonify, abort, make_response, request, render_template
import pymongo

app = Flask(__name__)
client = pymongo.MongoClient()
repo = client.repo
repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

landmarkDict = repo['soohyeok_soojee.transform_landmark'].find()[0]['LandmarkAndTown']
transDict = repo['soohyeok_soojee.transform_transportation'].find()[0]['TransportationAndTown']
crimeDict = repo['soohyeok_soojee.transform_crime'].find()[0]['CrimeAndTown']
landmarks = [[int(key), len(value)] for key, value in landmarkDict.items()]
transportations = [[int(key), len(value)] for key, value in transDict.items()]
crimes = [[int(key), len(value)] for key, value in crimeDict.items()]

@app.route('/', methods=['GET'])
def home():
    return render_template('map.html', landmarks=landmarks, transportations=transportations, crimes=crimes)

@app.route('/optimal', methods=['GET', 'POST'])
def optimal():
    kmeans_land_crime = repo['soohyeok_soojee.kmeans_landmark_crime'].find()[0]['centroid']
    kmeans_land_trans_crime = repo['soohyeok_soojee.kmeans_landmark_transportation_crime'].find()[0]['centroid']
    kmeans_land_trans = repo['soohyeok_soojee.kmeans_landmark_transportation'].find()[0]['centroid']
    kmeans_landmark = repo['soohyeok_soojee.kmeans_landmark'].find()[0]['centroid']
    if request.method == 'POST':
        land = request.form.get("land")
        trans = request.form.get("trans")
        crime = request.form.get("crime")
        kmeans = kmeans_landmark
        msg = ""
        if land and trans:
            kmeans = kmeans_land_trans
        elif land and crime:
            kmeans = kmeans_land_crime
        elif land and trans and crime:
            kmeans = kmeans_land_trans_crime
        elif (not land) and (trans or crime):
            msg = "Try Again!"
            kmeans=[]
        return render_template('optimal.html', landmarks=landmarks, transportations=transportations, crimes=crimes, kmeans=kmeans, msg=msg)
    return render_template('optimal.html', landmarks=landmarks, transportations=transportations, crimes=crimes)

if __name__ == '__main__':
    app.run(debug=True)
