#!/usr/bin/env python3

# **********************************************
# * BIN PACKER FOR MAJIKAZO                    *
# **********************************************


import array, struct, sys, io, os, string, operator


# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "Binary Pack Tool"
VERSION = "1.0"
COPYRIGHT = "2017"
HEADEROFFSET = 7


# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Armando Perez' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s directory maxsize prefix suffix ext \n" % execfile)
    print("     directory: where get files to pack.")
    print("     maxsize:   pack max size")
    print("     prefix:    file output prefix")
    print("     suffix:    file output suffix")
    print("     ext:       file output extension")
    print("     pntsuff:   Pointer data suffix")
    print("     output:    output dir")
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

# -----------------------------------------------------------------------------
# Arguments
# -----------------------------------------------------------------------------

def argtoint (arg):

    if arg.startswith("0x"):
        return int(arg, 16)

    return int(arg)


# -----------------------------------------------------------------------------
# Bin Packing 
# -----------------------------------------------------------------------------


class Bin(object):
    """ Container for items that keeps a running sum """
    def __init__(self):
        self.items = []
        self.sum = 0

    def append(self, key, item):

        self.items.append([key, item])
        self.sum += item

    def __str__(self):
        """ Printable representation """
        return 'Bin(sum=%d, items=%s)' % (self.sum, str(self.items))


def pack(values, maxValue):

    bins = []

    for key, item in values:
        # Try to fit item into a bin
        for bin in bins:
            if bin.sum + item <= maxValue:
                #print 'Adding', item, 'to', bin
                bin.append(key, item)
                break
        else:
            # item didn't fit into any bin, start a new bin
            #print 'Making new bin for', item

            if item <= maxValue:
                bin = Bin()
                bin.append(key, item)
                bins.append(bin)

    return bins



# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()

    if (len(args) < 8):
        usage(args[0])
        exit(-1)

    # Read arguments
    
    maxsize = argtoint(args[2])
    prefix = args[3]
    suffix = argtoint(args[4])
    ext = args[5]
    psuffix = args[6]
    output = args[7]

    # print arguments

    print("Maxsize: ", maxsize)
    print("Prefix : ", prefix)
    print("Suffix : ", suffix)
    print("Ext    : ", ext)
    print("Output : ", output)


    # maxsize for ALIGN

    tmaxsize = "{0:#0{1}x}".format(maxsize , 6)[2:]

    # Read all files
    
    files = {}
    for file in os.listdir(args[1]):
        fsize = os.path.getsize(args[1] + "/" + file)
        files[file] = fsize
        
    # order items
    sortf  = sorted(list(files.items()), key=operator.itemgetter(1), reverse = True) 
    
    # pack 
    bins = pack(sortf, maxsize)

    # create files

    tsuffix = suffix
    for bin in bins:
        suf = "{0:#0{1}x}".format(tsuffix , 4)[2:]
        name = "                * " + prefix + suf.upper() + "." + ext
        name = name.ljust(77) + "*\n"

        str = "        \
        **************************************************************\n"
        str += name
        
        str += "        \
        **************************************************************\n"

        str += "\n"
        str += "\n"
        str += "                ORG #A000\n"
        str += "\n"
        str += "\n"
        str += "--- RESOURCES   --------------------------------------------------------------\n"
        str += "\n"
        str += "\n"

            
        for key, value in bin.items:
            next = key.split(".")[-1]
            nfile = key.split(".")[0]
            label = (nfile + "_" + next).ljust(16)
            str += label + "INCBIN " + key + "\n"

        str += "\n"
        str += "\n"
        str += "--- ALIGN       --------------------------------------------------------------\n"
        str += "\n"
        str += "\n"
        #str += "                DEFS #C000 - $, #FF\n"        
        str += "                ALIGN  #" + tmaxsize
        str += "\n"
        str += "\n"
        tsize = "{0:#0{1}x}".format(bin.sum , 6)[2:]
        str += "                - TOTAL SIZE: #" + tsize.upper()
        str += "\n"
        str += "\n"



        fname = prefix + suf.upper() + "." + ext
        fname = output + "/" + fname
        writestringfile(fname, str)
        tsuffix += 1

    
    # create pointer file

    name = "                * " + prefix + "PNT." + ext
    name = name.ljust(77) + "*\n"

    str =  "**************************************************************\n".rjust(79)
    str += name
    str += "**************************************************************\n".rjust(79)
    
    str += "\n"
    str += "\n"
    str += "--- BANK        --------------------------------------------------------------\n"
    str += "\n"
    str += "\n"
     

    tsuffix = suffix


    for bin in bins:
        suf = "#" + "{0:#0{1}x}".format(tsuffix , 4)[2:].upper()
        for key, value in bin.items:

            next = key.split(".")[-1]
            nfile = key.split(".")[0]
            #pointer = (next + nfile).ljust(16)

            #nfile = key.split(".")[0]
            label = (nfile + "_" + next + "_B").ljust(16)

            str += label 
            str += "EQU  " + suf + "\n"
            #str += "                DEFW " + pointer + "\n\n"

        tsuffix += 1

    fname = output + "/" + prefix + "PNT." + ext    
    writestringfile(fname, str)

    # create include file

    name = "                * " + prefix + "INC." + ext
    name = name.ljust(77) + "*\n"

    str =  "**************************************************************\n".rjust(79)
    str += name
    str += "**************************************************************\n".rjust(79)
    
    str += "\n"
    str += "\n"
    str += "--- INCLUDE     --------------------------------------------------------------\n"
    str += "\n"
    str += "\n"
     

    tsuffix = suffix

    for bin in bins:
        suf = "{0:#0{1}x}".format(tsuffix , 4)[2:].upper()
        str += "".ljust(16) + "INCLUDE " + prefix + suf + "." + ext + "\n"
        tsuffix += 1

    fname = output + "/" + prefix + "INC." + ext    
    writestringfile(fname, str)


# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    





