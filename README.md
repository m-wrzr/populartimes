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
'id': 'ChIJFQtcfMTYnUcRMyPtgtKWFIY',
  'name': 'Wöllinger Wirtshaus',
  'address': 'Johann-Clanze-Straße 112, 81369 München, Germany',
  'rating': 4.1,
  'rating_n': 138,
  'searchterm': 'Wöllinger Wirtshaus Johann-Clanze-Straße 112, 81369 München, Germany',
  'types': [
    'cafe',
    'bar',
    'restaurant',
    'food',
    'point_of_interest',
    'establishment'
  ],
  'coordinates': {
    'lat': 48.11301,
    'lng': 11.51993
  },
  'populartimes': {
    'Monday': [
      10,
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
      23,
      29,
      33,
      33,
      32,
      36,
      48,
      70,
      91,
      99,
      86,
      61,
      34
    ],
    'Tuesday': [
      15,
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
      15,
      19,
      22,
      25,
      28,
      32,
      41,
      56,
      68,
      69,
      55,
      34,
      17
    ],
    'Wednesday': [
      7,
      0,
      0,
      0,
      ...
  }
```