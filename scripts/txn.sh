#!/bin/bash

INP_DIR="/data/transactions_in"
mkdir -p $INP_DIR

for i in `ls /data/transactions`; do
    sed '1d' /data/transactions/$i > $INP_DIR/$i.tmp
done

cat $INP_DIR/*.tmp > $INP_DIR/alltxns.txt
rm -rf $INP_DIR/*.tmp
