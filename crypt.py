#!/usr/bin/env python

from Crypto.Cipher import AES
import base64
import os, sys
from getpass import getpass

# the block size for the cipher object; must be 16 per FIPS-197
BLOCK_SIZE = 16

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

def encrypt(infile, outfile):
    data = ''
    with open(infile, 'r') as f:
        for line in f:
            data += line
    secret = getpass('Enter password: ')
    cipher = AES.new(secret)    
    e = EncodeAES(cipher, data)
    with open(outfile, 'w') as f:
        f.write(e)

def decrypt(infile, outfile):
    data = ''
    with open(infile, 'r') as f:
        for line in f:
            data+=line.strip()
    secret = getpass('Enter password: ')
    cipher = AES.new(secret)
    decoded = DecodeAES(cipher, data)
    with open(outfile, 'w') as f:
        f.write(decoded)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print 'Bad settings'
        os._exit(1)
    else:
        mode = sys.argv[1]
        if mode == 'enc':
            encrypt(sys.argv[2], sys.argv[3])
        elif mode == 'dec':
            decrypt(sys.argv[2], sys.argv[3])
        else:
            os._exit(1)



