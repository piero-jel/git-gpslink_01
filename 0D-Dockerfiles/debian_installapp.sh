#!/bin/bash
#=====================================================================================================
##
## Copyright 2015 - 2018, Luccioni Jesus Emanuel "J.E.L"
## All rights reserved.
#
#=====================================================================================================
## stdinp  0
## stdout  1
## stderr  2
CMD_APT=apt-get
CMD_PYTHON=python3
LOG=$PWD/log/install.log
LOG_ERR=$PWD/log/install_err.log


## redirect 
# echo "Esto es un mensaje"  1>$PWD/f.log
# echo "Esto es un mensaje"  1>$PWD/f.log 2>$PWD/f.log


function main()
{
#   apt-get update
#   apt-get install -y python3
#   apt-get install -y python3-pip
#   python3 -m pip install requests
#   python3 -m pip install flask
#   python3 -m pip install Django djangorestframework
#   python3 -m pip install fastapi
#   python3 -m pip install uvicorn[standard]
#   
  touch $LOG
  $CMD_APT update 1>$LOG 2>$LOG
  $CMD_APT install -y python3 1>$LOG 2>$LOG_ERR
  $CMD_APT install -y python3-pip 1>$LOG 2>$LOG_ERR
  $CMD_PYTHON -m pip install requests 1>$LOG 2>$LOG_ERR
  $CMD_PYTHON -m pip install flask 1>$LOG 2>$LOG_ERR
  $CMD_PYTHON -m pip install Django djangorestframework 1>$LOG 2>$LOG_ERR
  $CMD_PYTHON -m pip install fastapi 1>$LOG 2>$LOG_ERR
  $CMD_PYTHON -m pip install uvicorn[standard] 1>$LOG 2>$LOG_ERR
  return 0
}
main "$@" && exit 0
