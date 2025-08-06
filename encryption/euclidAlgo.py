# Eulerian algorithm
# This calculates the greatest common divisor of two numbers
# in logarithmic time complexity
def gcd(a, b):
   # While b is greater than 0
   while b:
       # We store the value of b in a temporary variable
       tmp = b
       # We then set b to a % b
       b = a % b
       # We then replace a with the old value b we stored earlier
       a = tmp
   # Once we have reduced b to 0, a will store the greatest common
   # divisor between the original a and b
   return a

