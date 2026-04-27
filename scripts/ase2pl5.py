#!/usr/bin/env python3

# **********************************************
# * ASE2PL5 Tool                               *
# * Convert .aseprite files to PL5 Pal file    *
# **********************************************


import array, struct, sys, io, os, string, math, json, csv, subprocess,re

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "ASE2PL5"
VERSION = "1.0"
COPYRIGHT = "2020"
HEADEROFFSET = 7





# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Armando Perez' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:      .aseprite file")
    print("     output:     output PL5 file")
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

def readjsonfile(namefile):
    f = open (namefile, 'r')
    data = json.load(f)
    f.close()
    return data

def readcsvfile(namefile, delimiter=","):
    data = []
    with open (namefile, mode = 'r') as csv_file:
        csv_reader = csv.reader (csv_file, delimiter = delimiter)
        for row in csv_reader:
            data.append(row)
    return data

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


def basename(namefile):
    return os.path.splitext(namefile)[0]
    

def notdir(namefile):
    return os.path.basename(namefile)

# -----------------------------------------------------------------------------
# String
# -----------------------------------------------------------------------------

def str2bool (boolstr):
    
    if boolstr.lower() in ("yes", "true", "t", "y", "1"):
        return True
    
    return False


def bytetohexstr (byte):
    db = "#"
    if (byte < 0x10):
        db += "0"
    db += "%X" % byte
    return db


# -----------------------------------------------------------------------------
# .aseprite
# -----------------------------------------------------------------------------

# Data types

ASE_BYTE = 1
ASE_WORD = 2
ASE_SHORT  = 2
ASE_DWORD = 4
ASE_LONG = 4

# Offsets

ASE_HEADER_SIZE = 128


# BPP types

ASE_BPP_RGBA = 32
ASE_BPP_GRAY = 16
ASE_BPP_INDEXED = 8

# Chunk Types

ASE_CHUNK_PALETTE = 0x2019

# Get data type

def getword(data, offset):
    return data[offset] + (data[offset + 1] << 8)

def getdword(data, offset):

    b0 = data[offset]
    b1 = data[offset + 1]
    b2 = data[offset + 2]
    b3 = data[offset + 3]

    return b0 + (b1 << 8) + (b2 << 16) + (b3 << 32)

# Read Heder

def readheader (asedata):

    header = asedata[0:ASE_HEADER_SIZE] 
    seekp = ASE_HEADER_SIZE 

    return header, seekp


def getframe (asedata, offset):
    
    size = getdword(asedata, offset) + offset
    return asedata[offset: size], offset + size

def getpalchunk (frame, offset):
    
    chkoff = ASE_DWORD + ASE_WORD + ASE_WORD + ASE_WORD + 2 + ASE_DWORD
    
    size = getdword (frame, chkoff)
    type = getword (frame, chkoff + ASE_DWORD)
    
    if (type != ASE_CHUNK_PALETTE):
        print("ERROR: No palette chunk found!")
        exit (-1)
    
    chkoff = chkoff + ASE_DWORD + ASE_WORD
   
    size = size + chkoff
    return frame [chkoff : size]

def getbpp (header):
    
    offset = ASE_DWORD + ASE_WORD + ASE_WORD + ASE_WORD + ASE_WORD

    return getword(header, offset)




# Get RGB

def getrgbfromchunk (chunk):

    palsize = getdword (chunk, 0)
    offset = ASE_DWORD + ASE_DWORD + ASE_DWORD + 8
    
    rgb = []
    for entry in range(0, palsize):
        f = chunk[offset]
        r = chunk[offset + 2]
        g = chunk[offset + 3]
        b = chunk[offset + 4]
        a = chunk[offset + 5]
        offset = offset + 6
        rgb.append ([r, g, b]) 

    return rgb


# Return PL5 file from .aseprite

def getpl5 (asedata):
    
    pl5 = []
    
    header, offset = readheader(asedata)
    
    bpp = getbpp(header)
        
    if (bpp != ASE_BPP_INDEXED):
        print("ERROR! Not indexed palette")
        exit (-1)

    frame, offset = getframe (asedata, offset)
        
    pl5chunk = getpalchunk(frame, 0) 

    rgb = getrgbfromchunk (pl5chunk) 

    
    return paltopl5(rgb)



# -----------------------------------------------------------------------------
# PALETTE RELATED
# -----------------------------------------------------------------------------


def paltopl5 (palette):

    pal = [];
    
     
    for i in range(0, len(palette)):
        color = palette[i]
        r = color[0]
        g = color[1]
        b = color[2]

            
        # Quick (bad) conversion
        #r = (r >> 1) & 0x70
        #g = (g >> 5) & 7
        #b = (b >> 5) & 7
        
        r = rgbto9938(r)
        g = rgbto9938(g)
        b = rgbto9938(b)

        palRB = (r << 4) | b
        palG = g
        
        # add to table 
        pal.append(palRB)
        pal.append(palG)
     
    return pal

def rgbto9938 (rgb):
    
    if (rgb <= 16):
        return 0

    if (rgb <= 48):
        return 1

    if (rgb <= 80):
        return 2

    if (rgb <= 108): 
        return 3

    if (rgb <= 144): 
        return 4

    if (rgb <= 176): 
        return 5

    if (rgb <= 208):
        return 6
    
    return 7


# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 3):
        usage(args[0])
        exit (-1)

    inputfile = args[1]
    outputfile = args[2]

    print(".aseprite file: ", inputfile)
    print("PL5 file: ", outputfile)

    inputdata = readfile (inputfile)
    
    pl5data = getpl5(inputdata)

    writefile(outputfile, pl5data)

    #bye
    exit(0)




# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    




