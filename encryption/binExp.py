# This function computes exponents in logarithmic time complexity
def binExp(base,exponent,mod):

    # This checks if mod is 0, if so it would lead to division by 0
    # And this would cause an arithmetic error
    if mod == 0:
       # We raise an exception here so that we can identify issues
       # more easily later when we are debugging
        raise Exception("mod argument should not be 0")
        # out stores the output for the calculation
    out = 1

     # This will make the program faster and won’t change the output
    base %= mod

    current = base
    # This loop will run until the exponent is not 0.
    # Once the exponent is 0, this means that it has gone over each binary digit in the exponent

    while exponent !=0:
    
        # Here we are seeing if the exponent is an odd number.
        # If the exponent is an odd number, this means that the right most binary 
        # digit in the exponent which has not alrady been iterated over is 1

        if exponent % 2 == 1:

        # The current output is now what the original value was multiplied by the new current value.
        # This is only carried out if the binary digit represents 1.

            out = (out * current) % mod

        # This caluclates the current value. it times the current value by 
        # itself (squaring), therefore we would get for example ^2 to the power of ^4
        # which is needs to carry out the binary exponentiation as shown in the development
        #section. 
        current = (current * current) % mod
        # floor dividing the exponent allows for the next binary value to be found
        # from the denary exponent'''
        exponent //= 2

    return out


