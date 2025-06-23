import sys

sys.setrecursionlimit(10000)

def gcdExtended(a, b):

    
    # Base Case
    if a == 0:
        return b, 0, 1
 
    gcd, x1, y1 = gcdExtended(b % a, a)
 
    # Update x and y using results of recursive call
    x = y1 - (b//a) * x1
    y = x1
    
    return gcd, x, y
 
 
#driver code
def findx(a,b):

    g, x, y = gcdExtended(a, b)
    # Our X value will be negtive, therefore we add it back to orignal b
    x = x + b
    return x




