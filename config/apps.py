from django.conf import settings
import sys
from typing import Optional
from .settings import DEBUG
from sys import exc_info
from pathlib import Path

from django.utils import timezone
from datetime import datetime, time

import logging
import os
PWD_DIR = Path(__file__).resolve().parent.parent
path = f'{PWD_DIR}/log/'
__pathfile = f'{PWD_DIR}/log/app.log'
## 10M 10*1024*1024 = 10485760
__size_max = 10485760
__deltatime = {'dias':4,'segundos':3600}
logging.basicConfig(level=logging.DEBUG, filename=__pathfile, format='%(asctime)s %(levelname)s:%(message)s')


BGColor = { 'HEADER' : '\033[95m'
                  , 'OKBLUE' : '\033[94m'
                  , 'OKCYAN' : '\033[96m'
                  , 'OKGREEN' : '\033[92m'
                  , 'WARNING' : '\033[93m'
                  , 'FAIL' : '\033[91m'
                  , 'ENDC' : '\033[0m'
                  , 'BOLD' : '\033[1m'
                  , 'UNDERLINE' : '\033[4m'}

def get_pathfile(lstr:str)->str:  
  ##buscamos el primer '\'
  posi = lstr.find("\'")
  ##
  posi += 1
  ##
  tmp = lstr[posi:]
  ## Buscamso la posicion final
  posf = tmp.find("\'")
  posf += posi
  # return lstr[posi:posf]
  return (os.path.dirname(lstr[posi:posf]) , os.path.basename(lstr[posi:posf]))
  dirname = os.path.dirname(pathfile)
  filename = os.path.basename(pathfile)


def file_truncate(**args):
  '''
    @fn def truncatefile(**args):
    
    args:
      * pathfile : ruta y nombre del archivo
  '''  
  if(__pathfile == None):
    return
  
  file_path = Path(__pathfile)
  with file_path.open("w") as file:
    file.write('')


def check_deltatime(acutime,deltatime) -> bool:
  """
    * acutime : variable donde la funcion acumula su tiempo. Este se actualiza al devolver True
    * deltatime : dic{'dias': <Nro Dias>,'segundos': <Nro Seg>}
  """
  try:
    delta = datetime.now() - acutime
    if(delta.days >= deltatime['dias'] and delta.seconds > deltatime['segundos']):        
      return True
    return False
  except:
    return False
  


def file_check(**args)-> bool :
  """
    @brief funcion que chequea un archivo, su existencia y si se especifica su tamaño
    en caso de que el mismo esceda este sera truncado (truncated = True, valor por defecto).
    @parama args
     * pathfile : ruta y nombre del archivo. Mandatorio.
     * size_max : tamaño maximo del archivo str o int, opcional.
     * truncated : {True (default) | False} especificamos si debe o no truncar el archivo. 
     Es valido si pasamos size_max de lo contrario se descarta.
  """
  if not hasattr(file_check, "localtime"):
    file_check.localtime = datetime.now()

  if(check_deltatime(file_check.localtime,__deltatime) == False):
    return True

  file_check.localtime = datetime.now()
  if(__pathfile == None):
    return False 
  
  truncated = args.get('truncated',True)

  file_path = Path(__pathfile)
  if(file_path.is_file() == False):
    return False
  
  if(__size_max == None):
    return True
    
  
  if(__size_max < file_path.stat().st_size and truncated == False):
    return True

  if(__size_max < file_path.stat().st_size):
    # print(f'truncando file {pathfile} size: {file_path.stat().st_size} size_max:{size_max}')
    file_truncate(pathfile=__pathfile)

  return True
  
from validate_email import validate_email

def validatinEmails(**args) -> bool:
  """
    @param args
      * email Este puede ser el strin que representa una direccion de email.
      Puede ser un diccionario con la clave 'email' donde esta el string de dirreccion de email.
      
      Puede ser una lista de emails


  """
  email = args.get('email',None)
  if(email == None):
    return False
  rval = None

  if(isinstance(email,str) == True):
    rval = validate_email(email,verify=True)
  
  elif((isinstance(email,dict) == True) and 'email' in email.keys() and\
     (isinstance(email['email'],str) == True) and (email['email'] != '')):
    rval = validate_email(email['email'],verify=True)


  else:
    return False

  if(rval == None):
    return False
  return True
  
  


def debug_print(
      *lvalues: object,
      lsep: Optional[str] = ' ' ,
      lend: Optional[str] = '\n' ,
      lfile: Optional[str] = sys.stdout ,
      lflush: Optional[str] = False ,
      ) -> None:
  '''
    @fn def debug_print()
    @brief funcion para imprimir un mensaje por pantalla y en un archivo.
    @param idem a print(), para versiones usperiores de python 3.6 f'{var}'
  '''
  folder,file = get_pathfile(str(sys._getframe().f_back))
  if(not DEBUG):
    if(file_check() == True):
      logging.info(f'{BGColor["WARNING"]} {folder}/{file}:{sys._getframe().f_back.f_lineno} \033[0m'+ str(*lvalues))

    return 
  # print(*lvalues)
  # print(lsep)
  # print(lend)
  # print(lfile)
  # print(lflush)
  # pathFile = getPathFile(f'{sys._getframe().f_back}')
  
  print(f'{BGColor["WARNING"]}{folder}/{file}:{sys._getframe().f_back.f_lineno} \033[0m',*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)
  logging.info(f'{BGColor["WARNING"]} {folder}/{file}:{sys._getframe().f_back.f_lineno} \033[0m'+ str(*lvalues))
  # logging.info(f'{BGColor["WARNING"]} {getPathFile(f"{sys._getframe().f_back}")}:{sys._getframe().f_back.f_lineno} \033[0m'+ f'{lvalues}')
  # logging.info(f'{BGColor["WARNING"]} {sys._getframe().f_back}:{sys._getframe().f_back.f_lineno} \033[0m'+ str(*lvalues))
  # print(f'type {type(sys._getframe().f_back)} {sys._getframe().f_back}:{sys._getframe().f_back.f_lineno}',*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)
  # print(f'{exc_info()}::{sys._getframe().f_back}:{sys._getframe().f_back.f_lineno}',*lvalues,sep=lsep, end=lend, file=lfile, flush=lflush)
  

def check_phoneNumber(**args) -> bool:
  """
    @brief
    @param args
      * number : Numero de telefono que se chequea
  """
  number = args.get('number',None)
  if(number == None or isinstance(number,str) == False):
    return False

  ## FIXME add check tel number
  if(len(number) > 0 ):
    tmp = number
    if(tmp[0] == '+' or tmp[0] == '-'):
      tmp = tmp [1:]
    try:
      tmp = int(tmp)
    except:      
      return False 
  ##endif
  ##
  return True


def deltatime2time(deltatime) -> time:
  days, seconds = deltatime.days, deltatime.seconds
  Hh = days * 24 + seconds // 3600
  Mm = (seconds % 3600) // 60
  Ss = (seconds % 60)
  # rval = datetime.now()
  # hour=Hh, minute=Mm, second=Ss)
  return time(Hh,Mm,Ss)


def str2systemdate(strdate:str):
  """
    @fn def str2date(strdate:str):
    @brief funcion para convertir un str a una fecha p/el sitema
    los formato que pueden venir son_
      + yyyy / mm / dd
      + dd / mm / yyyy
      considerando un separador {'/','-', ' '}
  """
  if(len(strdate) < 10):
    return None
  separador = ('/','-',' ')
  dd = None
  mm = None
  yy = None
  if((strdate[2] in separador) and (strdate[5] in separador) and (strdate[2] == strdate[5])):
    # formato dd/mm/yyyy
    dd = strdate[:2]
    mm = strdate[3:5]
    yy = strdate[6:10]

  elif((strdate[4] in separador) and (strdate[7] in separador) and (strdate[4] == strdate[7])):    
    yy = strdate[:4]    
    mm = strdate[5:7]
    dd = strdate[8:10]
  else:
    return None

  return f'{yy}-{mm}-{dd}'  

# import StringIO
try:
    from StringIO import StringIO

except ImportError:
    from io import StringIO

from io import BytesIO


import xlsxwriter
from django.utils.translation import ugettext ,ugettext_lazy


SHEET_COL = ('A:A','B:B','C:C','D:D','E:E','F:F','G:G','H:H','I:I','J:J','K:K'\
    ,'L:L','M:M','N:N','O:O','P:P','Q:Q','R:R','S:S','T:T','U:U','V:V' \
    ,'W:W','X:X','Y:Y','Z:Z','AA:AA','AB:AB','AC:AC','AD:AD','AE:AE','AF:AF','AG:AG')

def number2name(col:int) -> str:
  if(col > len(SHEET_COL)):
    col = col % len(SHEET_COL)
  return SHEET_COL[col]

def computeRows(text, width,font_size):
  """
    @fn def computeRows(text, width,font_size):
    @brief
    @param text       : texto a computar en funcion de su longitud
    @param width      : Ancho de la columna
    @param font_size  : Tamaño de la letra.

    @retrun valor para establecer en la celda y en el formato
      {'nrow':font_size, 'rtext':text}
    
    @example
      cellFormatCenter = workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
      'valign': 'vcenter'})
      ...
      a = computeRows(it.msg,40,12)        
      worksheet_s.write_string(crow, ccol, a['rtext'], cellFormatCenter)
      worksheet_s.set_row(crow, a['nrow'])

  """
  if len(text) < width:
    return {'nrow':3*font_size, 'rtext':text}
    
  
  newLine = '\n'

  rtext = ''
  ltext = text.split(' ')
  acum = 0
  nrow = 3
  for it in ltext:
    if( width > acum and len(it) < (width-acum)):
      rtext += it
      rtext += ' '
      acum += (len(it) + 1)

    else:
      rtext += newLine
      nrow += 1
      rtext += (it + ' ')
      acum = (len(it) + 1)

  ## endfor
  return {'nrow':nrow*font_size, 'rtext':rtext}


def createReportExcel(**args):
  """
    @fn def def createReportExcel(**args):
    @brief funcion para crear el reporte en formato de excell
    @param args:
      + context : contxto, contenido del reporte
  """
  contexto = args.get('context',None)

  if(contexto == None):
    return None

  # output = StringIO()
  output = BytesIO()
  workbook = xlsxwriter.Workbook(output)
  # workbook = xlsxwriter.Workbook('Report.xlsx')

  ## creamos una hoja
  worksheet_s = workbook.add_worksheet("reporte")
  ## creamos los formatos para el titulo y heade, celdas para el libro de trabajo 
  title = workbook.add_format({
      'bold': True
      ,'font_size': 14
      ,'align': 'center'
      ,'valign': 'vcenter'
  })
  subTitle = workbook.add_format({
      'bold': True
      ,'font_size': 13
      ,'color': 'blue'
      ,'align': 'left'
      ,'valign': 'vcenter'
      ,'border': 1
  })
  header = workbook.add_format({
      'bold': True,
      'bg_color': '#F7F7F7',
      'color': 'black',
      'align': 'center',
      'valign': 'top',
      'border': 1
  })
  cellFormat = workbook.add_format({'bold': False, 'font_color': 'blue','align': 'center','border': 1})

  # cellFormatCenter = workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
  #     'valign': 'vcenter','border': 1})

  cellFormatCent = { 
     'register' : workbook.add_format({'bold': False, 'font_color': 'black','font_size': 12,'align': 'center',
        'valign': 'vcenter','border': 1,'bg_color':'#BBBBBB'})

    ,'attend': workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
        'valign': 'vcenter','border': 1,'bg_color':'#FFFFFF'})

    ,'desarrollo': workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
        'valign': 'vcenter','border': 1,'bg_color':'#DDDDDD'})
  }

  cellFormatTicket = {
    ## https://xlsxwriter.readthedocs.io/format.html#format
      # color (161,219,219) = (A1,DB,DB)
      'open': workbook.add_format({'bold': True, 'font_color': 'black','font_size': 12,'align': 'center',
          'valign': 'vcenter','border': 1,'bg_color':'#A1DBDB'})

      # color (77,187,77) = (4D,BB,4D)
      ,'close': workbook.add_format({'bold': True, 'font_color': 'black','font_size': 12,'align': 'center',
          'valign': 'vcenter','border': 1,'bg_color':'#4DBB4D'})

      # color (246,246,83) = (F6,F6,56)
      ,'pending': workbook.add_format({'bold': True, 'font_color': 'black','font_size': 12,'align': 'center',
          'valign': 'vcenter','border': 1,'bg_color':'#F6F656'})
      }  
  '''
  cellFormatTicket_open = workbook.add_format({'bold': False, 'font_color': 'red','font_size': 12,'align': 'center',
      'valign': 'vcenter','border': 1})
  cellFormatTicket_open.set_bg_color('yellow')
  '''


  cellTimeFormat = {
    'attend' : workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
        'valign': 'vcenter','num_format':'hh:mm:ss','border': 1})

    ,'register' : workbook.add_format({'bold': False, 'font_color': 'black','font_size': 12,'align': 'center',
        'valign': 'vcenter','num_format':'hh:mm:ss','border': 1,'bg_color':'#BBBBBB'})

    ,'desarrollo' : workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
        'valign': 'vcenter','num_format':'hh:mm:ss','border': 1,'bg_color':'#DDDDDD'})
  }


  cellTimeTotalFormat = workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
      'valign': 'vcenter','num_format':'hh:mm:ss','border': 2})

  cellDateTimeFormat = {
       'attend' : workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
          'valign': 'vcenter','border': 1,'num_format':'dd/mm/yyyy hh:mm:ss'})

      ,'register' : workbook.add_format({'bold': False, 'font_color': 'black','font_size': 12,'align': 'center',
          'valign': 'vcenter','border': 1,'num_format':'dd/mm/yyyy hh:mm:ss','bg_color':'#BBBBBB'})
          
      ,'desarrollo' : workbook.add_format({'bold': False, 'font_color': 'blue','font_size': 12,'align': 'center',
          'valign': 'vcenter','border': 1,'num_format':'dd/mm/yyyy hh:mm:ss','bg_color':'#DDDDDD'})
      }

  # cellFormatCenter.set_align('center')
  # cellFormatCenter.set_align('vcenter')
  ## creamos el titulo
  title_text1 = u"{0}".format(ugettext(f"Reporte: \"{contexto['dateFrom']} : {contexto['dateTo']}\""))
  
  flagRegister = False
  if('empresa' in contexto.keys() and contexto['empresa'] != ''):
    title_text2 = u"{0}".format(ugettext(f"Empresa: \"{contexto['empresa']}\""))
    ## Colocamos el titulo en el merge de las dos campos 

    worksheet_s.merge_range('B2:E2', title_text1, title)
    worksheet_s.merge_range('B3:E3', title_text2, title)

    worksheet_s.write_string(4,1, f'Fecha Inicio:', subTitle)
    worksheet_s.write_string(5,1, f'Fecha Final:', subTitle)
    worksheet_s.write_string(4,2, f'{contexto["dateFrom"]}', cellFormat)
    worksheet_s.write_string(5,2, f'{contexto["dateTo"]}', cellFormat)

    
    worksheet_s.write_string(4,3, f'Tiempo Total:', workbook.add_format({
      'bold': True
      ,'font_size': 13
      ,'color': 'blue'
      ,'align': 'center'
      ,'valign': 'vcenter'
      ,'border': 1} ))
    # worksheet_s.write_string(4,4, f'{contexto["AcuTime"]}', cellFormat)
    

    ## colocamos la cabecera de la tabla: <row:4> col:0 ... 2
    header_labels = {"Id":10,"Ticket/Desarrollos":20,"Quien Registro":25 \
      ,"Fecha de Creacion":30, "Trabajo Realizado":50, "Tiempo Consumido":25 \
      ,"Fecha de Actualizacion":30 }
    crow = 8
    ccol = 0
    for it,wd in header_labels.items():
      worksheet_s.write(crow,ccol, ugettext(it), header)
      worksheet_s.set_column(number2name(ccol), wd)
      ccol += 1

    crow += 1
    ccol = 0
    brow = crow+1
    ## write cellds contexto['all_regwork']
    typeCell = ''
    for it in contexto['all_regwork']:      
      if(it.programmer == True):
        typeCell = 'attend'              
      else:
        flagRegister = True
        typeCell = 'register'

      ## ID del workregister
      ccol = 0
      worksheet_s.write_number(crow, ccol, it.id, cellFormatCent[typeCell])
      ## ID del ticket,
      ccol += 1
      
      if(it.ticket.estado == True):
        if(it.ticket.register_estado == True):
          worksheet_s.write_number(crow, ccol, it.ticket.id, cellFormatTicket['open'])
        else:
          worksheet_s.write_number(crow, ccol, it.ticket.id, cellFormatTicket['pending'])
      else:
        worksheet_s.write_number(crow, ccol, it.ticket.id, cellFormatTicket['close'])

      ccol += 1      
      worksheet_s.write_string(crow, ccol, f'{it.register_work.username}', cellFormatCent[typeCell])
      ccol += 1
      worksheet_s.write_datetime(crow, ccol, it.date_creacion, cellDateTimeFormat[typeCell])
      ccol += 1
      ## para mensajes multilinea    
      a = computeRows(f'{it.msg}',header_labels['Trabajo Realizado'],12)      
      worksheet_s.write_string(crow, ccol, a['rtext'], cellFormatCent[typeCell])
      worksheet_s.set_row(crow, a['nrow'])

      ccol += 1
      if(it.programmer):        
        worksheet_s.write_datetime(crow, ccol, it.tiempo, cellTimeFormat[typeCell])
      else:
        worksheet_s.write_datetime(crow, ccol, time(0,0,0), cellTimeFormat[typeCell])

      ccol += 1
      worksheet_s.write_datetime(crow, ccol, it.date_update, cellDateTimeFormat[typeCell])

      crow += 1
    ## endfor    




    #worksheet_s.write_formula(4,4, f'{{=sum(F{brow}:F{crow})}}', cellTimeTotalFormat)
    colLetter = 'F'

  else:
    title_text2 = u"{0}".format(ugettext(f"Empresa: \"TODAS\""))        
    ## Colocamos el titulo en el merge de las dos campos 

    worksheet_s.merge_range('B2:E2', title_text1, title)
    worksheet_s.merge_range('B3:E3', title_text2, title)

    worksheet_s.write_string(4,1, f'Fecha Inicio:', subTitle)
    worksheet_s.write_string(5,1, f'Fecha Final:', subTitle)
    worksheet_s.write_string(4,2, f'{contexto["dateFrom"]}', cellFormat)
    worksheet_s.write_string(5,2, f'{contexto["dateTo"]}', cellFormat)

    worksheet_s.write_string(4,3, f'Tiempo Total:', workbook.add_format({
      'bold': True
      ,'font_size': 13
      ,'color': 'blue'
      ,'align': 'center'
      ,'valign': 'vcenter'
      ,'border': 1} ))
    # worksheet_s.write_string(4,4, f'{contexto["AcuTime"]}', cellFormat)

    ## Colocamos el titulo en el merge de las dos campos 
    worksheet_s.merge_range('B2:E2', title_text1, title)
    worksheet_s.merge_range('B3:E3', title_text2, title)

    ## colocamos la cabecera de la tabla: <row:4> col:0 ... 2
    header_labels = {"Id":10,"Ticket/Desarrollos":20,"Empresa":20,"Quien Registro":25 \
      ,"Fecha de Creacion":30, "Trabajo Realizado":50, "Tiempo Consumido":25 \
      ,"Fecha de Actualizacion":30 }
    crow = 8
    ccol = 0
    for it,wd in header_labels.items():
      worksheet_s.write(crow,ccol, ugettext(it), header)
      worksheet_s.set_column(number2name(ccol), wd)
      ccol += 1
      
    ''' 
      worksheet_s.write(4, 0, ugettext("Id"), header)
      worksheet_s.write(4, 1, ugettext("Ticket"), header)
      worksheet_s.write(4, 2, ugettext("Empresa"), header)
      worksheet_s.write(4, 2, ugettext("Empresa"), header)
      worksheet_s.write(4, 2, ugettext("Empresa"), header)
      worksheet_s.write(4, 2, ugettext("Empresa"), header)
    '''

    ## establecemos el ancho por defecto de las columnas:
    ''' 
      worksheet_s.set_column('A:A', 10)
      worksheet_s.set_column('B:B', 20)
      worksheet_s.set_column('C:C', 40)
    '''
    crow += 1
    ccol = 0
    brow = crow+1
    ## contexto['all_regwork']
    typeCell = ''
    for it in contexto['all_regwork']:      
      if(it.programmer == True):
        typeCell = 'attend'        
      else:
        flagRegister = True
        typeCell = 'register'
      ## id work register
      ccol = 0      
      # worksheet_s.write_number(crow, ccol, it.id, cellFormatCenter)
      worksheet_s.write_number(crow, ccol, it.id, cellFormatCent[typeCell])
      
      ## id tiket 
      ccol += 1
      if(it.ticket.estado == True):
        if(it.ticket.register_estado == True):
          worksheet_s.write_number(crow, ccol, it.ticket.id, cellFormatTicket['open'])
        else:
          worksheet_s.write_number(crow, ccol, it.ticket.id, cellFormatTicket['pending'])
      else:
        worksheet_s.write_number(crow, ccol, it.ticket.id, cellFormatTicket['close'])

      ccol += 1
      # worksheet_s.write_string(crow, ccol, f'{it.ticket.register.empresa.nombre}', cellFormatCenter)
      worksheet_s.write_string(crow, ccol, f'{it.ticket.register.empresa.nombre}', cellFormatCent[typeCell])
      ccol += 1
      # worksheet_s.write_string(crow, ccol, f'{it.register_work.username}', cellFormatCenter)
      worksheet_s.write_string(crow, ccol, f'{it.register_work.username}', cellFormatCent[typeCell])
      ccol += 1

      worksheet_s.write_datetime(crow, ccol, it.date_creacion, cellDateTimeFormat[typeCell])
      ccol += 1
      ## para mensajes multilinea    
      a = computeRows(f'{it.msg}',header_labels['Trabajo Realizado'],12)      
      # worksheet_s.write_string(crow, ccol, a['rtext'], cellFormatCenter)
      worksheet_s.write_string(crow, ccol, a['rtext'], cellFormatCent[typeCell])
      worksheet_s.set_row(crow, a['nrow'])

      ccol += 1

      # worksheet_s.write_string(crow, ccol, f'{it.tiempo}', cellFormatCenter)
      if(it.programmer):        
        worksheet_s.write_datetime(crow, ccol, it.tiempo, cellTimeFormat[typeCell])
      else:
        worksheet_s.write_datetime(crow, ccol, time(0,0,0), cellTimeFormat[typeCell])

      ccol += 1
      worksheet_s.write_datetime(crow, ccol, it.date_update, cellDateTimeFormat[typeCell])

      crow += 1
    ## endfor
    ## title_text1 = u"{0}".format(ugettext(f"Reporte: \"{contexto['dateFrom']} : {contexto['dateTo']}\""))    
    ## Total Time
    #worksheet_s.write_formula(4,4, f'{{=sum(G{brow}:G{crow})}}', cellTimeTotalFormat)
    colLetter = 'G'

    

  
  typeCell = 'desarrollo'
  ## write cellds contexto['all_regtrabajodesarrollo']
  for it in contexto['all_regtrabajodesarrollo']:
    """ Modelo de la tabla para Hilo del Historial de registros de trabajo de un ticket.
      * desarrollo      : Ticket sobre el cual se registrara el trabajo, Modelo Tickets
      * register_work   : quien registra el trabajo sobre el ticket en cuestion, Modelo Programador    
      * fecha_creacion  : Fecha en la cual se creo el registro del nuevo trabajo.    
      * msg             : Detalle del trabajo realizado o mensage descriptivo.    
      * file1           : Archivo para acompañar el detalle del trabajo realizado.
      * file2           : Archivo para acompañar el detalle del trabajo realizado.    
      * tiempo          : Tiempo consumido para realizar el trabajo.    
      * date_update     : Hora y Fecha de actualizacion del registro.
      * programmer      : True | False , especifica si es programador quien registra
    """
    
    # if(it.programmer == True):
    #   typeCell = 'attend'
    # else:
    #   typeCell = 'register'

    ## ID del workregister
    ccol = 0
    worksheet_s.write_number(crow, ccol, it.id, cellFormatCent[typeCell])
    ## ID del ticket,
    ccol += 1
    
    if(it.desarrollo.estado == True):
      worksheet_s.write_number(crow, ccol, it.desarrollo.id, cellFormatTicket['open'])
    else:
      worksheet_s.write_number(crow, ccol, it.desarrollo.id, cellFormatTicket['close'])

    if('empresa' not in contexto.keys() ):
      ccol += 1      
      if(it.desarrollo.empresa != None):
        worksheet_s.write_string(crow, ccol, f'{it.desarrollo.empresa.nombre}', cellFormatCent[typeCell])        
      else:
        worksheet_s.write_string(crow, ccol, 'Interno', cellFormatCent[typeCell])

    ccol += 1      
    worksheet_s.write_string(crow, ccol, f'{it.register_work.username}', cellFormatCent[typeCell])
    ccol += 1
    worksheet_s.write_datetime(crow, ccol, it.fecha_creacion, cellDateTimeFormat[typeCell])
    ccol += 1
    ## para mensajes multilinea    
    a = computeRows(f'{it.msg}',header_labels['Trabajo Realizado'],12)      
    worksheet_s.write_string(crow, ccol, a['rtext'], cellFormatCent[typeCell])
    worksheet_s.set_row(crow, a['nrow'])

    ccol += 1
    if(it.programmer):        
      worksheet_s.write_datetime(crow, ccol, it.tiempo, cellTimeFormat[typeCell])
    else:
      worksheet_s.write_datetime(crow, ccol, time(0,0,0), cellTimeFormat[typeCell])

    ccol += 1
    worksheet_s.write_datetime(crow, ccol, it.date_update, cellDateTimeFormat[typeCell])

    crow += 1
  ## endfor  



  worksheet_s.write_formula(4,4, f'{{=sum({colLetter}{brow}:{colLetter}{crow})}}', cellTimeTotalFormat)


  ## write leyend
  crow += 4  
  if(len(contexto['all_regtrabajodesarrollo']) > 0):
    worksheet_s.write_string(crow, 2, "Desarrollos", cellFormatCent['desarrollo'])

  if(flagRegister == True):
    worksheet_s.write_string(crow, 3, "Mensajes Clientes", cellFormatCent['register'])

  worksheet_s.write_string(crow, 1, "Ticket Open", cellFormatTicket['open'])
  crow += 1
  worksheet_s.write_string(crow, 1, "Ticket Close", cellFormatTicket['close'])
  crow += 1
  worksheet_s.write_string(crow, 1, "Ticket Pending", cellFormatTicket['pending'])

  ##
  workbook.close()
  xlsx_data = output.getvalue()
  # xlsx_data contains the Excel file
  return xlsx_data
  
