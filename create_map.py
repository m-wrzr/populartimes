import folium
import json
import threading

from pymongo import MongoClient


# adds marker to corresponding map, executed as thread
def add_marker(_lat, _lng, _name, _time, _day):
    maps["{}_{}".format(_time["weekday_num"], _day["time"] % 24)] \
        .circle_marker(location=[_lat, _lng], radius=day["popularity"],
                       popup=_name, line_color='#3186cc',
                       fill_color='#3186cc')


params = json.loads(open("params.json", "r").read())

client = MongoClient('localhost', params["dbPort"])
mongod = client[params["dbName"]]
places = mongod[params["collectionName"]]

maps = {}

# init with empty maps "day_time"
for x, y in [(day, currT) for day in range(7) for currT in range(24)]:
    maps["{}_{}".format(x, y)] = folium.Map(location=[52.509719, 13.393527],
                                            tiles='Stamen Toner',
                                            zoom_start=14)

curr_thread = None

# iterate over mongodb data with populartimes
for i, location in enumerate(places.find({"popular_times": {"$exists": True}})):

    print("--- place #{} ---".format(i))

    loc = location["location"]["location"]
    lat = loc["lat"]
    lng = loc["lng"]
    name = location["name"]

    for time in location["popular_times"]:
        for day in time["data"]:
            curr_thread = threading.Thread(target=add_marker(lat, lng, name, time, day))
            curr_thread.start()

curr_thread.join()

for map_key in maps.keys():
    maps[map_key].create_map(path="maps/{}.html".format(m))
    print("--- created map {} ---".format(m))
