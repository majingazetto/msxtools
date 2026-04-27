#!/usr/bin/env python3

# **********************************************
# * PNG8TOPS Tool                              *
# * PNG Pat 8x8 PGT to Pat SxS map             *
# **********************************************


import array, struct, sys, io, os, string, math
from PIL import Image



# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "PNG8TOPS Tool"
VERSION = "1.0"
COPYRIGHT = "2019"
HEADEROFFSET = 7



# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Armando Perez Abad' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s layout pgt output\n" % execfile)
    print("     layout          : indexed PNG File with map.")
    print("     pgt             : Pattern Generator Table (PNG indexed).")
    print("     pat size        : Pattern size")
    print("     num patterns    : number of patterns to extract")
    print("     pgt patterns    : number of pgt patterns")
    print("     output          : output base name (.Z8A, .MAP will be added)")
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
# Map 
# -----------------------------------------------------------------------------


def extractmaptable (map, wm, hm, pgt, wp, hp, patsize, pgtpat, numpat):
        
    # pgt to pat8array
        
    pgt8 = pgttopat8(pgt, wp, hp, pgtpat)

    nametbl = []
    mappat = (wm / patsize ) * (hm / patsize)
    print("Map Patterns Max Lenght: ",mappat)
    
    if (mappat < numpat):
        print("ERROR: numpat > mappat")
        exit(-1)

    wsize = wm / patsize
    hsize = hm / patsize
    for idx in range (0, numpat):
        ymeta = (idx / wsize) * patsize
        xmeta = (idx % wsize) * patsize
        offsetmeta = (ymeta * wm) + xmeta
        metaraw = extractmetraw(map, offsetmeta, wm, patsize) 
        meta8 = metatopat8(metaraw, patsize)
        #
        metamap = []
        for metidx in range (0, len(meta8)):
            rawpat = meta8[metidx]
            midx = -1
            for pidx in range (0, len(pgt8)):
                rawpgt = pgt8[pidx]
                if (rawpgt == rawpat):
                    midx = pidx
                    break 
            if (midx == -1):
                offex, offey = getoffsetfrompatidx(metidx, patsize)
                xerror = xmeta + offex
                yerror = ymeta + offey
                print("Pattern not found: metaidx = %i pat8idx = %i xmeta = %i ymeta = %i xpat = %i ypat = %i" % (idx, metidx, xmeta, ymeta, xerror , yerror))
                midx = 0
            metamap.append(midx)

        nametbl.append(metamap)

    return nametbl


def extractmetraw (map, offset, wm, size):
    raw=[]
    for y in range(0, size):
        yoff = (y * wm) + offset
        for x in range (0, size):
            p = map[yoff + x]
            raw.append(p)
            
    return raw


def metatopat8 (raw, patsize):
    pat8array = []
    for y in range (0, patsize >> 3):
        offy = y * (patsize << 3)
        for x in range (0, patsize >> 3):
            offx = x << 3 
            pat8 = []
            for ypat in range (0, 8):
                offscan = ypat * patsize 
                for xpat in range (0, 8):
                    offset = offy + offx + offscan + xpat
                    p = raw[offset]
                    pat8.append(p)
            pat8array.append(pat8)
    return pat8array

def pgttopat8 (raw, w, h, numpat):
    wsize = w >> 3
    hsize = h >> 3
    pat8array = []
    for idx in range (0, numpat):
        y = (idx / wsize) << 3
        x = (idx % wsize) << 3
        offset = (y * w) + x
        data = []
        for y in range (0,8):
            for x in range (0, 8):
                byte = raw[offset + (y * w) + x]
                data.append(byte)
        pat8array.append(data) 
    return pat8array


def getoffsetfrompatidx (patidx, size):

    offx = 0
    offy = 0
    npside = size >> 3 
    
    offy = (patidx / npside) << 3
    offx = (patidx % npside) << 3
    

    return (offx, offy)


# -----------------------------------------------------------------------------
# MAP TO FILES
# -----------------------------------------------------------------------------

def maptbltobin (tbl):
    bintbl = []
    for idx in range (0, len(tbl)):
            metamap = tbl[idx]
            for midx in range (0, len(metamap)):
                bintbl.append(metamap[midx])

    return bintbl

# -----------------------------------------------------------------------------
# Main program
# -----------------------------------------------------------------------------

def main(args):
    
    logo()
   
    if (len(args) < 7):
        usage(args[0])
        exit (-1)

    mapname = args[1]
    pgtname = args[2]
    patsize = int(args[3])
    numpat = int(args[4])
    pgtpat = int(args[5])
    baseoutput = args[6]
    sourceoutput = baseoutput + ".Z8A"
    binoutput = baseoutput + ".MAP"

    print("Map file: ",mapname) 
    print("PGT file: ", pgtname)
    print("Pattern size: ", patsize)
    print("Number of pat: ", numpat)
    print("Number of pgt pat: ", pgtpat)
    print("Base output: ", baseoutput)
    print("--------------")
    print("Source output: ", sourceoutput)
    print("Binary output: ", binoutput)
    print("--------------")
    
    # Read and process 

    mapimg = Image.open(mapname)
    if mapimg.mode != 'P':
        print("ERROR: Not indexed image (map)!!")
        exit(-1)
    mw, mh = mapimg.size

    pgtimg = Image.open(pgtname)
    if pgtimg.mode != 'P':
        print("ERROR: Not indexed image (pgt)!!")
        exit(-1)
    pw, ph = pgtimg.size

    print("Map Width : ", mw)
    print("Map Height: ", mh)
    print("PGT Width : ", pw)
    print("PGT Height: ", ph)
    print("--------------")

    if (mw < patsize):
        print("ERROR: Min Width < ", patsize)
        exit(-1)

    if (mh < patsize):
        print("ERROR: Min Height < ", patsize)
        exit(-1)

    ppalette_mode, ppalette_data = pgtimg.palette.getdata()
    pstride = len(ppalette_mode)
    ppalette = [(ppalette_data[i*pstride], ppalette_data[i*pstride+1], ppalette_data[i*pstride+2]) for i in range(len(ppalette_data) // pstride)]

    mpalette_mode, mpalette_data = mapimg.palette.getdata()
    mstride = len(mpalette_mode)
    mpalette = [(mpalette_data[i*mstride], mpalette_data[i*mstride+1], mpalette_data[i*mstride+2]) for i in range(len(mpalette_data) // mstride)]

    print("Pal Map size: ", len(mpalette))
    print("Pal PGT size: ", len(ppalette))

    if len(ppalette) != len(mpalette):
        print("ERROR: Palette size differs")
        exit(-1)

    map_raw = mapimg.tobytes()
    mapdata = pixelstoraw([list(map_raw[y*mw:(y+1)*mw]) for y in range(mh)])
    pgt_raw = pgtimg.tobytes()
    pgtdata = pixelstoraw([list(pgt_raw[y*pw:(y+1)*pw]) for y in range(ph)])

    maptbl = extractmaptable(mapdata, mw, mh, pgtdata, pw, ph, patsize, pgtpat, numpat)
    bintbl = maptbltobin(maptbl)
    writefile (binoutput, bintbl);

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    





