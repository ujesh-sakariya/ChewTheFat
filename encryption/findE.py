# get the gcd function fron euclidAlgo
from euclidAlgo import gcd
#get a random number generator 
import random

# Define the function 
def findE(lamN):
    # generate a random number 
    e = random.randint(1,lamN)
    # test if e is coprime with lamN
    while (gcd(e,lamN)) != 1:
        # if not test if e is less than 1 less than lamN
        if e < (lamN -1):
            # test with the next value of e
            e += 1
        # if the next value will not be less than lamN, generate a new value for e
        else:
            e = random.randint(1,lamN)
    return e
    

