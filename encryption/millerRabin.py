# We import randint from random so that we can generate random integers
from random import randint
# we also need to get binExp function
from binExp import binExp


# This function checks if a number is composite using a value
def composite(n, a, copy, two):
   # We use our binExp function from earlier to calculate a**copy
   # efficiently under the modulo of n
   value = binExp(a, copy, n)
   # If either value == 1 or value == n-1 then we know that n is not
   # composite because this only holds for prime numbers
   if value == 1 or value == n-1:
       # We know n is prime so we just return 0
       return 0
   # We iterate from 0 to two-1
   for r in range(0,two):
       # We square value under the modulo of n to test for the next
       # factor in Fermat’s little theorem
       value = (value*value) % n
       # If value == n-1 then we know value+1 is divisible by n
       # This only holds for prime numbers so we know that n is not
       # composite and we can return 0
       if value == n-1:
           return 0
   # If we have reached this point then we know that n is composite
   # So we can just return 1
   return 1
# This function checks if a number if prime by testing
# If it is composite with many randomly generated values
# It will return 1 if it is prime or 0 if it isn’t
def checkPrime(n):
   # This accounts for the edge cases where n is very small
   if n < 4:
       # If n < 4 then the only primes are 2 and 3 so,
       # This function will return 1 if n == 2 or n == 3
       return n == 2 or n == 3
   
   # This accounts for all cases where n is even
   # If we have reached this stage we know n >= 3 so it can’t be prime
   if n % 2 == 0:
       return 0


   # This creates a copy of n with its value decremented by 1
   copy = n-1
   # This initialises the variable two to zero
   two = 0
   # This keeps dividing copy by 2 until it becomes odd
   # We store how many times we needed to divide it in the variable two
   while not copy % 2 == 1:
       copy //= 2
       two += 1


   # Here we set up some constants
   # ITERATIONS is the number of times we check the number is composite
   # INT_MAX defines the maximum random number that we can use
   ITERATIONS = 50
   INT_MAX = 2**31
   # This just does the check ITERATIONS times
   for i in range(ITERATIONS):
       # We generate a random integer and take it modulo (n-3)
       # We then add 2 so that a < n
       a = 2 + randint(0,INT_MAX) % (n-3)
       # We use a to check if n is composite
       if composite(n, a, copy, two):
           # If a has shown to be composite we can return 0 as we know
           # That the number is not prime
           return 0
   # If we have reached this point then we know that n must be prime
   # So we just return 1
   return 1




