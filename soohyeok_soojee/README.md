# CS504 Project#2: Proper Boston Tour
## Contributors:
- Soojee Kim
- Soohyeok Lee


### Project Goal:
Our goal is to determine best travel experiences for incoming tourists within Greater Boston Area. Having such an immense area, people may not have their best experiences in their limited time of travel and we wanted to suggest specific areas based on various datasets for the best possible experience.

### Data sources Used:
- Analyze Boston (*data.boston.gov*)
- Boston Maps Open Data (*bostonopendata-boston.opendata.arcgis.com*)
- Massachusetts Department of Transportation (*geo-massdot.opendata.arcgis.com*)

### Datasets Used:
1. Boston Neighborhoods (*get_neighborhoods.py*)
https://data.boston.gov/dataset/boston-neighborhoods
2. Crime rate (*get_crimeData.py*)  
https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system
3. Boston Landmarks Commission (BLC) Historic Districts (*get_landmarks.py*)   
http://bostonopendata-boston.opendata.arcgis.com/datasets/547a3ccb7ab443ceaaba62eef6694e74_4
4. MBTA Bus Stops (*get_busStops.py*)  
https://geo-massdot.opendata.arcgis.com/datasets/2c00111621954fa08ff44283364bba70_0
5. MBTA Station stops (*get_trainStations.py*)  
https://geo-massdot.opendata.arcgis.com/datasets/train-stations?geometry=-73.51%2C41.878%2C-69.555%2C42.59

### Project Description:
We currently put together the few datasets listed above and transformed the acquired datasets to see which neighborhoods within the Greater Boston Area  
- has greater number of landmarks to see
- has better system of public transportation
- has low crime rates.

Although we have different datasets of polygons and points, our current project model is heavily dependent on geolocation datsets. We are currently researching on possible datasets to incorporate into our project to further develop user experience.
#### (*Project#2 justification*)
We needed a way to rate the neighborhoods somehow based on the coordinate datas we have collected. The problem is that we have each neighborhood's landmark coordinates, public tranportation coordiantes and crime coordiantes (where crime occured) but we do not have a way to compare a neighborhood to another neighborhood.

### Transformation:  
#### *transform_landmark.py* (file name-changed and updated from *landmarkRate.py*):
- Pulls dataset of polygons from *get_neighborhoods.py*
- Pulls dataset of polygons from *get_landmarks.py*
- Polygon datset of landmarks is averaged into points
- Now that we have points, checks and counts where the crime points are marked within the neighborhood polygons.

#### *transform_crime.py* (file name-changed and updated from *crimeRate.py*):
- Pulls dataset of polygons from *get_neighborhoods.py*
- Pulls dataset of points from *get_crimeData.py*
- Checks and counts where the crime occurred within which polygons of neighborhoods.

#### *transform_transportation.py* (file name-changed and updated from *transportation.py*):
- Pulls dataset of polygons from *get_neighborhoods.py*
- Pulls dataset of points from *get_trainStations.py*
- Pulls dataset of points from *get_busStops.py*
- Merges two dataset of points of bus and train
- Checks and counts where the bus stops and trainstations are within which polygons of neighborhoods.

### non-trivial constraint satisfaction or optimization technique:
- There are different variation for the k-means for the different visualization we are preparing for project#3
#### *k-means_landmark.py*:
- K-means algorithm for finding clusters of landmarks
- locates K coordinates that are centers of the found clusters 
#### *k-means_landmark_crime.py*:
- K-means algorithm for finding clusters of landmarks
- landmark coordinates close to crime coordinates are removed
- locates K coordinates that are centers of the found clusters
#### *k-means_landmark_transportation.py*:
- K-means algorithm for finding clusters of landmarks and transporations (bus & train)
- locates K coordinates that are centers of the found clusters 
#### *k-means_landmark_transportation_crime.py*:
- K-means algorithm for finding clusters of landmarks and trasnportations (bus & train) where
- landmark or transporation coordinates close to crime coordinates are removed 
- locates K coordinates that are centers of the found clusters 

### statistical analysis or inference algorithm:
- There are different variation for the stats alg for the different visualization we are preparing for project#3
#### *stat_landmark.py*:
- finds the averaging center point of landmarks based on each neighborhood's landmark coordinates
- then finds the average distance to each landmark to the found coordinate
#### *stat_landmark_crime.py*:
- landmark coordinates near crime coordinates are removed
- finds the averaging center point of landmarks based on each neighborhood's landmark coordinates
- then finds the average distance to each landmark to the found coordinate
#### *stat_landmark_transportation.py*:
- finds the averaging center point of landmarks and transportations based on each neighborhood's landmark coordinates and transportation coordinates
- then finds the average distance to each landmarks and transporations to the found coordinates
#### *stat_landmark_transportation_crime.py*:
- landmark coordinates near crime coordinates are removed
- finds the averaging center point of landmarks and transportations based on each neighborhood's landmark coordinates and transportation coordinates
- then finds the average distance to each landmarks and transporations to the found coordinates

### Execution Script for Provenance.html:
To execute all the algorithms for the project in an order that respects their explicitly specified data flow dependencies, run the following from the root directory:
```
python execute.py soohyeok_soojee
```

### Note:
If you have any suggestions to improve tourist experience or possible dataset to incorporate onto our project please leave a comment on github or send any of us an e-mail
- soohyeok@bu.edu
- soojee@bu.edu
