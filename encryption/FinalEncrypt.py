from random import randint, random
import sys

sys.setrecursionlimit(10000)

def binExp(base, exponent, mod):
    if mod == 0:
        raise Exception("mod argument should not be 0")
    out = 1
    base %= mod
    current = base
    while exponent != 0:
        if exponent % 2 == 1:
            out = (out * current) % mod
        current = (current * current) % mod
        exponent //= 2
    return out

def composite(n, a, copy, two):
    value = binExp(a, copy, n)
    if value == 1 or value == n - 1:
        return 0
    for _ in range(two):
        value = (value * value) % n
        if value == n - 1:
            return 0
    return 1

def checkPrime(n):
    if n < 4:
        return n == 2 or n == 3
    if n % 2 == 0:
        return 0
    copy = n - 1
    two = 0
    while copy % 2 == 0:
        copy //= 2
        two += 1
    ITERATIONS = 50
    INT_MAX = 2 ** 31
    for _ in range(ITERATIONS):
        a = 2 + randint(0, INT_MAX) % (n - 3)
        if composite(n, a, copy, two):
            return 0
    return 1

def findPrime():
    n1 = 10 ** 400 + randint(10 ** 300, 10 ** 400)
    n2 = 10 ** 400 + randint(10 ** 300, 10 ** 400)
    while not checkPrime(n1):
        n1 += 1
    while not checkPrime(n2):
        n2 += 1
    return str(n1), str(n2)

def n(x, y):
    return x * y

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def carmichael(n1, n2):
    n1 -= 1
    n2 -= 1
    return (n1 * n2) // gcd(n1, n2)

def findE(lamN):
    e = randint(1, lamN)
    while gcd(e, lamN) != 1:
        if e < lamN - 1:
            e += 1
        else:
            e = randint(1, lamN)
    return e

def gcdExtended(a, b):
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = gcdExtended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def findx(a, b):
    _, x, _ = gcdExtended(a, b)
    return x + b

from random import randint, random
import sys

sys.setrecursionlimit(10000)

def binExp(base, exponent, mod):
    if mod == 0:
        raise Exception("mod argument should not be 0")
    out = 1
    base %= mod
    current = base
    while exponent != 0:
        if exponent % 2 == 1:
            out = (out * current) % mod
        current = (current * current) % mod
        exponent //= 2
    return out

def composite(n, a, copy, two):
    value = binExp(a, copy, n)
    if value == 1 or value == n - 1:
        return 0
    for _ in range(two):
        value = (value * value) % n
        if value == n - 1:
            return 0
    return 1

def checkPrime(n):
    if n < 4:
        return n == 2 or n == 3
    if n % 2 == 0:
        return 0
    copy = n - 1
    two = 0
    while copy % 2 == 0:
        copy //= 2
        two += 1
    ITERATIONS = 50
    INT_MAX = 2 ** 31
    for _ in range(ITERATIONS):
        a = 2 + randint(0, INT_MAX) % (n - 3)
        if composite(n, a, copy, two):
            return 0
    return 1

def findPrime():
    n1 = 10 ** 400 + randint(10 ** 300, 10 ** 400)
    n2 = 10 ** 400 + randint(10 ** 300, 10 ** 400)
    while not checkPrime(n1):
        n1 += 1
    while not checkPrime(n2):
        n2 += 1
    return str(n1), str(n2)

def n(x, y):
    return x * y

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def carmichael(n1, n2):
    n1 -= 1
    n2 -= 1
    return (n1 * n2) // gcd(n1, n2)

def findE(lamN):
    e = randint(1, lamN)
    while gcd(e, lamN) != 1:
        if e < lamN - 1:
            e += 1
        else:
            e = randint(1, lamN)
    return e

def gcdExtended(a, b):
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = gcdExtended(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def findx(a, b):
    _, x, _ = gcdExtended(a, b)
    return x + b

def message(text):
    m = 0
    for char in text:
        m = m * 128 + ord(char)
    return m

def decrypt(m):
    out = ""
    while m:
        out += chr(m % 128)
        m //= 128
    out = out[::-1]
    return out


# Generate primes
p_str, q_str = findPrime()
p = int(p_str)
q = int(q_str)

# Calculate n and Carmichael's totient
n_val = n(p, q)
lam_n = carmichael(p, q)

# Generate public exponent e
e = findE(lam_n)

# Find private exponent d (modular inverse of e)
d = findx(e, lam_n)
d %= lam_n

# Example message to encrypt
message = message('HELLO')

# Encrypt the message
ciphertext = binExp(message, e, n_val)

# Decrypt the message
decrypted = decrypt(binExp(ciphertext, d, n_val))



# Print results
print(f"Original message: {message}")
print(f"Ciphertext: {ciphertext}")
print(f"Decrypted message: {decrypted}")