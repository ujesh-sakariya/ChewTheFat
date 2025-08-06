def message(text):
# This is the public key generated from multiplying our primes together
# This is our output message stored as an integer
    m = 0
# This iterates over all of the characters in the message
    for i in range(len(text)):
   # This shifts all of the current characters in m to the left so that
   # our current character won’t interfere with the previous ones
        m *= 128
   # The ord function gets the unicode value of the current character
   # and we add this onto m
        m += ord(text[i])

    return(m)

