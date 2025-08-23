#import the neccesary functions to encrypt the message
from findPrime import findPrime
from n import n
from carmichael import carmichael
from findE import findE
from extEuclidAlgo import findx
from message import message
from binExp import binExp
from decrypt import decrypt
import sys
sys.setrecursionlimit(10000)
# Find the 2 prime numbers
p,q = findPrime()
p = int(p)
q = int(q)
print(f'The 2 prime numbers: \n p is{p} \n q is {q}\n')
N = n(p,q)
print(f'N (which is the multiplication of the 2 prime numbers is: \n {N}')
# find the carmicheal value
lamN = carmichael(p,q)
print(f'lamN (which is the value after passing the 2 prime numbers into the carmichael function): \n{lamN}')
# find E
e = findE(lamN)
print(f' The encryption k is: \n {e}')
# find d 
d = findx(e,lamN)
print(f'The decryption key is \n {d}')
# obtain the message that will be encrypted
plaintext = int(message(input("enter message to encrypt: ")))
# encrpyt the message
cyphertext = binExp(plaintext,e,N)
print(f'the cyphertext is \n{cyphertext}')
# decrypt the message
decrypted = binExp(cyphertext,d,N)
# output the message
#convert from ASCII into the string
message = decrypt(decrypted)
print(message)
