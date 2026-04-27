#!/bin/bash

DEST=$1
shift
PARAMS=$#

if [ $PARAMS -eq 0 ]
then
    echo "Usage: ram2data destdir ramfile [...]";
fi

declare -a DATA=("00" "01" "02" "03" "04" "05" "06" "07" "08")


for ((i=0 ; i < $PARAMS ; i++))
do
    pletter $1 $DEST/DATA.T${DATA[$i]}
    shift
done


