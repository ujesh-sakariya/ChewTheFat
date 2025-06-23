#get the gcd function from euclidAlgo
from euclidAlgo import gcd 
import sys

sys.setrecursionlimit(10000)
# defining the function 
def carmichael(n1,n2):
    # first we minus 1 from both these numbers 
    n1 -= 1
    n2 -= 1
    # next we find n3
    n3 = n1 * n2
    # We then calculate lcm using the formula 
    lcm = int(n3 // gcd(n1,n2))

    return lcm 



    