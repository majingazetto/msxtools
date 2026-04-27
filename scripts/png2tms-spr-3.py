#!/usr/bin/env python3

# **********************************************
# * PNG2TMS Tool                               *
# * Convert PNG file to TMS sprite data        *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNG2TMS-SPR Tool"
VERSION = "1.0"
COPYRIGHT = "2016"
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
    print("     number of sprites (optional): number of sprites to extract.")
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
# TMS Sprite
# -----------------------------------------------------------------------------

def rawspr2dat (raw):
    data = []
    idx = 0;
    for byte in range (0, 32):
        bt = 0;
        for i in range (0, 8):
            bt <<= 1;
            pix = raw[idx]
            idx += 1
            if (pix != 1):
                bt |= 1
        data.append(bt)
    return data

def extractsprraw (idx, raw, width, height):
    
    # Calc offsets
    w16 = width >> 4
    h16 = height >> 4
    y = idx // w16
    x = idx % w16
    offset = int ((y * width * 16) + x * 16)
    
    data = []

    # up-left + down-left
    for y in range (0,16):
        for x in range (0, 8):
            i_idx = int(offset + (y * width) + x)
            byte = raw[i_idx]
            data.append(byte)

    # up-right + down-right
    for y in range (0,16):
        for x in range (0, 8):
            i_idx = int(offset + (y * width) + x + 8)
            byte = raw[i_idx]
            data.append(byte)


    return data

def rawtotmsspr (raw, width, height, sprites):

    numspr = (width >> 4) * (height >> 4)
    print("Sprite Max Lenght: ",numspr)

    if ((sprites != 0) and (sprites <= numspr)):
        numspr = sprites

    print("Number of sprites to extract: ",numspr)
         
    tmsdata = [] 
    for idx in range (0, numspr):
        sprraw = extractsprraw(idx, raw, width, height)
        sprdat = rawspr2dat(sprraw) 
        for byte in sprdat:
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
    
    print("Input:  ", filename)
    print("Output: ", outputname)
    
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

    # Create sprite data
    sprdata = rawtotmsspr(rawdata, w, h, lenght)
    writefile (outputname, sprdata);

    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



