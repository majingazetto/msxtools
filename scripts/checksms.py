#!/usr/bin/env python3

# **********************************************
# * CHECKSUM Tool                              *
# * Calculate CRC FOR SMS                      *
# **********************************************

import array, struct, sys, io, os, string

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "Checksum SMS Tool"
VERSION = "1.0"
COPYRIGHT = "2016"
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
    
    checksum = 0
    for i in range (0, 8192 - 16):
        b = datain[i] 
        checksum += b
        checksum &= 0xFFFF

    # Calculate value
    print("Checksum: %X" % checksum)

    # Write
    datain[0x4000 - 16 + 10] = checksum & 0xFF
    datain[0x4000 - 16 + 11] = (checksum >> 8) & 0xFF
    writefile(outputname, datain)


    print("Ok. Bye!") 
    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



