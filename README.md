# Populartimes - Version 2
The goal of this update is to remove dependencies and make everything faster.

## Setup
+ Get a Google Maps API key https://developers.google.com/places/web-service/?hl=de (for more than 1000 reqests/sec add payment information)
+ Update params.json and add you API key, change search parameters and remove comments
+ Run "python3 main.py"

## Return
+ Data for each place is written to a file in the data folder, with the google place id as filename
+ Example for a place.json
```json
{
  "id": "ChIJ6cI52_EBCUER56PDz9hLEx0",
  "name": "Rockbox",
  "address": "Hochbrückenstraße 15, 80331 München, Germany",
  "rating": 3.7,
  "rating_n": 44,
  "searchterm": "Rockbox Hochbrückenstraße 15, 80331 München, Germany",
  "types": [
    "bar",
    "point_of_interest",
    "establishment"
  ],
  "coordinates": {
    "lat": 48.1362713,
    "lng": 11.5796438
  },
  "populartimes": [
    {
      "name": "monday",
      "data": [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        3,
        7,
        13,
        21,
        29,
        37
      ]
    },
    {
      "name": "tuesday",
      "data": [
        39,
        37,
        29,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        5,
        15,
        19,
        13,
        17
      ]
    },
    ...,
    {
      "name": "friday",
      "data": [
        29,
        43,
        66,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        5,
        13,
        19,
        29,
        52,
        84
      ]
    },
    {
      "name": "saturday",
      "data": [
        100,
        84,
        56,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        7,
        29,
        66,
        92,
        88
      ]
    },
    {
      "name": "sunday",
      "data": [
        74,
        76,
        74,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0
      ]
    }
  ]
}
```