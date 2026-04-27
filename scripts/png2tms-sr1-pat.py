#!/usr/bin/env python3

# **********************************************
# * PNG2TMS Tool                               *
# * Convert PNG file to TMS patters            *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNG2TMS-PAT SR1 Tool"
VERSION = "1.1"
COPYRIGHT = "2016 - 2020"
HEADEROFFSET = 7
RAWPATSIZE = 0x4000
FIXEDWIDTH = 256
TBLCOLSIZE = 32

# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Ramones' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:    4 bit indexed PNG File (Special B/W + Color table format).")
    print("     output:   Converted Raw Pattern data file (PAT and CT1).")
    print("     number of patterns (optional): number of patterns to extract.")
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
# PNG
# -----------------------------------------------------------------------------

def pixelstoraw (pixels):
    raw = []
    for row in pixels:
        for i in range(0, len(row)):
            raw.append(row[i])
    return raw


# -----------------------------------------------------------------------------
# RAW DATA
# -----------------------------------------------------------------------------

#a[start:stop]  # items start through stop-1
#a[start:]      # items start through the rest of the array
#a[:stop]       # items from the beginning through stop-1
#a[:]           # a copy of the whole array

# Split data in pixel raw pattern data and color pattern data
def splitrawdata (rawdata):
    
    pat = []
    col = []
   
    if (len(rawdata) < RAWPATSIZE):
        pat = rawdata[:]
    else:
        pat = rawdata[:RAWPATSIZE]
        col = rawdata[RAWPATSIZE:]
    
    return pat, col





# -----------------------------------------------------------------------------
# TMS Pattern 
# -----------------------------------------------------------------------------


def calcbackcolor (raw):
    two = []
    for col in raw:
        if (col in two) == False:
            two.append(col)
    
    cback = 0;

    if (len(two) == 1):
        if (two[0] == 0):
            cback = 0;
        else:
            #cback = two[0]
            cback = (two[0] - 1) & 0xF
        

    if (len(two) == 2):
        if (0 in two):
            cback = 0
        else:
            if (two[0] < two[1]):
                cback = two[0]
            else:
                cback = two[1]

    return cback 

#SR1 B/W Mode: Color 0 is always back
def rawpat2dat (raw):
    data = []
    idx = 0;
    for byte in range (0, 8):
        bt = 0;
        # Calc color background - foreground
        pixels = []
        for i in range (0, 8):
            pix = raw[idx + i]
            pixels.append(pix)
        # Calc byte
        for i in range (0, 8):
            bt <<= 1;
            pix = raw[idx]
            idx += 1
            if (pix > 1):
                bt |= 1
        data.append(bt)
    return data

def extractpatraw (idx, raw, width, height):
    
    # Calc offsets
    w8 = width >> 3
    h8 = height >> 3
    y = int(idx / w8)
    x = int(idx % w8)
    offset = int((y * width * 8) + x * 8)
   
    data = []

    # 8 x 8 bytes
    for y in range (0,8):
        for x in range (0, 8):
            byte = raw[offset + (y * width) + x]
            data.append(byte)

    return data

def rawtotmspat (raw, patterns):

    height = int (len(raw) / 256)
    numpat = int((FIXEDWIDTH >> 3) * (height >> 3))
    if (patterns != 0):
        numpat = patterns


    print("Number of patterns to extract: ",numpat)
         
    tmsdata = [] 
    for idx in range (0, numpat):
        patraw = extractpatraw(idx, raw, FIXEDWIDTH, height)
        patdat = rawpat2dat(patraw) 
        for byte in patdat:
            tmsdata.append(byte)

    return tmsdata


# -----------------------------------------------------------------------------
# TMS SR1 Color
# -----------------------------------------------------------------------------


def rawtosr1col(coldata, lenght):
    tblsize = TBLCOLSIZE
    if (lenght != 0):
       tblsize = int(lenght / 8)
    tblcol = [0 for i in range (tblsize)]
    height = int(len(coldata) / FIXEDWIDTH)
    
    for idx in range (0, tblsize):
        colraw = extractpatraw (idx, coldata, FIXEDWIDTH, height)
        coldat = rawcol2sr1(colraw)
        tblcol[idx] = coldat

    return tblcol

def rawcol2sr1 (raw):
    bc = raw[0]
    fc = bc

    for c in raw:
        if c != bc:
            fc = c
            break

    coldat = ((bc & 0x0F) +  ((fc & 0xF) << 4)) & 0xFF

    return coldat


# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 3):
        usage(args[0])
        exit (-1)

    filename = args[1]
    outputname = args[2]
    
    outputnamepat = outputname + ".PAT"
    outputnamecol = outputname + ".TC1"
    print("Input:  ", filename)
    print("Output Pattern: ", outputnamepat)
    print("Output Color: ", outputnamecol)
    

    lenght = 0;
    if (len(args) == 4):
        lenght = int(args[3])

    # Read and process 

    img = Image.open(filename)
    if img.mode != 'P':
        print("ERROR: Not indexed image!!")
        exit(-1)
    w, h = img.size
    print("Width : ", w)
    print("Height: ", h)

    if (w < 8):
        print("ERROR: Min Width = 16!!!!")
        exit(-1)

    if (h < 8):
        print("ERROR: Min Height = 16!!!!")
        exit(-1)

    palette_mode, palette_data = img.palette.getdata()
    stride = len(palette_mode)
    n_colors = len(palette_data) // stride
    palette = [(palette_data[i*stride], palette_data[i*stride+1], palette_data[i*stride+2]) for i in range(n_colors)]

    if len(palette) > 16:
        print("Warning: > 16 colour image!!")

    raw_pixels = img.tobytes()
    pixel_list = [list(raw_pixels[y*w:(y+1)*w]) for y in range(h)]

    # list pixels to raw data
    rawdata = pixelstoraw(pixel_list)

    # Split pattern and color data
    rawpatdata, rawcoldata = splitrawdata(rawdata)

    # Create pattern data
    patdata = rawtotmspat(rawpatdata, lenght)
    writefile (outputnamepat, patdata);



    # Create color data

    if (rawcoldata):
        coldata = rawtosr1col(rawcoldata, lenght)
        writefile (outputnamecol, coldata);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    




