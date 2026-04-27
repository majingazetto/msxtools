#!/usr/bin/env python3


# **********************************************
# * bintrozo                                   *
# * generate "trozo" of files                  *
# **********************************************


import array, struct, sys, io, os


# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "BIN Trozo Tool"
VERSION = "1.1"
COPYRIGHT = "2012"
HEADEROFFSET = 7

# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------


def logo():
    print('%s v%s (c) %s Kralizec' % (PROGRAMNAME, VERSION, COPYRIGHT))
    print()

def usage(execfile):
    print("\nUsage: %s file fileoutput offset size\n" % execfile)
    print() 
    print("    file: file to TROZO ")
    print("    fileoutput: TROZO result")
    print("    offset: init offset of TROZO")
    print("    size: Size of TROZO. You can ommit this param")
    print()


# -----------------------------------------------------------------------------
# File I/O
# -----------------------------------------------------------------------------


def readfile(namefile, header=False, offset=HEADEROFFSET):
    arr = []
    f = open(namefile, 'rb')
    if (header):
        f.seek(offset)
    bytes_read = f.read()
    f.close()
    return bytes_read


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


# -----------------------------------------------------------------------------
# Arrays
# -----------------------------------------------------------------------------

# Merge Arrays

def mergedata(array, arraym):
    data = []
    for c in range (len(array)):
        b = array[c]
        m = arraym[c]
        data.append(b)
        data.append(m)
    return data

# Append array to array

def appenddata(array,data):
    for c in data:
        array.append(c)
    return array


# -----------------------------------------------------------------------------
# Process
# -----------------------------------------------------------------------------

def process(args):

    file = args[1]
    fileoutput = args[2]
    offset =  int(args[3])
    size = 0
    if (len(args) > 4):
        size = int(args[4])

    data = readfile(file)
    sizefile = len(data)

    if (size == 0):
        size = (sizefile - offset) 

    if (offset > sizefile  - 1):
        print("CAZURRO ERROR: Offset > Size of file")
        exit (-1)

    if ( (sizefile - offset) < size):
        print("CAZURRO ERROR: Size > Size of file - Offset")
        exit (-1)


    print("File: %s" % (file))
    print("File Output: %s" % (fileoutput))
    print("Size of File: %i " % (sizefile))
    print("Offset: %i " % (offset))
    print("Size: %i " % (size))

    print()
    print("Trozing...")
    output = []
    for i in range(offset, offset + size, 1): 
        b = data[i]
        output.append(b)

    writefile(fileoutput,output)

    print("Bye!")

# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------


def main(args):
    
    logo()
    if (len(args) < 4):
        usage(args[0])
        exit(-1)
    process(args)

# ---------------------
# Call to Main
# ---------------------
main(sys.argv)





