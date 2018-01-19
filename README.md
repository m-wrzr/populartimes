# Populartimes
The goal of this library is to provide an option to use Google Maps popular times data, until it is available via Google's API.

## How to get started
+ Get a Google Maps API key https://developers.google.com/places/web-service/?hl=de (for more than 1000 requests/sec add payment information)
+ Install the wheel via: pip3 install populartimes-2.0-py3.whl
+ **Note**: The library is not available via PyPI, so you have to clone/download the repository and install the file locally.
+ *import populartimes* and run with *populartimes.get(...)* or *populartimes.get_id(...)*


## populartimes.get(...)
+ **populartimes.get**(api_key, types, bound_lower, bound_upper, n_threads (opt), radius (opt), all_places (opt))
    + **api_key** str; api key from google places web service; e.g. "your-api-key"
    + **types** [str]; placetypes; see https://developers.google.com/places/supported_types; e.g. ["bar"]
    + **p1** (float, float); lat/lng of point delimiting the search area; e.g. (48.132986, 11.566126)
    + **p2** (float, float); lat/lng of point delimiting the search area; e.g. (48.142199, 11.580047)
    + **n_threads (opt)** int; number of threads used; e.g. 20
    + **radius (opt)** int; meters; up to 50,000 for radar search; e.g. 180; this has can be adapted for very dense areas
    + **all_places (opt)** bool; include/exclude places without populartimes

+ **Example call**
    + populartimes.get("your-api-key", ["bar"], (48.132986, 11.566126), (48.142199, 11.580047))

+ **Response**
    + The data is represented as a list of dictionaries, with responses according to the example below
    + The populartimes data for each day is an array of length 24, with populartimes data starting from hour 0 to 23
    + *current_popularity*, *rating*, *rating_n* and *phone* are optional return parameters and only present if available.

```json
{
  "id": "ChIJ6cI52_EBCUER56PDz9hLEx0",
  "name": "Rockbox",
  "address": "Hochbrückenstraße 15, 80331 München, Germany",
  "rating": 3.7,
  "rating_n": 44,
  "searchterm": "Rockbox Hochbrückenstraße 15, 80331 München, Germany",
  "phone": "+49 176 64825227",
  "types": [
    "bar",
    "point_of_interest",
    "establishment"
  ],
  "coordinates": {
    "lat": 48.1362713,
    "lng": 11.5796438
  },
  "current_popularity": 12,
  "populartimes": [
        {
          "name": "Monday",
          "data": [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 7, 13, 21, 29, 37
          ]
        },
        {
          "name": "Tuesday",
          "data": [
            39, 37, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 15, 19, 13, 17
          ]
        },
        {
          "name": "Wednesday",
          "data": [
            33, 41, 37, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 15, 31, 45, 50
          ]
        },
        {
          "name": "Thursday",
          "data": [
            50, 47, 43, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 11, 13, 15, 21, 25
          ]
        },
        {
          "name": "Friday",
          "data": [
            29, 43, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 13, 19, 29, 52, 84
          ]
        },
        {
          "name": "Saturday",
          "data": [
            100, 84, 56, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 29, 66, 92, 88
          ]
        },
        {
          "name": "Sunday",
          "data": [
            74, 76, 74, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
          ]
        }
    ]
 }
 ```

 
## populartimes.get_id(...)
+ **populartimes.get_id**(api_key, place_id)
    + **api_key** str; api key from google places web service; e.g. "your-api-key"
    + **place_id** str; unique google maps id; retrievable via populartimes.get() or https://developers.google.com/maps/documentation/javascript/examples/places-placeid-finder
 
+ **Example call**
    + populartimes.get_id("your-api-key", "ChIJ01CaE2PfnUcRUpb8Ylg-UXo")
 
+ **Response**
    + The response format is equal to the json described above, with the exception of the search term parameter, which is not present.
    + The data is represented as a dictionary containing information
    + *current_popularity*, *rating*, *rating_n* and *phone* are optional return parameters and only present if available.

```

 ## Example how the data can be used for visualization
 ![Bars-Gif](/content/bars_visualization.gif "Bars Munich,Berlin,Barcelona, London")
