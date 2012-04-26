Backbone Stats
=============
Trying out Backbone & some Redis tricks.

Requirements
========
- redis (2.4.4)
- python (2.7)
    - Modules:
        - Tornado
        - Redis
        - bitarray

Usage
=====
This app generates stats in Redis using Sorted Sets to create Top lists and bitfields to count unique users and rides. It uses tornado to serve data to a Backbone front end. It serves no purpose except as a tech demo.

Installation
=====
1. Check out git repo.
2. pip install -r requirements.txt
3. Start redis
4. python app.py
5. Go to localhost:8080/randomize
6. Enter the number of drivers, passengers, and rides you want to generate (Max 200 each of drivers and passengers)
7. Press Generate. Wait.
8. Play with stats.

Notes
=====
This is mostly a tech demo. There's a number of things that are incomplete or unsupported on the front-end. Were this to be an actual app, it would implement ranges, proper date detection, and a raft more stats & graph options.