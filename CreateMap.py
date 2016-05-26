import folium
import json

from pymongo import MongoClient

params = json.loads(open("params.json", "r").read())

client = MongoClient('localhost', params["dbPort"])
database = client[params["dbName"]]
locations = database[params["collectionName"]]

maps = {}

# init with empty maps "day_time"
for x, y in [(day, currT) for day in range(7) for currT in range(24)]:
    maps["{}_{}".format(x, y)] = folium.Map(location=[48.131776, 11.576037],
                                            tiles='Stamen Toner',
                                            zoom_start=14)

for location in locations.find({"popular_times": {"$exists": True}}):

    loc = location["location"]["location"]
    lat = loc["lat"]
    lng = loc["lng"]
    name = location["name"]

    for time in location["popular_times"]:
        for day in time["data"]:
            maps["{}_{}".format(time["weekday_num"], day["time"])] \
                .circle_marker(location=[lat, lng], radius=day["popularity"],
                               popup=name, line_color='#3186cc',
                               fill_color='#3186cc')

for m in maps.keys():
    maps[m].create_map(path="maps/{}.html".format(m))
