#!/bin/bash

PARAMS=$#
SOURCE=$1
DEST=$2
SIZE=$3

if [ $PARAMS -lt 3 ]
then
    echo "Usage: vrampacker sourcefile destfile sizecut";
fi

cuttersize $SOURCE $SIZE > /dev/null

BASECUT="${SOURCE%.*}"
COUNT=$(ls -1 $BASECUT.0* | wc -l)
FILES=$(find $BASECUT.0*)

rm -Rf $BASECUT.pck
for file in $FILES
do
    pack $file > /dev/null
    rm -Rf $file
    mv $file.pck $file
done

printf "\\x$(printf "%x" $COUNT)" > $BASECUT.count

cat $BASECUT.count $FILES > $DEST


