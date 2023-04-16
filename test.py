#!/usr/bin/python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
import socket
import subprocess
import signal
from typing import Optional

CMD_PYTHON='python3'

BackgroundColor = {
            'BLACK'  :40
            ,'RED'    :41
            ,'GREEN'  :42
            ,'YELLOW' :43
            ,'BLUE'   :44
            ,'MAGENTA':45
            ,'CYAN'   :46
            ,'WHITE'  :47
            }

FontColor = {
            'BLACK'   :30
            ,'RED'    :31
            ,'GREEN'  :32
            ,'YELLOW' :33
            ,'BLUE'   :34
            ,'MAGENTA':35
            ,'CYAN'   :36
            ,'WHITE'  :37            
            }

Style = {'RESET':0, 'BOLD':1, 'UNDERLINE':2 , 'ITALIC':3,'BLINK':5}





def cprint(*lvalues: object,lsep: Optional[str]=' ',lend: Optional[str] = '\n',lbegin: Optional[str]='',lfile: Optional[str]=sys.stdout,lflush: Optional[str] = False,fcolor: Optional[str]='',bcolor: Optional[str] = '',fstyle: Optional[str] = '',) -> None:
  '''
    @fn def cprint()
    @brief funcion para imprimir un mensaje por pantalla con un color
    @param idem a print(), para versiones usperiores de python 3.6 f'{var}'
  '''
  if(fcolor == '' and bcolor == '' and fstyle == ''):
    return print(*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)
  
  font_color = None
  back_color = None
  font_style = None
  
  if(fcolor != ''):
    fcolor = fcolor.upper()  
        
  if(bcolor != ''):
    bcolor = bcolor.upper()    
    
  if(fstyle != ''):
    fstyle = fstyle.upper()

  
  if(not fcolor in FontColor.keys() and fcolor != ''):
    return print(*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)
    
  if(not bcolor in BackgroundColor.keys() and bcolor != ''):
    return print(*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)    
    
  if(not fstyle in Style.keys() and fstyle != '' ):
    return print(*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)    
  
  """ 
    print("\033[1;32;40m Bright Green  \n")
            ~~~ ~ ~~ ~~
              | |  |  |
              | |  |  +-> BACKGROUND COLOR 'Black'
              | |  +----> FONT COLOR 'green'
              | +-------> TEXT STYLE 'bold'
              +---------> Escape code
  """ 
  font_cfg_begin = None  
  
  if(  fcolor != '' and bcolor != '' and fstyle != ''):
    font_cfg_begin = f'\033[{Style[fstyle]};{FontColor[fcolor]};{BackgroundColor[bcolor]}m'

  elif(fcolor != '' and bcolor != '' and fstyle == ''):
    font_cfg_begin = f'\033[0;{FontColor[fcolor]};{BackgroundColor[bcolor]}m'    

  elif(fcolor != '' and bcolor == '' and fstyle != ''):
    font_cfg_begin = f'\033[{Style[fstyle]};{FontColor[fcolor]}m'    
                          
  elif(fcolor != '' and bcolor == '' and fstyle == ''):
    font_cfg_begin = f'\033[0;{FontColor[fcolor]}m'    
                          
  elif(fcolor == '' and bcolor != '' and fstyle != ''):
    font_cfg_begin = f'\033[{Style[fstyle]};{BackgroundColor[bcolor]}m'    
                          
  elif(fcolor == '' and bcolor != '' and fstyle == ''):
    font_cfg_begin = f'\033[0;{BackgroundColor[bcolor]}m'    
                          
  elif(fcolor == '' and bcolor == '' and fstyle != ''):
    font_cfg_begin = f'\033[{Style[fstyle]}m'    
                          
  elif(fcolor == '' and bcolor == '' and fstyle == ''):
    return print(*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)
  
  
  if(lbegin != ''):
    return print(f'{lbegin} {font_cfg_begin}',*lvalues,sep=lsep, file=lfile, flush=lflush, end=f'\033[0m {lend}')
    
  return print(f'{font_cfg_begin}',*lvalues,sep=lsep, file=lfile, flush=lflush, end=f'\033[0m {lend}')
  

def getHostIp() -> str:
  """
    @brief Funcion para obtener la ip del Host, solo valida para
    host del tipo unix|linux
    @return string con la ip del Host, no la ip local '127.0.0.1'

  """
  st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    st.connect(('10.255.255.255', 1))
    IP = st.getsockname()[0]
  except Exception:
    IP = '127.0.0.1'
  finally:
    st.close()
  return f'{IP}'


def Exit_fn(signal, frame):
    cprint("\tCerrando Servicios.....",fcolor='CYAN',lend = '\n\n')
    sys.exit(0)

def main():
    """Run administrative tasks."""
    port = 8000
    ip = getHostIp()    
    cprint(f"Direccion Global: http://{ip}:{port}",lbegin='\t',fcolor='green',bcolor='black',fstyle='blink')
    #cprint(f"\tGlobal: http://{ip}:{port}\n",fcolor='red',bcolor='white',fstyle='bold')
    #subprocess.call(f" python enable_env.py", shell=True)
    subprocess.call(f"{CMD_PYTHON} manage.py runserver 0.0.0.0:{port}", shell=True)





  
if __name__ == '__main__':
  signal.signal(signal.SIGINT, Exit_fn)

  main()
