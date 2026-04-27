#!/usr/local/bin/rebol


REBOL 
[
    Author: "Armando Perez Ramones"
    File: %sr5pal2db.r
    Date: 17-Jan-2010
    Title: "PL5 (SR5 MSX Palette File) to DB"
]


; *****************************************************
; *               Const / Vars                        *
; *****************************************************

VERSION: "1.0"
EXT:   ".ASC"


; ----------------------------------------------------
; Basename
; Extract Basename of file
; ----------------------------------------------------

Basename: function [ filename [string!] ]
[ bname [string!] ext [string!] ]
[
    bname: copy/deep ""
    bname: split-path (to-file filename)
    bname: to-string bname/2
    ext: none
    ext: find/reverse (tail bname) "."
    if (ext <> none)
    [
        bname: copy/deep/part (head bname) ext
    ]
    bname: to-string bname
    bname
]





; -----------------------------------------------------
; ExitError
; Exit to OS with -1  to OS
; -----------------------------------------------------

ExitError: func []
[
    print ""
    waitKey
    quit/return -1
]

; -----------------------------------------------------
; ExitOK
; Exito to OS with return 0 and All Done MSG
; -----------------------------------------------------

ExitOK: func []
[
    print ""
    print "All Done"
    print ""
    waitKey
    quit/return 0
]

; -----------------------------------------------------
; Error
; Print string and exit program
; In: block! error
; Out: none
; -----------------------------------------------------

Error: func [ errortxt [ block! ] ]
[
    print ""
    print errortxt
    ExitError
]

; -----------------------------------------------------
; Logo
; Prints logo
; In/Out: (none)
; -----------------------------------------------------

Logo: func []
[
    print ["SR5pal2db v." VERSION]
    print ["PL5 file to DB asc file"]
    print ""
]




; -----------------------------------------------------
; Usage
; prints usage
; In/Out: (none)
; -----------------------------------------------------

Usage: func []
[
    print ["Usage: rebol --quiet --secure allow --script sr5paldb.r file palnumber (0-7) numberofpals (1-8)"]
    print ["    file: PL5 file"]
    print ["    palnumber: (default 0) number of PL5 palette (0-7)"]
    print ["    numberofpals: (default 1) number of palettes to write in file"]
    print ""
]

; -----------------------------------------------------
; ExitUsage
; Exit to OS showing Usage
; Exit with -1
; -----------------------------------------------------

ExitUsage: func []
[
    Usage
    ExitError
]


; -----------------------------------------------------
; checkWindows
; Check windows system
; -----------------------------------------------------

checkWindows: function[]
[ isWindows ] 
[
    isWindows: false 
    if (((fourth system/version) = 3) and ((fifth system/version) = 1))
    [
        isWindows: true
    ]
    isWindows
]


; ------------------------------------------------------
; waitKey if is Windows
; ------------------------------------------------------

waitKey: function []
[  ] 
[
    
    if (checkWindows = true)
    [
        system/console/break: false
        wait cons
        system/console/break: true
    ]
]



; *****************************************************
; *                 create DB                         *
; *****************************************************

createDBheader: function [ dbdata [string! ] ]
[]
[
    ; append header

    append dbdata  rejoin [ "; ------------------------------------^/" ]  
    append dbdata  rejoin [ "; Automatic file created by SR5PAL2DB ^/" ] 
    append dbdata  rejoin [ "; Do not edit!!!^/"] 
    append dbdata  rejoin [ "; ------------------------------------^/^/" ] 
]


createDBpal: function [ dbdata [string!] rawdata[binary!] palnumber[integer!] numberofpals [integer!] ]
[ praw num cnt ]
[
    ; Write info

    append dbdata rejoin [ "; MSX Pal Data ^/^/" ]
    ; prepare rawdata pointer
    rawdata: head rawdata
    praw:  skip rawdata (32 * palnumber)  
    cnt: 0
    for num 1 (numberofpals * 32) 1
    [
        hexval: copy/part tail (to-hex to-integer to-char (first praw)) -2
        if (cnt = 0)
        [
            append dbdata rejoin [ "        db    "]
        ]
        hexval: rejoin [ "0" hexval "h" ]
        cnt: cnt + 1
        either (cnt =  16)
        [
            cnt: 0
            hexval: rejoin [ hexval "^/" ]
        ]
        [
            hexval: rejoin [ hexval "," ]
        ]
        append dbdata hexval
        praw: next praw
    ]
    append dbdata "^/"

]


createDBpalSMS: function [ dbdata [string!] rawdata[binary!] palnumber[integer!] numberofpals [integer!] ]
[ praw num cnt smscolor r g b rc gc bc]
[
    convtable: [0 0 1 1 2 2 3 3]

    ; Write info

    append dbdata rejoin [ "; SMS Pal Data ^/^/" ]
    ; prepare rawdata pointer
    rawdata: head rawdata
    praw:  skip rawdata (32 * palnumber)  
    cnt: 0
    for num 1 (numberofpals * 32) 2
    [
        ; Create color from RBG
        r: to-integer ((first praw) / 16)
        b: to-integer to-binary to-char (first praw) and 15 
        g: to-integer to-binary to-char (second praw) and 15 
        rc: (pick convtable r + 1) 
        gc: (pick convtable g + 1) * 4
        bc: (pick convtable b + 1) * 16


        smscolor: bc + gc + rc

        hexval: copy/part tail (to-hex to-integer to-char (smscolor)) -2
        if (cnt = 0)
        [
            append dbdata rejoin [ "        db    "]
        ]
        hexval: rejoin [ "0" hexval "h" ]
        cnt: cnt + 1
        either (cnt =  16)
        [
            cnt: 0
            hexval: rejoin [ hexval "^/" ]
        ]
        [
            hexval: rejoin [ hexval "," ]
        ]
        append dbdata hexval
        praw: next praw
        praw: next praw
    ]
    append dbdata "^/"

]


saveFile: function [ filename [string!] data [string!] ]
[]
[

    if (error? try [ write to-file filename data ] ) [Error ["ERROR: Can't write" filename ] ]
]


; *****************************************************
; *                 Main Code                         *
; *****************************************************

if not value? 'cons [cons: open/binary [scheme: 'console]]

; Print Logo

Logo


;  Check arguments < 1 

if ( system/options/args = none )
[
    ; Show Usage and exit
    ExitUsage
]

; Separate argument and command

args: system/options/args
file: args/1
palnumber: 0

if ((length? args) > 1)
[
    if (error? try [ palnumber: to-integer args/2 ]) [ palnumber: 0 ]
    if ((palnumber < 0) or (palnumber > 7)) [ ExitUsage ]
]

numberofpals: 1

if ((length? args) > 2)
[

    if (error? try [ numberofpals: to-integer args/3 ]) [ numberofpals: 1 ]
    if ((numberofpals < 1) or (palnumber > 8)) [ ExitUsage ]
    ; Adjust number of pals
    if ( numberofpals > (8 - palnumber) )
    [
        numberofpals:  8 - palnumber;
    ]
]


bname: Basename file
outputname: rejoin [ bname EXT  ]

print [ "Converting file: " file  ]
print [ "Creating DB file: " outputname ] 
print [ "Init palette: " palnumber ];
print [ "Number of palettes: " numberofpals ];

; Read file

if (error? try [ rawdata: read/binary (to-file file) ]) [ Error [ "Can't read file " file ] ] 

dbdata: copy/deep ""

createDBheader dbdata
createDBpal dbdata rawdata palnumber numberofpals
createDBpalSMS dbdata rawdata palnumber numberofpals
saveFile outputname dbdata 

ExitOK




