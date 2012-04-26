import redis
import bitarray
import logging
import random
from datetime import date

class RideImporter(object):
    """RideImporter handles importing data into Redis"""
    def __init__(self,db=1):
        super(RideImporter, self).__init__()
        self.pool = redis.ConnectionPool(host='localhost',db=1)
        self.redis = redis.Redis(connection_pool=self.pool)
    
    def addUser(self,t,info):
        """Add a user to Redis. t: type of the user, either psng or drvr."""
        uid = self.redis.get('%s:nextid' % t) or 1
        if self.redis.hmset('%s:%s'%(t,uid),info):
            self.redis.incr('%s:nextid' % t)
            return True
        return False
    
    def addRide(self,psng,drvr,miles,ridedate=None):
        """Add a ride to Redis. psng: Passenger ID, drvr: Driver ID, miles: length of ride, Date: Date, defaults to today."""
        rideiso = ridedate or date.today().isoformat()
        ridedate = date(*[int(x) for x in rideiso.split('-')])
        week = ridedate.strftime('%Y-w%W')
        month = ridedate.strftime('%Y-%m')
        year = ridedate.year
        #Ease of string formatting
        ride = {'psng':psng,'drvr':drvr,'miles':miles,'date':rideiso,'week':week,'month':month,'year':year}
        #Increment ride stats:
        self.addRideStats('psng',psng,ride)
        self.addRideStats('drvr',drvr,ride)
        self.addRideMiles(ride)
        
    def addRideStats(self,t,uid,ride):
        """Imports stats for users (either drivers or passengers): mark user as active 
        and increment their mile counts in the top lists"""
        ride['type'] = t
        self.redis.setbit('count:%(type)s:%(date)s' % ride,uid,1)
        self.redis.setbit('count:%(type)s:%(week)s' % ride,uid,1)
        self.redis.setbit('count:%(type)s:%(month)s' % ride,uid,1)
        self.redis.setbit('count:%(type)s:%(year)s' % ride,uid,1)
        # Update mile counts
        self.redis.zincrby('miles:%(type)s:%(date)s' % ride,uid,ride['miles'])
        self.redis.zincrby('miles:%(type)s:%(week)s' % ride,uid,ride['miles'])
        self.redis.zincrby('miles:%(type)s:%(month)s' % ride,uid,ride['miles'])
        self.redis.zincrby('miles:%(type)s:%(year)s' % ride,uid,ride['miles'])
    
    def addRideMiles(self,ride):
        """Import stats for a ride: Increase overall mile counts and add ride to top lists"""
        #Increment miles
        self.redis.incr('count:miles:%(date)s' % ride,ride['miles'])
        self.redis.incr('count:miles:%(week)s' % ride,ride['miles'])
        self.redis.incr('count:miles:%(month)s' % ride,ride['miles'])
        self.redis.incr('count:miles:%(year)s' % ride,ride['miles'])
        #Insert into Ride Tables
        ride['id'] = self.redis.get('rides:nextid') or 1
        insertRide = {k: ride[k] for k in ['psng','drvr','miles','date']}
        if self.redis.hmset('rides:%(id)s'%ride,insertRide):
            self.redis.incr('rides:nextid')
            self.redis.zadd('miles:rides:%(date)s'%ride,ride['id'],ride['miles'])
            self.redis.zadd('miles:rides:%(week)s'%ride,ride['id'],ride['miles'])
            self.redis.zadd('miles:rides:%(month)s'%ride,ride['id'],ride['miles'])
            self.redis.zadd('miles:rides:%(year)s'%ride,ride['id'],ride['miles'])

class Randomizer(object):
    """The Randomizer does the heavy lifting of populating the db with users and rides."""
    def __init__(self):
        self.minYear = 2008
        self.maxYear = 2012
        self.maxMiles = 100
        self.Import = RideImporter()
        self.redis = redis.Redis(db=1)

    def clearTables(self):
        """Clear all previous info from the db"""
        self.redis.flushdb()
        
    def Randomize(self,psng,drvr,rides):
        """Called by the Tornado app - creates users and then creates rides for them.
        Params: psng, drvr, rides: number of passengers, drivers, and rides to create.
        Note, the maximum users which can be created is 600 (we need a name for each)."""
        self.createPsng(psng)
        self.createDrvr(psng,drvr)
        self.createRides(rides,psng,drvr)

    def createPsng(self,psng):
        """Create Passengers. Param: psng: number of passengers to create. Uses name list for usernames"""
        for name in names[:psng]:
            self.Import.addUser('psng',{'name':name})

    def createDrvr(self,psng,drvr):
        """Create Drivers. Param: psng: number of passengers previously created, drvr: number of drivers to create"""
        for name in names[psng:psng+drvr]:
            self.Import.addUser('drvr',{'name':name})

    def createRides(self, rides, psng, drvr):
        """Create rides: Match a random rider with a random driver for a random number of miles."""
        random.seed()
        for i in xrange(rides):
            pid = random.randint(1,psng)
            did = random.randint(1,drvr)
            miles = random.randint(1,self.maxMiles)
            year = random.randint(self.minYear,self.maxYear)
            month = random.randint(1,12)
            day = random.randint(1,28)
            date = "%i-%i-%i" % (year,month,day)
            self.Import.addRide(pid,did,miles,date)

# Name list: Give us 600 potential names.
names = ['Luke', 'Ian', 'Jasmine', 'Juliana', 'Stella', 'Brooke', 'Caleb', 'Daniel', 'Aaron', 'Miles', 'Gavin', 'James', 'Taylor', 'Sophia', 'Audrey', 'Carson', 'Katherine', 'Austin', 'Jack', 'Jackson', 'Carter', 'Sebastian', 'Jocelyn', 'Alexa', 'Cameron', 'Isaiah', 'Scarlett', 'Hadley', 'Ethan', 'Isabelle', 'Sadie', 'Abby', 'Nicholas', 'Aiden', 'Grace', 'Blake', 'Bella', 'Summer', 'Joshua', 'Michael', 'Emma', 'Anna', 'Evan', 'William', 'Mason', 'Kendall', 'Benjamin', 'Charlotte', 'Alexandra', 'Max', 'Alexander', 'Abigail', 'Asher', 'Gabriella', 'Alex', 'Aaliyah', 'Bryson', 'Christopher', 'Molly', 'Paige', 'Jordyn', 'Penelope', 'Wyatt', 'Addison', 'Charlie', 'Bentley', 'Lucas', 'Jonathan', 'Caden', 'Lillian', 'Eva', 'Christian', 'Brandon', 'Brianna', 'Ella', 'Kaitlyn', 'Adam', 'Dylan', 'Sienna', 'Elijah', 'Arianna', 'Mia', 'Samantha', 'Nathan', 'Dominic', 'Chloe', 'Xavier', 'Kennedy', 'Chase', 'Lily', 'Adrian', 'Hailey', 'Bailey', 'Caroline', 'Nevaeh', 'Sean', 'Jayden', 'Jason', 'Sophie', 'Annabelle', 'Maya', 'Madison', 'Anthony', 'Kayla', 'Cooper', 'Julian', 'Victoria', 'Brooklyn', 'Lila', 'Hannah', 'Alyssa', 'Joseph', 'Jacob', 'Jeremiah', 'Elise', 'Olivia', 'Sydney', 'Reagan', 'Savannah', 'Owen', 'Sarah', 'Gabriel', 'Kaylee', 'Eli', 'Justin', 'Nolan', 'Lauren', 'Colton', 'Keira', 'Lucy', 'Hayden', 'Kylie', 'Jordan', 'Peyton', 'Layla', 'Riley', 'David', 'Micah', 'Cole', 'Elizabeth', 'Liliana', 'Aubrey', 'Riley', 'Henry', 'Ashlyn', 'Ava', 'Logan', 'Nora', 'Jace', 'Aria', 'Isabella', 'Kate', 'Ellie', 'Gianna', 'Amelia', 'Grayson', 'Hudson', 'Brayden', 'Violet', 'Colin', 'Tyler', 'Nathaniel', 'Liam', 'Natalie', 'Zachary', 'Thomas', 'Ryan', 'Samuel', 'Oliver', 'Matthew', 'Madelyn', 'Bryce', 'Allison', 'Connor', 'Claire', 'Alexis', 'Ryder', 'Morgan', 'Parker', 'Leah', 'Tristan', 'Evelyn', 'Josiah', 'Julia', 'Harper', 'Brody', 'Piper', 'Jake', 'Hunter', 'Makayla', 'John', 'Landon', 'Maria', 'Isaac', 'Noah', 'Mackenzie', 'Andrew', 'Emily', 'Levi', 'Avery']
names.extend(names)
names.extend(names)
