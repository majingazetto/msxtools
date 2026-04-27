
REBOL 
[
    Author: "Armando Pérez Abad (Ramones)"
    File: %sms2rom.r
    Date: 21-Jan-2010
    Title: "SMS Rom to MSX Franky Compatible ROM"
]

; Version special para golvellius

; *****************************************************
; *               Const / Vars                        *
; *****************************************************

VERSION: "1.0"
BYTESBACK: 32
sqdata: [

    #{D3FE00} #{CD09FD}
    #{D3FD00} #{CD06FD}
    #{D3FC00} #{CD03FD}

    #{DBFE00} #{3A02FD}
    #{DBFD00} #{3A01FD}
    #{DBFC00} #{3A00FD}
    
]



; *****************************************************
; *          Print Console / Exit / Error             *
; *****************************************************

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
    print ["SMS2ROM v."VERSION"SMS ROM to MSX Franky ROM"]    
    print ["(c) 2010 Ramones"]
    print ""
]




; -----------------------------------------------------
; Usage
; prints usage
; In/Out: (none)
; -----------------------------------------------------

Usage: func []
[
    print [ "Usage: rebol --quiet --secure allow --script sms2rom.r SMSRomFile" ]
    print [ "    SMSRomFile: Master System Rom file to convert." ]
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




; *****************************************************
; *              Operating System                     *
; *****************************************************


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
; *                 Low level datatypes               *
; *****************************************************


    ; all "to" conversions returns binary! datatype! 

    to-ilong: func [
        "Converts an integer to a little-endian long."
        value [integer!] "Value to convert"
    ][
        to-binary rejoin [
            to-char value and 255
            to-char to-integer (value and 65280) / 256
            to-char to-integer (value and 16711680) / 65536
            to-char to-integer (value / 16777216)
        ]
    ]
    to-ishort: func [
        "Converts an integer to a little-endian short."
        value [integer!] "Value to convert"
    ][
        to-binary rejoin [
            to-char value and 255
            to-char to-integer value / 256
        ]
    ]
    to-long: func [
        "Converts an integer to a big-endian long."
        value [integer!] "Value to convert"
    ][do join "#{" [to-hex value "}"]]
    
   
    to-byte: func [
        "Converts and integer to a byte (low byte only)."
        value [integer!] "Value to convert"
        ] 
        [ 
            to-binary to-char value and 255
        ]


    get-ishort: func [
        "Converts a little-endian short to an integer."
        value [any-string! port!] "Value to convert"
    ][to-integer head reverse to-binary copy/part value 2]
    get-ilong: func [
        "Converts a little-endian long to an integer."
        value [any-string! port!] "Value to convert"
    ][to-integer head reverse to-binary copy/part value 4]


; *****************************************************
; *                 Conversion                        *
; *****************************************************

; converts integer block into a binary short little endian

blockToiShortBin: function [ data [ block! ] ]
[ bindata ]
[
    
    ; init bin data
    bindata: copy/deep #{}
    forall data
    [
        append bindata to-ishort (first data)
    ]
    bindata 

    

]
; converts integer block into a binary byte

blockToByteBin: function [ data [ block!] ]
[ bindata ]
[
    ; init bin data
    bindata: copy/deep #{}
    forall data
    [
        append bindata to-byte (first data)
    ]
    bindata 

]



; *****************************************************
; *                 Convert code                      *
; *****************************************************


replaceGeneric: function [ data [binary!] repdata[block!] ]
[
    ordata 
    chgdata 
]
[
    repdata: head repdata
    while [ not tail? repdata ]
    [
        ordata: first repdata
        chgdata: second repdata

        replace/case/all data ordata chgdata 

        repdata: next repdata
        repdata: next repdata
    ]
    data 
]



; IO searh data
iosearch: [
    #{D37E}
    #{D37F}
    #{D3BE}
    #{D3BF}
    #{D3F0}
    #{D3F1}
    
    
    #{DB7E}
    #{DB7F}
    #{DBBE}
    #{DBBF}
    #{DBDC}
    #{DBDE}
    

]
        
; IO change data
iochange: [

    #{D348}
    #{D349}
    #{D388}
    #{D389}
    #{D37C}
    #{D37D}

    #{DB48}
    #{DB49}
    #{DB88}
    #{DB89}
    #{DBA2}
    #{DBA2}

]

iomassearch: [
    #{EDA2}
    #{EDA3}
    #{EDB3}
    #{ED41}
    #{EDB2}
]

iomasinssr: [
    #{0E7E} #{0E48}
    #{0E7F} #{0E49}
    #{0EBE} #{0E88}
    #{0EBF} #{0E89} 
    #{0EF0} #{0E7C} 
    #{0EF1} #{0E7D} 
    #{017E} #{0148} 
    #{017F} #{0149} 
    #{01BE} #{0188} 
    #{01BF} #{0189} 
    #{01F0} #{017C} 
    #{01F1} #{017D}
]


replaceIO: function [ smsdata [ binary! ] ]
[
    smsport
    msxport
    tmpport
    z80ins
    fz80ins
    cnt
]
[
    ; Replace direct I/O
    
    iosearch: head iosearch
    iochange: head iochange

    while [ not tail? iosearch ]
    [
        smsport: first iosearch 
        msxport: first iochange 

        replace/case/all smsdata smsport msxport 


        iosearch: next iosearch 
        iochange: next iochange
    ]
    
    ; replace inir, ini, otir, outi

    iomassearch: head iomassearch

    while [ not tail? iomassearch ] 
    [
        z80ins: first iomassearch

        fz80ins: find/case smsdata z80ins
        
        ; instruction found
        while [ fz80ins  ]
        [
            iomasinssr: head iomasinssr
           ; print ["Valor encontrado: " z80ins ]
            while [not tail? iomasinssr]
            [
                smsport: first iomasinssr
                msxport: second iomasinssr
                fz80ins: skip fz80ins (BYTESBACK * -1)

                cnt: 0
                while [cnt < BYTESBACK ]
                [
                    tmpport: copy/part fz80ins 2
                    if (tmpport = smsport)
                    [
                        replace/case fz80ins tmpport msxport
                    ]
                    fz80ins: next fz80ins 
                    cnt: cnt + 1
                ]

                iomasinssr: skip iomasinssr 2
            ]
            fz80ins: next fz80ins
            fz80ins: next fz80ins
            fz80ins: find/case fz80ins z80ins
        ]
        iomassearch: next iomassearch

    ]
    smsdata
]

mappersr: [
    #{32FFFF} #{CD09FD}
    #{32FEFF} #{CD06FD}
    #{32FDFF} #{CD03FD}

    #{3AFFFF} #{3A02FD}
    #{3AFEFF} #{3A01FD}
    #{3AFDFF} #{3A00FD}
   

    #{32FFDF} #{CD09FD}
    #{32FEDF} #{CD06FD}
    #{32FDDF} #{CD03FD}

    #{3AFFDF} #{3A02FD}
    #{3AFEDF} #{3A01FD}
    #{3AFDDF} #{3A00FD}
]


replaceMapper: function [ smsdata [binary!] ] 
[
    smsmapper
    msxmapper
]
[
    mappersr: head mappersr
    while [ not tail? mappersr ]
    [
        smsmapper: first mappersr
        msxmapper: second mappersr

        replace/case/all smsdata smsmapper msxmapper
        

        mappersr: next mappersr
        mappersr: next mappersr
    ]
    smsdata
]

; -----------------------------
; createRomFile
; Converts sms file
; to compatible Franky ROM file
; In:
;   binary! msxpage 0 code
;   binary! smsdata (rom file)
; Out:
;   binary! ROM file
; -------------------------------
createRomFile: function [ msxdata [binary!]  smsdata [binary!] ]
[
    romdata
]
[
    ; init romdata
    romdata: copy/deep smsdata
   
    ; firts replace I/O Entrys (vdp, psg)

    romdata: replaceIO romdata   
    
    ; replace mapper data

    romdata: replaceMapper romdata

    ; finally insert msxdata
    insert romdata msxdata
    romdata 
]


createRomFileGen: function [ msxdata [binary!]  smsdata [binary!] repdata [block!] ]
[
    romdata
]
[
    ; init romdata
    romdata: copy/deep smsdata
   
    ; replace generic
    romdata: replaceGeneric romdata repdata
    
    ; finally insert msxdata
    insert romdata msxdata
    romdata 
]


; Tabla de parcheo automatico

; Direccion (atencion a poner bytes enteros)
; Viejo valor
; nuevo valor

manualdata: [
    #{01EEED} #{88} #{BE} 
]

manualPatch: function [ romdata [binary! ] ]
[
    dir
    oldval
    newval

]
[
    if (length? manualdata) 
    [
        manualdata: head manualdata
        while [not tail? manualdata]
        [
            dir: to-integer manualdata/1
            oldval: manualdata/2
            newval: manualdata/3
            replace/case (skip romdata dir) oldval newval
            manualdata: skip manualdata 3
        ]
    ]
    romdata
]


; *****************************************************
; *                 Main Code                         *
; *****************************************************


if not value? 'cons [cons: open/binary [scheme: 'console]]
args: system/options/args

Logo


if  ( args = none )
[
    ExitUsage
]


; read filename from args

filename: args/1

; keyboard parth?

key: false

if (find args "key")
[
    key: true
]

; default msxdata here


; load filename

if (error? try [smsdata: read/binary to-file filename]) [ Error [ "Can't load SMS file->" to-string filename ] ]

; read msxdata
msxdata: rejoin [ what-dir "msxpage0.rom" ]

if (error? try [msxpage0: read/binary to-file msxdata]) [ Error [ "Can't MSXDATA->" msxdata ] ]

; convert


either (find args "super")
[
    print ["Patching with super mode."]
    romdata: createRomFileGen msxpage0 smsdata sqdata
]
[
    print ["Normal SMS path"]
    romdata: createRomFile msxpage0 smsdata
]

; manual patch

romdata: manualPatch romdata

; save
bname: Basename filename
bname: rejoin [ bname ".rom" ]
if (error? try [ write/binary to-file bname romdata]) [ Error [ "Can't Write output file ->" bname ] ]


ExitOK

