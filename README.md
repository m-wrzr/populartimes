# populartimes
exploring google maps popular times data
## Requirements for RequestPlaces
+ Google Chrome WebDriver for Selenium
    https://sites.google.com/a/chromium.org/chromedriver/getting-started
+ Google Maps API key https://developers.google.com/places/web-service/?hl=de
+ MongoDB https://www.mongodb.com/
+ Add params.json

         {
                    "API_key" : "yourKey",
                    "bounds" : [
                            {"lat" : 48.123,"lng" : 10.123},
                            #bigger than previous
                            {"lat" : 48.456,"lng" : 10.456}
                                ],
                    #between 1 and 500
                    "radius" : 180,
                    #https://developers.google.com/places/supported_types
                    "types" : ["bar", "restaurant"], 
                    "dbPort" : yourMongoPort,
                    "dbName" : yourDbName,
                    "collectionName" : yourCollectionName
        }

+ Examples for created maps
![Saturday-20](/content/5-20.png?raw=true "Saturday 20:00")
![Saturday-21](/content/5-21.png?raw=true "Saturday 21:00")
![Saturday-22](/content/5-22.png?raw=true "Saturday 22:00")
