#!/usr/bin/env python3

# **********************************************
# * PNG2SR8 Tool                               *
# * Convert PNG file to SR8 (RGB 332) raw data *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNG2SR8 Tool"
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
    print("     input:    RGB332 indexed PNG File.")
    print("     output:   Converted Raw data file.")
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
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 3):
        usage(args[0])
        exit (-1)

    filename = args[1]
    outputname = args[2]
    
    outputnamepat = outputname + ".332"
    print("Input:  ", filename)
    print("Output: ", outputnamepat)
    
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

    if len(palette) > 256:
        print("Warning: > 256 colour image!!")

    raw_pixels = img.tobytes()
    pixel_list = [list(raw_pixels[y*w:(y+1)*w]) for y in range(h)]

    # list pixels to raw data
    rawdata = pixelstoraw(pixel_list)

    # Create pattern data
    writefile (outputnamepat, rawdata);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



