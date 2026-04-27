#!/usr/bin/env python3

# **********************************************
# * PNG2SR5 Tool                               *
# * Convert PNG file to SR5 raw data           *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNG2SR5 Tool"
VERSION = "1.0"
COPYRIGHT = "2019"
HEADEROFFSET = 7



# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Armando Perez Abad' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:    Indexed 8 bit (8 bit colormap) PNG File.")
    print("     output:   Converted Raw data file. (RA5, PA5, SR5, PL5)")
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
# SR5
# -----------------------------------------------------------------------------

def rawtosr5 (raw):
    sr5 = []

    # Header

    sr5.append(0xFE)
    sr5.append(0x00)
    sr5.append(0x00)
    sr5.append(0x00)
    sr5.append(0x6A)
    sr5.append(0x00)
    sr5.append(0x00)

    # Raw Data
    
    cnt = 128 * 212

    for i in range(0, len(raw)):
        sr5.append(raw[i])
        cnt = cnt - 1
        if (cnt == 0):
            break

    if (cnt != 0):
        for i in range (0, cnt):
            sr5.append(0)

    return sr5
    

# -----------------------------------------------------------------------------
# PNG
# -----------------------------------------------------------------------------

def pixelstoraw (pixels):
    raw = []
    for row in pixels:
        b = 0
        for i in range(0, len(row)):

            if (i & 1):
                b = b | row[i]
                raw.append(b)
            else:
                b = row[i] << 4 
            
    return raw


def paltopl5 (palette):

    pal = [];
        
    for i in range(0, len(palette)):
        color = palette[i]
        r = color[0]
        g = color[1]
        b = color[2]

        # Quick (bad) conversion
        
        r = (r >> 1) & 0x70
        g = (g >> 5) & 7
        b = (b >> 5) & 7
        palRB = r | b
        palG = g
        
        # add to table 
        pal.append(palRB)
        pal.append(palG)
     
    return pal

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

    outputnamepat = outputname + ".RA5"
    print("Output RAW: ", outputnamepat)
    outputnamepal = outputname + ".PA5"
    print("Output PAL: ", outputnamepal)
    outputnamesr5 = outputname + ".SR5"
    print("Output SR5: ", outputnamesr5)
    outputnamepl5 = outputname + ".PL5"
    print("Output PL5: ", outputnamepl5)


    
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
    stride = len(palette_mode)   # 3 for RGB, 4 for RGBA
    n_colors = len(palette_data) // stride
    palette = [(palette_data[i*stride], palette_data[i*stride+1], palette_data[i*stride+2]) for i in range(n_colors)]

    if len(palette) < 16:
        print("Warning: < 16 colour image!!")

    raw_pixels = img.tobytes()
    pixel_list = [list(raw_pixels[y*w:(y+1)*w]) for y in range(h)]

    
    # palette to RB G
    paldata = paltopl5(palette)

    # list pixels to raw data
    rawdata = pixelstoraw(pixel_list)
    
    # rawdata to sr5
    sr5data = rawtosr5(rawdata)

    # Save pattern data
    writefile (outputnamepat, rawdata);

    # Save SR5 data
    writefile (outputnamesr5, sr5data);

    # Save pal data
    writefile (outputnamepal, paldata);
    writefile (outputnamepl5, paldata);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



