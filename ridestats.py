import redis
import logging
from bitarray import bitarray

def bitunion(*args): 
    """Union a list of bitarrays of different lengths. Returns a new bitarray
    Implementation: Find the max bitarray length, build new bitarray of that length, substituting False for all
    unfilled positions in other bitarrays.
    """
    return bitarray((max((x[i] if i < len(x) else False for x in args)) for i in xrange(max((len(x) for x in args)))))
def bitintersect(*args): 
    """Intersect a list of bitarrays of different lengths. Returns a new bitarray. Same implementation as above."""
    return bitarray((min((x[i] if i < len(x) else False for x in args)) for i in xrange(max((len(x) for x in args)))))

class Stats(object):
    """The Stats class is the interface with Redis and formats answers for the tornado app"""
    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost',db=1)
        self.redis = redis.Redis(connection_pool=self.pool)

    def hasStats(self):
        """Checks if we have any stats - no passengers = no stats."""
        return (self.redis.get('psng:nextid') != None)

    def getUserCounts(self,who,when):
        """Get bitarray from Redis, count "True"s"""
        table = "count:%s:%s" % (who,when)
        bytes = self.redis.get(table)
        if not bytes:
            return 0
        count = bitarray()
        count.frombytes(bytes)
        return count.count()

    def getMileCounts(self,when):
        """Get Mile Counts. Simple Int - pass unedited."""
        table = "count:miles:%s" % (when)
        count = self.redis.get(table) or 0
        return count

    def getTopUsers(self,who,when,count=10):
        """Get top <count> users, match userid with nickname."""
        table = "miles:%s:%s" % (who, when)
        redis_top = self.redis.zrevrange(table,0,count,withscores=True)
        toplist = []
        # Empty if no results.
        for top in redis_top:
            topmap = self.getUserInfo(who,top[0])
            topmap['miles'] = top[1]
            toplist.append(topmap)
        return toplist

    def getTopRides(self,when,count=10):
        """Get top <count> rides, match passenger and driver ids with nicknames"""
        table = "miles:rides:%s" % when
        redis_top = self.redis.zrevrange(table,0,count,withscores=True)
        toplist = [self.getRideInfo(rideid=t[0]) for t in redis_top]
        return toplist

    def getRideInfo(self,rideid):
        """Gets info for a ride, including passenger and driver nicknames"""
        rideinfo = self.redis.hgetall('rides:%s' % rideid)
        rideinfo['id'] = rideid
        rideinfo['miles'] = int(rideinfo['miles'])
        rideinfo['drvr'] = self.getUserInfo('drvr',rideinfo['drvr'],'name')
        rideinfo['psng'] = self.getUserInfo('psng',rideinfo['psng'],'name')
        return rideinfo

    def getUserInfo(self,who,userid,field=None):
        """Get individual user info. Defaults to returning all info"""
        table = "%s:%s" % (who, userid)
        if field:
            info = {field:self.redis.hget(table,field)}
        else:
            info = self.redis.hgetall(table)
        info['id'] = userid
        return info

    def close(self):
        """Clean up connection."""
        self.pool.disconnect()
