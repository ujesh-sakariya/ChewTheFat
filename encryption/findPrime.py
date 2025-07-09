from millerRabin import checkPrime 
from random import randint


def findPrime():

# This is our starting point to search for the next prime after
# We use a random number from randint to find where we start
# we initialise the 2 starting numbers
    
    n1 = 10**400 + randint(10**300, 10**400)
    n2 = 10**400 + randint(10**300, 10**400)
# While number isn’t prime we keep increasing number by 1 until
# We get number being prime

    while not checkPrime(n1):
        n1 += 1
    # If we have reached this point we know number is prime 
    while not checkPrime(n2):
        n2 += 1
    
    n1 = str(n1)
    n2 = str(n2)
    return(n1,n2)
     
   # with open('newPrimeNumbers.txt', 'a') as fh:
    #    fh.write((str(n1)+'\n'))
     #   fh.write((str(n2)+'\n'))



 