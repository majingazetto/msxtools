#!/usr/bin/env python3

# **********************************************
# * Z80PRE Tool                                *
# * Convert Z80 ASM File to "modern" Z80 ASM   *
# **********************************************


import array, struct, sys, io, os, string

# ---------------------
# Constant DEFINES
# ---------------------

PROGRAMNAME = "Z80PRE Tool"
VERSION = "1.0"
COPYRIGHT = "2012"
HEADEROFFSET = 7


# -----------------------------------------------------------------------------
# Logo, usage and help
# -----------------------------------------------------------------------------

def logo():
    print('%s v%s (c) %s Kralizec' % (PROGRAMNAME, VERSION, COPYRIGHT))


def usage(execfile):
    print("\nUsage: %s input output\n" % execfile)
    print("     input:    Z80 Assembler File.")
    print("     output:   Converted Z80 Assembler File")
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
# Parse
# -----------------------------------------------------------------------------

def parseline (line):

    parsed = ""
   
    # clean * to end
    parsed = cleancomment(line, "*")
    # clean * to end
    parsed = cleancomment(parsed, "-")
    # clean ; to end
    parsed = cleancommentall(parsed, ";")
    # clean last comment 
    #parsed = cleanlastcomment(parsed)
    # replace locale labels
    parsed = replacelocale(parsed,"$",".")
    # clean \n and add \n
    parsed = parsed.replace("\n","")
    parsed += "\n" 

    return parsed

# Clean * Comment
def cleancomment(line, commentchar):
    
    index = line.find(commentchar)
    if (index == -1):
        return line

    # Check if is first character
    
    if (index == 0):
        return "";

    for i in range (index):
        c = line[i]
        if ((c == ' ') or (c == "\t")):
            continue
        return line

    return line[:index]

# Clean * Comment
def cleancommentall(line, commentchar):
    
    index = line.find(commentchar)
    if (index == -1):
        return line

    # Check if is first character
    
    if (index == 0):
        return "";

    return line[:index]

# Clean last comment
def cleanlastcomment(line):

    if (len(line) < 64):
        return line
    
    return line[:64] 


def replacelocale (line, char, to):
    
    for i in range(len(line)):
        c = line[i]
        if (c == char):
          if ((i + 1) < (len(line) - 1)):
              ci = line[i + 1]
              if ((ci != ' ') and (ci != ',')):
                  line = line.replace(char, to, 1)

    return line

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

    # Read and process 
    string = readstringfile(filename)
    splitstring = string.split("\n")    
    
    parsed = ""
    for line in splitstring:
        pline = parseline(line)
        parsed += pline
    
    writestringfile(outputname, parsed)

    print("Ok. Bye!")
    exit(0)

# ---------------------
# Call to Main
# ---------------------

main(sys.argv)    



