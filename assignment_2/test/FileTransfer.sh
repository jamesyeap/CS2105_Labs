#!/bin/bash

# colors
NOCOLOR='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
LIGHTGRAY='\033[0;37m'
DARKGRAY='\033[1;30m'
LIGHTRED='\033[1;31m'
LIGHTGREEN='\033[1;32m'
YELLOW='\033[1;33m'
LIGHTBLUE='\033[1;34m'
LIGHTPURPLE='\033[1;35m'
LIGHTCYAN='\033[1;36m'
WHITE='\033[1;37m'

numPassed=0
numTestCases=0
############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Syntax: $0 -i Student_id [-h|s|A|n|e|r] "
   echo "options:"
   echo "i     the secret student_id given to you"
   echo "h     Print this Help."
   echo "s     Run server."
   echo "A     Run all test."
   echo "n     Run reliable network test."
   echo "e     Run packet error test."
   echo "r     Run packet reorder test."
   echo
}

############################################################
############################################################
# Main program                                             #
############################################################
############################################################

student_id_missing=true

# Set variables
run_server=false
run_test_error=false
run_test_reorder=false
run_test_no_error=false

############################################################
# Process the input options. Add options as needed.        #
############################################################
# Get the options to see if we need to run the server
while getopts ":i:hsAner" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      i) # the student id
         student_id_missing=false
         student_id=$OPTARG;;
      s) # we will run as server
         run_server=true;;
      A) # test to run
         run_test_error=true
         run_test_reorder=true
         run_test_no_error=true;;
      n) # test to run
         run_test_no_error=true;;
      e) # test to run
         run_test_error=true;;
      r) # test to run
         run_test_reorder=true;;
     \?) # Invalid option
         echo "Error: Invalid option"
         Help
         exit;;
   esac
done

if $student_id_missing ; then
  echo 'student_id is not provided'
  echo
  Help
  exit
fi
#########################################################
if $run_server ; then
  echo -e "${YELLOW}Running test on Server${NOCOLOR}"
  fname="Server"
else
  echo -e "${YELLOW}Running test on Client${NOCOLOR}"
  fname="Client"
fi
echo '############################################'

# initializations
d0="$(dirname "$(readlink -f -- "$0")")"

source "$d0/common.sh"

mkdirTmp
findPy3

d1="$d0/.."
py36="/usr/local/Python-3.7/bin/python3"

######################
IP=137.132.92.111
function getFileName()
{
    local  myresult=''
    if $run_server ; then
      myresult="test/input/${mode}${size_val}.dat"
    else
      myresult="test/output/${mode}${size_val}.hash"
    fi
    echo "$myresult"
}
function getFileNameIn()
{
    local  myresult=''
    myresult="test/input/${mode}${size_val}.dat"
    echo "$myresult"
}
function getFileNameInHash()
{
    local  myresult=''
    myresult="test/input/${mode}${size_val}.hash"
    echo "$myresult"
}
function getPortNum()
{
    local  myresult=''
    case $mode in
      0) # mode
         myresult=4445;;
      1) # mode
         myresult=4446;;
      2) # mode
         myresult=4447;;
      3) # mode
         myresult=4448;;
     \?) # Invalid option
         echo "Error: Invalid mode"
         exit;;
   esac
   echo "$myresult"
}

function check_md5()
{
  # if you are client compare the hash value
  if ! $run_server ; then
    echo "generating the md5 digest and comparing"
    fileNameIn=$(getFileNameIn)
    fileNameInHash=$(getFileNameInHash)
    md5_org=$(cat $fileNameInHash)
    md5_client=($(md5sum $fileName))
    echo "correct  digest:" $md5_org
    echo "client's digest:" $md5_client

    numTestCases=$((numTestCases + 1))
    if [[ "$md5_org" == "$md5_client" ]]; then
      numPassed=$((numPassed + 1))
      echo
      echo -e "${size_val} ${GREEN}Test passed${NOCOLOR}"
      echo
    else
      echo
      echo -e "${size_val} ${RED}Test Failed${NOCOLOR}"
      echo
    fi
    # needed to ensure we wait for the simulator to flush old connection
    sleep 5
  else
    # to compensate for the time taken by client to generate the hash
    sleep 10
  fi
}

function generate_file_and_info()
{
  echo '############################################'
  case $mode in
      0) # mode
         echo -e "${YELLOW}---------------Running test on reliable channel---------------${NOCOLOR}";;
      1) # mode
         echo -e "${YELLOW}---------------Running test with packet error-----------------${NOCOLOR}";;
      2) # mode
         echo -e "${YELLOW}---------------Running test with packet reorder---------------${NOCOLOR}";;
      3) # mode
         echo -e "${YELLOW}---------------Running test with packet error and reorder-----${NOCOLOR}";;
     \?) # Invalid option
         echo "Error: Invalid mode"
         exit;;
  esac

  # delete the existing hash file if you are client
  if ! $run_server ; then
    rm $fileName
  fi

  # generate file if needed
  (eval exec $py36 test/GenerateRandomFile.py $mode)
  echo
  echo
}

function execute_test()
{
  portNum=$(getPortNum)
  fileName=$(getFileName)

  generate_file_and_info
  # executing the student code
  (eval exec "$evalcmd" $student_id $mode $IP $portNum $fileName)
  check_md5
}
##########################

if $run_test_no_error ; then
  mode=0
  size_val='_small'
  execute_test
  size_val='_large'
  execute_test
fi

if $run_test_error ; then
  mode=1
  size_val='_small'
  execute_test
  size_val='_large'
  execute_test
fi

if $run_test_reorder ; then
  mode=2
  size_val='_small'
  execute_test
  size_val='_large'
  execute_test
fi

if ! $run_server ; then
  echo "------------ Summary ------------"
  echo "Passed $numPassed out of $numTestCases cases."
fi
