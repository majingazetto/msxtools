#!/usr/bin/env python3

# **********************************************
# * ACWA Tool                                  *
# * Calculate CRC FOR ACWA ROM SELF TEST       *
# **********************************************

import array, struct, sys, io, os, string

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "ACWA Tool"
VERSION = "1.0"
COPYRIGHT = "2012"
HEADEROFFSET = 7


# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Kralizec' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:    Binary file to calculate.")
    print("     output:   Output modified file")
    print() 

# -----------------------------------------------------------------------------
# File I/O
# -----------------------------------------------------------------------------


def readfile(namefile, header=True, offset=HEADEROFFSET):
    arr = []
    f = open(namefile, 'rb')
    if (header):
        f.seek(offset)
    bytes_read = f.read()
    for b in bytes_read:
        byte = struct.unpack('B', b)
        arr.append(byte[0])
    f.close()
    return arr


def readstringfile(namefile):
    f = open (namefile, 'r')
    string = f.read()
    f.close()
    return string


def writefile(namefile, data):
    f = open (namefile,'wb')
    for b in data:
        byte = struct.pack('B',b)
        f.write(byte)
    f.flush()
    f.close()            

        
def writestringfile(namefile, string):
    f = open (namefile, 'wb')
    for b in string:
        f.write(b)
    f.flush()
    f.close()

# ----------------------------------------------------------------------------- # Main program # -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 3):
        usage(args[0])
        exit (-1)

    filename = args[1]
    outputname = args[2]

    datain = readfile(filename, False)
    
    acwa = 0
    carry = 0
    for i in range (len (datain) - 1):
        b = datain[i] 
        acwa += carry
        acwa += b
        # check carry
        carry = 0 
        cy = acwa & 0x100
        acwa = acwa & 0xFF
        if (cy != 0):
            carry = 1
        

    # Calculate value
    print("ACWA - 1: %x" % acwa)
    print("Carry: %x" %carry)
    value = (0x100 - acwa) & 0xFF
    value = (value - carry) & 0xFF
    print("Calculated last byte: %x" % value) 
    acwa = (acwa + carry + value) & 0xFF
    print("ACWA + Calculated byte: %x" % acwa)

    # Write
    datain[len(datain) -1] = value
    writefile(outputname, datain)


    print("Ok. Bye!") 
    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    


