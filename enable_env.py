#!/usr/bin/env python3
""" Django's command-line utility for administrative tasks.
    Instalaccion de pipenv 
    $ sudo apt update -yqq    
    $ sudo apt-get -yqq install build-essential
    $ sudo apt-get -yqq install python3-pip python3-dev 
    $ pip3 install --user pipenv
    
    $ export PATH=~.local/bin:$PATH
    


pip3 install --upgrade pip
## unicorn no esta en requeriment
## gunicorn config.wsgi [config: folder que contiene el archivo wsgi.py]
RUN pip3 install django gunicorn
## instalamos las utilidades usadas por la app
RUN pip3 install easy_thumbnails xlsxwriter validate_email
# RUN pip3 install psycopg2 pillow openpyxl
RUN pip3 install pillow openpyxl django-multi-email-field django-filer

## FIXME 
RUN pip3 install tzdata    
"""
import os
import sys
import subprocess

import signal
import platform

def Exit_gracefully(signal, frame):
    print("Cerrando Environment")
    sys.exit(0)


def getPathPipEnv() -> str:
  """
    
  """
  #path_cmd = None
  ## no lo contiene al path de pipenv solo el de python.exe
  ##  >> py -m site --user-site
  ##  C:\Users\jesus\AppData\Roaming\Python\Python38\site-packages
  ## la ruta
  ## c:\\Users\\jesus\\AppData\\Roaming\\Python\\Python38\\Scripts\\
  ##
  #[print(f'{it}',end='') for it in file.readlines()]
  it = ''
  if('pipenv.exe' in it):
    path_cmd = it
    #C:\Users\jesus\AppData\Local\Microsoft\WindowsApps\python.exe  
  return f'{it}'

def main():
  """Run administrative tasks."""
  try:
    print(f'Habilitando el Entorno virtual para el Usuario: {os.getlogin()}')
  except Exception as e:
    print(f'Error os.getlogin() : {e}')
  
  if(platform.system() == 'Windows' or 'CYGWIN' in f'{platform.system()}'):
    ## para saver donde esta instalado todo en windows:
    #subprocess.call(f" {getPathPipEnv()}ipts\\pipenv.exe shell", shell=True)
    #subprocess.call(f" where python", shell=True)
    subprocess.call(f" c:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Python\\Python38\\Scripts\\pipenv.exe shell", shell=True)
  else:
    subprocess.call(f" pipenv shell", shell=True)


if __name__ == '__main__':
  signal.signal(signal.SIGINT, Exit_gracefully)
  main()
