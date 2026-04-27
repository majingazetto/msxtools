#!/usr/bin/env python3

# ***************************************************
# * PNG2MODE2 Tool                                  *
# * Convert PNG file data to Sprite MSX Mode 2 Data *
# ***************************************************


import array, struct, sys, io, os, string, math
from PIL import Image

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNG2MODE2 Tool"
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
    print("     input:    indexed PNG File 16 colours with specific format.")
    print("     output:   Basename output.")
    print("     size:     Number of Sprites to process.")
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
# PNG
# -----------------------------------------------------------------------------

def pixelstoraw (pixels):
    raw = []
    for row in pixels:
        for i in range(0, len(row)):
            raw.append(row[i])
    return raw



# -----------------------------------------------------------------------------
# Mode 2
# -----------------------------------------------------------------------------



def getrawspridx(raw, idx):

    data = []
    x = (idx & 7) * 16
    y = ((idx & 0xF8) << 1) 
    offset = (y << 8) + x

    for y in range(16):
        for x in range(16):
            b = raw[offset + (y << 8) + x]
            data.append(b)
    
    return data


def getrawpalidx(raw, idx):
   
    data = []
    x = ((idx & 7) * 8) + 128
    y = ((idx & 0xF8) << 1) 
    offset = (y << 8) + x

    for y in range(16):
        for x in range(8):
            b = raw[offset + (y << 8) + x]
            if ((x & 1) == 0):
                #print "Pal[%i] Scan[%x]: %x " % (idx, y, b)
                data.append(b)

    return data



def getscandata(sprraw, sprpal, idx):
    
    data = []
    pal0 = sprpal[(idx * 4) + 1]
    pal1 = sprpal[(idx * 4) + 2]
    pal2 = sprpal[(idx * 4) + 3]
    
    #print pal0,pal1,pal2 
    b0 = 0
    b1 = 0
    p0 = 0x20 | (pal0 & 0xF)
    p1 = 0x60 | (pal1 & 0xF)

    for i in range(16):
        px = sprraw[(idx * 16) + i]
        if (px != 0):
            
            if (px == pal0):
                b0 = (b0 << 1) | 1
                b1 = (b1 << 1)

            if (px == pal1):
                b0 = (b0 << 1)
                b1 = (b1 << 1) | 1
            
            if (px == pal2):
                b0 = (b0 << 1) | 1
                b1 = (b1 << 1) | 1
                #p1 = p1 | 0x40

        else:
            b0 = b0 << 1
            b1 = b1 << 1


    data.append(b0 & 0xFFFF)
    data.append(b1 & 0xFFFF)
    data.append(p0 & 0xFFFF)
    data.append(p1 & 0xFFFF)
    return data
    

def getscandatasingle(sprraw, idx):
    
    data = []
    
    bit = 0

    for i in range(16):
        px = sprraw[(idx * 16) + i]
        if (px != 0):
            bit = (bit << 1) | 1         
        else:
            bit = (bit << 1)


    data.append(bit & 0xFFFF)
    return data

def rawscantomode2 (raw):
    
    data = []
    
    tmp00 = []
    tmp01 = []
    tmp02 = []
    tmp03 = []

    tmp10 = []
    tmp11 = []
    tmp12 = []
    tmp13 = []

    
    # Reorder data

    for i in range(8):
        scan = raw[i]
        tmp00.append( (scan[0] >> 8) & 0xFF)
        tmp02.append(scan[0] & 0xFF)
        tmp10.append( (scan[1] >> 8) & 0xFF)
        tmp12.append(scan[1] & 0xFF)
        scan = raw[i + 8]
        tmp01.append( (scan[0] >> 8) & 0xFF)
        tmp03.append(scan[0] & 0xFF)
        tmp11.append( (scan[1] >> 8) & 0xFF)
        tmp13.append(scan[1] & 0xFF)


    data = appenddata(data, tmp00)
    data = appenddata(data, tmp01)
    data = appenddata(data, tmp02)
    data = appenddata(data, tmp03)
    data = appenddata(data, tmp10)
    data = appenddata(data, tmp11)
    data = appenddata(data, tmp12)
    data = appenddata(data, tmp13)

    return data


def rawscantomode2single (raw):
    
    data = []
    
    tmp00 = []
    tmp01 = []
    tmp02 = []
    tmp03 = []

    
    # Reorder data

    for i in range(8):
        scan = raw[i]
        tmp00.append( (scan[0] >> 8) & 0xFF)
        tmp02.append(scan[0] & 0xFF)
        scan = raw[i + 8]
        tmp01.append( (scan[0] >> 8) & 0xFF)
        tmp03.append(scan[0] & 0xFF)


    data = appenddata(data, tmp00)
    data = appenddata(data, tmp01)
    data = appenddata(data, tmp02)
    data = appenddata(data, tmp03)
    return data


def getsprdata(raw, idx):

    sprdata = {'sgt': [], 'spl' : [], 'sg1': []}
    sprraw = getrawspridx(raw, idx)
    sprpal = getrawpalidx(raw, idx)

    data = []
    data1 = []
    for y in range(16):
        scan = getscandata(sprraw, sprpal, y)
        data.append(scan)
        scan = getscandatasingle(sprraw, y)
        data1.append(scan)

    
    datasgt = rawscantomode2(data)
    sprdata['sgt'] = datasgt

    datasg1 = rawscantomode2single(data1)
    sprdata['sg1'] = datasg1
    
    pal0 = []
    pal1 = []
    for i in range (16):
       scan = data[i]
       pal0.append(scan[2])
       pal1.append(scan[3])

    dataspl = []
    dataspl = appenddata(dataspl, pal0)
    dataspl = appenddata(dataspl, pal1)
    
    sprdata['spl'] = dataspl
    return sprdata



def getmode2data(raw, size):
    
    sprdata = {'sgt': [], 'spl' : [], 'sg1':[]}
    
    sgt = []
    spl = []
    sg1 = []
    for idx in range(size):
        data = getsprdata(raw, idx)
        sgt = appenddata(sgt, data['sgt']) 
        spl = appenddata(spl, data['spl']) 
        sg1 = appenddata(sg1, data['sg1']) 
    
    sprdata['sgt'] = sgt
    sprdata['sg1'] = sg1
    sprdata['spl'] = spl
    return sprdata


# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 4):
        usage(args[0])
        exit (-1)

    filename = args[1]
    outputname = args[2]
    size = int(args[3])

    outputnameSGT = outputname + ".SGT"
    outputnameSG1 = outputname + ".SG1"
    outputnameSPL = outputname + ".SPL"
    print("Input:  ", filename)
    print("Output SGT: ", outputnameSGT)
    print("Output SPL: ", outputnameSPL)
    print("Output SG1: ", outputnameSG1)
    print("Size: ", size)

    # Read and process 

    img = Image.open(filename)
    if img.mode != 'P':
        print("ERROR: Not indexed image!!")
        exit(-1)
    w, h = img.size

    if (w < 256):
        print("ERROR: Width != 256!!!!")
        exit(-1)

    if (h < 16):
        print("ERROR: Min Height = 16!!!!")
        exit(-1)
    if (size <= 0):
        print("ERROR: Size can't be 0!!!")
        exit(-1)

    if (( (((size - 1) >> 3) + 1) * 16) > h):
        print("ERROR: PGN it's small for number of sprites required...")
        exit(-1)

    palette_mode, palette_data = img.palette.getdata()
    stride = len(palette_mode)
    n_colors = len(palette_data) // stride
    palette = [(palette_data[i*stride], palette_data[i*stride+1], palette_data[i*stride+2]) for i in range(n_colors)]

    if len(palette) < 16:
        print("Warning: < 16 colour image!!")

    raw_pixels = img.tobytes()
    pixel_list = [list(raw_pixels[y*w:(y+1)*w]) for y in range(h)]

    # list pixels to raw data
    rawdata = pixelstoraw(pixel_list)




    # rawdata to mode 2 spr and pal data 
    sprdata = getmode2data(rawdata, size); 

    # Write files
    writefile (outputnameSGT, sprdata['sgt']);
    writefile (outputnameSG1, sprdata['sg1']);
    writefile (outputnameSPL, sprdata['spl']);


    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



