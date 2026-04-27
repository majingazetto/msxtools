#!/usr/bin/env python3

# **********************************************
# * PNGTMSMAP Tool                             *
# * Map Layout PNG                             *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNGTMS-MAP Tool"
VERSION = "1.0"
COPYRIGHT = "2016"
HEADEROFFSET = 7



# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Ramones' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s layout pgt output\n" % execfile)
    print("     layout: 4 bit indexed PNG File with map.")
    print("     pgt   : Pattern Generator Table (PNG 4 bit).")
    print("     output: 768 bytes PNG Nametable.")
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


def extractpatraw (idx, raw, width, height):
    
    # Calc offsets
    w8 = width >> 3
    h8 = height >> 3
    y = int(idx / w8)
    x = int(idx % w8)
    offset = int ((y * width * 8) + x * 8)
    
    data = []

    # 8 x 8 bytes
    for y in range (0,8):
        for x in range (0, 8):
            byte = raw[offset + (y * width) + x]
            data.append(byte)

    return data


# -----------------------------------------------------------------------------
# Process
# ------------------------------------------------------------------------------



def getnametblindex (mapraw, pgt, wp, hp):
    index = -1
    pgtpat = (wp >> 3) * (hp >> 3)
    for idx in range (0, pgtpat):
        pgtraw = extractpatraw (idx, pgt, wp, hp)
        if (mapraw == pgtraw):
            return idx

    return index




def extractnametable (map, wm, hm, pgt, wp, hp):
    nametbl = []
    pgtpat = (wp >> 3) * (hp >> 3)
    print("PGT Patterns Max Lenght: ",pgtpat)
    mappat = (wm >> 3) * (hm >> 3)
    print("Layout Patterns Max Lenght: ",mappat)

    for idx in range (0, mappat):
        w8 = wm >> 3
        h8 = hm >> 3
        y_grid = int(idx / w8)
        x_grid = int(idx % w8)
        mapraw = extractpatraw (idx, map, wm, hm)
        attindex = getnametblindex(mapraw, pgt, wp, hp)
        if (attindex == -1):
            # Sample first few bytes of the failing pattern for comparison
            sample = mapraw[:8]
            print("Pattern not found: idx = %i (Grid X=%i, Y=%i) Px_Coord(x=%i, y=%i) Sample=%s" % ( idx, x_grid, y_grid, x_grid * 8, y_grid * 8, str(sample)))
            attindex = 0

        nametbl.append(attindex & 0xFF)

    
    return nametbl




# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 4):
        usage(args[0])
        exit (-1)

    mapname = args[1]   
    pgtname = args[2]
    nametblname = args[3]
    
    print("Map file:  ", mapname) 
    print("PGT file: ",  pgtname)
    print("Name Table file: ", nametblname) 
    

    # Read and process 

    mapimg = Image.open(mapname)
    if mapimg.mode != 'P':
        print("ERROR: Not indexed image (map)!!")
        exit(-1)
    w, h = mapimg.size
    print("Map Width : ", w)
    print("Map Height: ", h)

    if (w < 16):
        print("ERROR: Min Width = 8!!!!")
        exit(-1)

    if (h < 16):
        print("ERROR: Min Height = 8!!!!")
        exit(-1)

    palette_mode, palette_data = mapimg.palette.getdata()
    stride = len(palette_mode)
    n_colors = len(palette_data) // stride
    palette = [(palette_data[i*stride], palette_data[i*stride+1], palette_data[i*stride+2]) for i in range(n_colors)]

    if len(palette) > 16:
        print("Warning: > 16 colour image!!")

    pgtimg = Image.open(pgtname)
    if pgtimg.mode != 'P':
        print("ERROR: Not indexed image (pgt)!!")
        exit(-1)
    wp, hp = pgtimg.size
    print("Pgt Width : ", wp)
    print("pgt Height: ", hp)

    if (wp < 8):
        print("ERROR: Min Width = 8!!!!")
        exit(-1)

    if (hp < 8):
        print("ERROR: Min Height = 8!!!!")
        exit(-1)

    ppalette_mode, ppalette_data = pgtimg.palette.getdata()
    pstride = len(ppalette_mode)
    pn_colors = len(ppalette_data) // pstride
    ppalette = [(ppalette_data[i*pstride], ppalette_data[i*pstride+1], ppalette_data[i*pstride+2]) for i in range(pn_colors)]

    if len(ppalette) > 16:
        print("Warning: > 16 colour image!!")

    map_raw = mapimg.tobytes()
    mapdata = pixelstoraw([list(map_raw[y*w:(y+1)*w]) for y in range(h)])
    pgt_raw = pgtimg.tobytes()
    pgtdata = pixelstoraw([list(pgt_raw[y*wp:(y+1)*wp]) for y in range(hp)])

    nametbl = extractnametable(mapdata, w, h, pgtdata, wp, hp)
    writefile (nametblname, nametbl);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    





