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

PROGRAMNAME = "PNG2TMS-PAT Tool"
VERSION = "1.0"
COPYRIGHT = "2017"
HEADEROFFSET = 7



# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Ramones' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:    4 bit indexed PNG File.")
    print("     output:   Converted Raw Sprite data file.")
    print("     back:     Force Back Color (optional).")
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
# TMS Pattern 
# -----------------------------------------------------------------------------


def calcbackcolor (raw, back):
    two = []
    for col in raw:
        if (col in two) == False:
            two.append(col)
    
    cback = 0;


    if (back != -1):
        if (back in two) == True:
            return back

    if (len(two) == 1):
        cback = two[0]

    if (len(two) == 2):
        if (1 in two):
            cback = 1
        elif (0 in two):
            cback = 0
        else:
            if (two[0] < two[1]):
                cback = two[0]
            else:
                cback = two[1]

    return cback 

def rawpat2dat (raw, back):
    data = []
    idx = 0;
    for byte in range (0, 8):
        bt = 0;
        # Calc color background - foreground
        pixels = []
        for i in range (0, 8):
            pix = raw[idx + i]
            pixels.append(pix)
        cback = calcbackcolor(pixels, back)
        # Calc byte
        for i in range (0, 8):
            bt <<= 1;
            pix = raw[idx]
            idx += 1
            if (pix != cback):
                bt |= 1
        data.append(bt)
    return data

def extractpatraw (idx, raw, width, height):
    
    # Calc offsets
    w8 = width >> 3
    h8 = height >> 3
    y = int (idx / w8)
    x = int (idx % w8)

    offset = int( (y * width * 8) + x * 8)
    
    data = []


    # 8 x 8 bytes
    for y in range (0,8):
        for x in range (0, 8):
            byte = raw[offset + (y * width) + x]
            data.append(byte)

    return data

def rawtotmspat (raw, width, height, patterns, back):

    numpat = (width >> 3) * (height >> 3)
    print("Patterns Max Lenght: ",numpat)

    if ((patterns != 0) and (patterns <= numpat)):
        numpat = patterns

    print("Number of patterns to extract: ",numpat)
         
    tmsdata = [] 
    for idx in range (0, numpat):
        patraw = extractpatraw(idx, raw, width, height)
        patdat = rawpat2dat(patraw, back) 
        for byte in patdat:
            tmsdata.append(byte)

    return tmsdata


# -----------------------------------------------------------------------------
# TMS Color
# -----------------------------------------------------------------------------


def raw8pix2byte (raw, back):
    
    two = []
    for col in raw:
        if (col in two) == False:
            two.append(col)

    cback = calcbackcolor(raw, back)


    byte = cback << 4 | cback;

    if (len (two) == 2):
        byte = byte & 0x0F
        cfor = two[1]
        if (two[1] == cback):
            cfor = two[0]
        byte = byte | (cfor << 4)

    byte = byte & 0xFF
    return byte    



def rawcol2dat (raw, back):
    data = []
    idx = 0;
    for byte in range (0, 8):
        colors = []
        for i in range (0, 8):
            pix = raw[idx]
            idx += 1
            colors.append(pix);
        bt = raw8pix2byte(colors, back);
        data.append(bt)
    return data



def rawtotmscol (raw, width, height, patterns, back):

    numpat = (width >> 3) * (height >> 3)
    print("Patterns Max Lenght: ",numpat)

    if ((patterns != 0) and (patterns <= numpat)):
        numpat = patterns

    print("Number of patterns to extract: ",numpat)
         
    tmsdata = [] 
    for idx in range (0, numpat):
        colraw = extractpatraw(idx, raw, width, height)
        coldat = rawcol2dat(colraw, back) 
        for byte in coldat:
            tmsdata.append(byte)

    return tmsdata

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
    outputnamecol = outputname + ".COL"
    print("Input:  ", filename)
    print("Output Pattern: ", outputnamepat)
    print("Output Color: ", outputnamecol)
    

    backcolor = -1;
    if (len(args) >= 4):
        backcolor = int(args[3])
        print("Back Color: ", backcolor)

    lenght = 0;
    if (len(args) >= 5):
        lenght = int(args[4])
        print("Number of patterns: ", lenght)

    # Read and process 

    img = Image.open(filename)
    if img.mode != 'P':
        print("ERROR: Not indexed image!!")
        exit(-1)
    w, h = img.size
    print("Width : ", w)
    print("Height: ", h)

    if (w < 16):
        print("ERROR: Min Width = 16!!!!")
        exit(-1)

    if (h < 16):
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

    # Create pattern data
    patdata = rawtotmspat(rawdata, w, h, lenght, backcolor)
    writefile (outputnamepat, patdata);

    # Create color data
    coldata = rawtotmscol(rawdata, w, h, lenght, backcolor);
    writefile (outputnamecol, coldata);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



