import folium
from os import walk
import json

# TODO multiple maps at the beginning not possible, change iteration to map

for i in range(24):
    mymap = folium.Map(location=[48.131776, 11.576037], tiles='Stamen Toner', zoom_start=15)

    for (dirpath, dirnames, filenames) in walk("data"):
        for filename in filenames:
            if ".DS" not in filename:
                with open(dirpath + "/" + filename) as file:

                    place = json.loads(file.read().replace('\n', ''))
                    loc = place["location"]["location"]
                    lat = loc["lat"]
                    lng = loc["lng"]
                    name = place["name"]

                    for time in place["popular_times"]:
                        if time["weekday"] == "Friday":
                            for d in time["data"]:
                                if d["time"] == i:
                                    mymap.circle_marker(location=[lat, lng], radius=d["popularity"],
                                                        popup=name, line_color='#3186cc',
                                                        fill_color='#3186cc')

    mymap.create_map(path="maps/{}.html".format(i))
