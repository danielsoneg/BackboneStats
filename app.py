#!/usr/bin/env python
#! encoding: utf-8
# System Modules
import sys
import os
import codecs
import logging
from datetime import date
# Tornado Modules
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
from tornado.options import define, options
# Our modules
import importer
import ridestats

define("port", default=8080, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    """Contains common methods for all Stat calls."""
    def initialize(self):
        """Initializes the handler. Fired before requests are processed. Sets a date object & a redis connection"""
        self.Stats = ridestats.Stats()
        # Date object for easier calls.
        today = date.today()
        self.date = {'now':today.isoformat()}
        self.date['week'] = today.strftime('%Y-w%W')
        self.date['month'] = today.strftime('%Y-%m')
        self.date['year'] = today.year

    def on_finish(self):
        """Clean up Redis connection"""
        self.Stats.close()
    
    def getTitle(self, who,what,when,fordate="today"):
        """ Cheap #hack to generate a title to hand to Backbone. """
        if fordate == 'today': fordate = date.today().isoformat()
        who = {'psng':"Passengers",'drvr':"Drivers",'rides':"Rides"}[who]
        what = {'top':"Top",'count':"Total"}[what]
        whenm = {'now':"the Day",'week':"the week",'month':"the month",'year':"the year"}
        when = "%s of %s" % (whenm[when], fordate)
        name = "%s %s for %s" % (what,who,when)
        return name

    def parseDate(self, when, fordate):
        # Convenience method for now
        rideiso = date.today().isoformat() if fordate == 'today' or fordate == 'undefined' else fordate
        ridedate = date(*[int(x) for x in rideiso.split('-')])
        rd = {}
        rd['today'] = ridedate.isoformat()
        rd['week'] = ridedate.strftime('%Y-w%W')
        rd['month'] = ridedate.strftime('%Y-%m')
        rd['year'] = ridedate.year
        if when in rd:
            return rd[when]
        else:
            return rd['today']

    # Default methods: Fail nicely
    def post(self, **kwargs):
        """Stand-in method. Overwrite this."""
        self.fail('invalid method')
    
    def get(self, **kwargs):
        """Stand-in method. Overwrite this."""
        self.fail('invalid method')
    
    def put(self, **kwargs):
        """Stand-in method. Overwrite this."""
        self.fail('invalid method')
    
    # Format responses
    def fail(self, error='error', data = False):
        """Returns an Error status message, passed error text, and data if given"""
        msg = {'status':'error', 'error':error}
        if data: msg['data'] = data
        self.write(msg)
    
    def success(self, data=False):
        """Returns a Success status message and passed data"""
        msg = {'status':'success'}
        if data: msg['data']=data
        self.write(msg)

    def stat(self, who, what, when, fordate, data):
        """Return a Stat model object for Backbone"""
        params = {'who':who,'what':what,'when':when,'fordate':fordate}
        title = self.getTitle(who,what,when,fordate)
        self.write({'title':title,'data':data,'params':params})

class getUserStats(BaseHandler):
    """getUserStats handles requests for information about Drivers and Pasengers"""
    def get(self,who,what,when,fordate=None,count=10):
        """Routes get requests to the appropriate method, formats & returns response"""
        given_when = when
        fordate = fordate or date.today().isoformat()
        when = self.parseDate(given_when,fordate)
        if what == "count":
            data = self.__getCounts(who,when)
        elif what == "top":
            data = self.__getTop(who,when,count)
        else:
            data = None
        self.stat(who, what, given_when, fordate, data)
    
    def post(self, who, what, when, fordate=None, count=10):
        fordate = fordate or date.today().isoformat()
        """Backbone Gets and Posts. We give identical responses to both."""
        return self.get(who, what, when, fordate, count)

    def __getCounts(self, who, when):
        """Requests counts for passengers or drivers from Stats database"""
        count = self.Stats.getUserCounts(who, when)
        return count
    
    def __getTop(self, who, when, count):
        """Requests top passenger or driver lists from the Stats database"""
        toplist = self.Stats.getTopUsers(who,when,count)
        return toplist

class getRideStats(BaseHandler):
    """getUserStats handles requests for information about Rides. Distinct because different methods are used
    on the back end, interface may change."""
    def get(self,what,when,fordate,count=10):
        """Route requests to the appropriate handler"""
        given_when = when
        when = self.parseDate(when,fordate)
        if what == "count":
            data = self.__getCounts(when)
        elif what == "top":
            data = self.__getTop(when, count)
        else:
            data = None
        self.stat('rides', what, given_when,fordate, data)

    def post(self, what, when, fordate, count=10): 
        """Backbone Gets and Posts. We give identical responses to both."""
        return self.get(what, when, fordate, count)
    
    def __getCounts(self, when):
        """Get number of miles riden"""
        count = self.Stats.getMileCounts(when)
        return count
        
    def __getTop(self, when, count):
        """Get longest rides"""
        toplist = self.Stats.getTopRides(when,count)
        return toplist
    
class importStuff(BaseHandler):
    """ImportStuff fronts the importer API and handles posts to /importer/(rides|user)"""
    def initialize(self):
        super(importStuff, self).initialize()
        self.importer = importer.RideImporter()
    
    def post(self,t):
        """Route a post to the right import method"""
        if t == 'user':
            return self.__addUser()
        elif t == 'ride':
            return self.__addRide()
        else:
            self.fail("Bad Import")
    
    def __addUser(self):
        """Imports a user. Username is the only info currently supported.
        Post fields are: 
            t=psng|drvr
            name=username."""
        if not self.get_argument('name',False) or not self.get_argument('t',False):
            self.fail("No name or type given!")
            return False
        else:
            name,t = self.get_argument('name'), self.get_argument('t')
            if self.importer.addUser(t,{'name':name}):
                self.success("Added user %s" % name)
                return True
            else:
                self.fail("Failed to add user %s" % name)
                return False
        
    def __addRide(self):
        """Import a ride.
        Post fields are: 
        psng=(Passenger ID) 
        drvr=(Driver ID) 
        miles=(Miles of Trip) 
        date=(ISO-format date - optional)"""
        if not min([self.get_argument(x,False) for x in ['psng','drvr','miles']]):
            self.fail("insufficient information given")
            return False
        else:
            self.importer.addRide(date = self.get_argument('date',self.date['now']),
             psng = self.get_argument('psng'),
             drvr = self.get_argument('drvr'),
             miles = self.get_argument('miles')
            )
            self.success('Added Ride.')
            return True

class Index(BaseHandler):
    """Hand off index.html if we have data, randomize if we don't"""
    def get(self):
        if self.Stats.hasStats() == False:
            self.redirect('/randomize')
            return
        self.render('templates/index.html')

class Randomizer(tornado.web.RequestHandler):
    """Randomizer allows us to populate the database with random data."""
    def get(self):
        """Serve html to /randomize""" 
        self.render('templates/randomize.html')

    def post(self):
        """Creates a Randomizer object, clears the old DB info, adds info as posted.
        Post fields are:
            psng=(int: Number of passengers to create)
            drvr=(int: Number of drivers to create)
            rides=(int: Number of rides to create)"""
        if False in [self.get_argument(x,False) for x in ['psng','drvr','rides']]:
            self.write("Need all vars")
            return
        try:
            psng = int(self.get_argument('psng'))
            drvr = int(self.get_argument('drvr'))
            rides = int(self.get_argument('rides'))
        except ValueError:
            self.write("Invalid values!")
            return
        self.randomizer = importer.Randomizer()
        self.randomizer.clearTables()
        self.randomizer.Randomize(psng,drvr,rides)
        self.write("<h1>Randomized!</h1>")
        self.redirect('/')

def run():
    sys.stdout = codecs.lookup('utf-8')[-1](sys.stdout) # Unicode
    sys.stderr = codecs.lookup('utf-8')[-1](sys.stderr) # Unicode
    # Standard Tornado Stuff
    tornado.options.parse_command_line()
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "debug": "true",
    }
    # Here there be regex
    application = tornado.web.Application([
        (r"/", Index),
        (r"/Stats/(?P<who>psng|drvr)/(?P<what>.*?)/(?P<when>.*?)/(?P<fordate>.*?)",getUserStats),
        (r"/Stats/rides/(?P<what>.*?)/(?P<when>.*?)/(?P<fordate>.*?)",getRideStats),
        (r'/importer/(?P<who>user|ride)',importStuff),
        (r'/randomize',Randomizer)
        ],**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()

