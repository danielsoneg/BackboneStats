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
# Check out git repo.
# pip install -r requirements.txt
# Start redis
# python app.py
# Go to localhost:8080/randomize
# Enter the number of drivers, passengers, and rides you want to generate (Max 200 each of drivers and passengers)
# Press Generate. Wait.
# Play with stats.

Notes
=====
This is mostly a tech demo. There's a number of things that are incomplete or unsupported on the front-end. Were this to be an actual app, it would implement ranges, proper date detection, and a raft more stats & graph options.