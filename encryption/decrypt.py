def decrypt(m):
        # out stores the output message as we generate it
    out = ""
    # This makes us keep adding characters to out until m == 0
    while m:
    # This takes m modulo 128 and chr will turn that number into a
    # character via ASCII or unicode
    # We then add this character onto the end of out
        out += chr(m % 128)
    # We then divide m by 128 to get to the next character
        m //= 128
    # This reverses the string out as we will have generated the original
    # message backwards
    out = out[::-1]
    # We can then just print out the original message
    return(out)