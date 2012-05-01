from bitarray import bitarray
import unittest

def bitunion(*args): 
    """Union a list of bitarrays of different lengths. Returns a new bitarray
    Implementation: Find the max bitarray length,build new bitarray of that length,substituting False for all
    unfilled positions in other bitarrays.
    """
    return bitarray((max((x[i] if i < len(x) else False for x in args)) for i in xrange(max((len(x) for x in args)))))
def bitintersect(*args): 
    """Intersect a list of bitarrays of different lengths. Returns a new bitarray. Same implementation as above."""
    return bitarray((min((x[i] if i < len(x) else False for x in args)) for i in xrange(max((len(x) for x in args)))))

class TestBitarrayFunctions(unittest.TestCase):
    def setUp(self):
        self.a = bitarray([True, True, False,False])
        self.b = bitarray([False,False,True, True])
        self.long     = bitarray([True, True, False,False,True, False,True])
        self.alsolong = bitarray([True, True, False,True, False,True, False,True, False])
    
    def test_union(self):
        # Test our union function. Should return all true.
        u = bitunion(self.a,self.b)
        self.assertEqual(u.tolist(),[True, True, True, True])
    
    def test_intersect(self):
        n = bitintersect(self.a,self.b)
        self.assertEqual(n.tolist(),[False,False,False,False])
    
    def test_arbitrary_length_union(self):
        u = bitunion(self.long,self.alsolong)
        self.assertEqual(u.tolist(),[True,True,False,True,True,True,True,True,False])
    
    def test_arbitrary_length_intersect(self):
        u = bitintersect(self.long,self.alsolong)
        self.assertEqual(u.tolist(),[True, True, False,False,False,False,False,False,False])
        
if __name__ == '__main__':
    unittest.main()