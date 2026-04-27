#!/usr/bin/env python3

# **********************************************
# * PNG2SR5 Tool                               *
# * Convert PNG file to SR5 file               *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNGPAL Tool"
VERSION = "1.0"
COPYRIGHT = "2016 - 2019"
HEADEROFFSET = 7



# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Ramones' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:    Indexed PNG File.")
    print("     sr5pal:   9938 SR5 Pal file.")

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

    filename = args[1]
    pl5file = args[2]


    print("Input:  ", filename)
    print("SR5 PAL file: ", pl5file)

    # Read and process 

    img = Image.open(filename)
    if img.mode != 'P':
        print("ERROR: Not indexed image!!")
        exit(-1)
    w, h = img.size

    print("Width : ", w)
    print("Height: ", h)

    palette_mode, palette_data = img.palette.getdata()
    stride = len(palette_mode)
    n_colors = len(palette_data) // stride
    palette = [(palette_data[i*stride], palette_data[i*stride+1], palette_data[i*stride+2]) for i in range(n_colors)]

    print("Palette: ", palette)

    
    # palette to RB G
    paldata = paltopl5(palette)
    # Save pal data
    writefile (pl5file, paldata);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



