#!/bin/bash

d0="$(dirname "$(readlink -f -- "$0")")"

source "$d0/common.sh"

mkdirTmp
findPy3

#d1="/home/course/cs2105/autotest/a1"
d1="$d0/.."
py36="/usr/local/Python-3.7/bin/python3"

######################
(eval exec "$evalcmd" $1 2> "$tmpdir/s-err")
echo
echo
echo "Client terminated"
echo "Server log"
echo "----------------------------------------------------"
echo "--     Server Log being dumped in log.txt         --"
echo "----------------------------------------------------"
./test/print_result $1 > log.txt
echo "----------------------------------------------------"
echo "----------------------------------------------------"
