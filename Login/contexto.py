from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.contrib.auth.models import Group , Permission ,PermissionsMixin
from config.apps import debug_print , str2systemdate
from config.settings import HOSTING_URL, EMAIL_HOST_USER,EMAIL_REPLY_TO,EMAIL_SEND_RETRY
from .models import User 
from Contact.models import Contact
import sys
import threading , time
from django.db.models.query import QuerySet
from django.db.models import Q

from datetime import datetime
import random
from config.settings import PUESTA_PRODUCTION
LABELS_GROUPS_PROGRAMADOR = 'Programador'
LABELS_GROUPS_CLIENTE = 'Cliente'
LABELS_GROUPS_ADMIN = 'Administrador'

'''
  luser: cliente01 luser.get_group_permissions: {'Contact.register'}
  luser: programador01 luser.get_group_permissions: {'Contact.attend'}
  luser: administrador01 luser.get_group_permissions: {'Contact.admin'}
'''
LABELS_PERM_PROGRAMADOR = 'Contact.attend'
LABELS_PERM_CLIENTE = 'Contact.register'
LABELS_PERM_ADMIN = 'Contact.admin'

def CheckUserget_current_attend(**args):
  '''
    @brief funcion para obetener el attend actualmente logeado
    @param args :
      + contex= 'Contexto -> request'
    
    @return el usuario/username del attend actual, de lo contrario
    (no tiene un registro dentro de la tabla Programador) retorna None
  '''
  if('contex' in args.keys()):
    ##
    try:
      return User.objects.filter(id=args['contex'].id)[0]
    except:      
      return None

  else:  
    ## args erroneo
    return None


def get_current_register(**args):
  if('contex' in args.keys()):
    ## 
    try:
      return args['contex'].user.id

    except:      
      return None

  else:  
    ## args erroneo
    return None    


def is_attend(**args):
  if('contex' in args.keys()):
    ## query para verificar si es programador, o attend del ticket
    if(User.objects.filter(id=args['contex'].id)):
      return True
    else:
      return False

  else:  
    ## args erroneo
    return False

def is_register(**args):
  ## por decantacion, en caso de no tener un modelo Cliente:
  if('contex' in args.keys()):
    ## query para verificar si es programador, o attend del ticket
    if(not User.objects.filter(id=args['contex'].id)):
      return True
    else:
      return False

  else:  
    ## args erroneo
    return False



def GetGroupCurrentUser(**args):
  """
    @brief funcion para obtener el grupo actual de un usuario, si este tiene uno asignado dentro 
    de la familia de grupo establecidos.
    @param args :    
      + user = objetct User ==> {client | programador | admin | superuser}
      
    @return 
      + Failure:  None        
      + Success: 'client'  | 'programador' | 'admin' | 'superuser'
  """
  luser = args.get('user',None)
  if(luser == None):
    return None
  if(isinstance(luser,User)==False):
    ## debemos agregar la opcion de resques.user
    return None

  target_user = {LABELS_GROUPS_CLIENTE:'client' ,LABELS_GROUPS_PROGRAMADOR:'programador',LABELS_GROUPS_ADMIN:'admin'}
  userGroups = luser.groups.all()
  for it in userGroups:
    strit = f'{it}'
    # debug_print(f'it: {it}, target_user.keys() : {target_user.keys()}')
    if(strit in target_user.keys()):
      return target_user[strit]
  # Consultamos si el User es sueruser
  try:
    if(luser.is_superuser == True):
      return 'superuser'    
  except:  
    debug_print(f'User {luser}, no tiene grupo asignado')
  ## ojo no podemos colocar finaly ya que formzamos la salida por este bloque y descarta el retirn de try  
  return None


def CheckCurrentUser(**args):
  """
    @brief funcion para chequear el usaurio actual
    @param args :    
      + user = client | programador | admin | superuser
      + req = request
      + ticket_id, devuelve un ticket relasionado al user "menos para superuser"
    @return 
      + Failure:  
        None        
      + success: 
        dict  { 'user': obj, 'ticket': obj "Opcional"
              , 'ticket_access': {True|False},'': obj}
          'user' : si es cliente User, si es programador Programador, Admin => User, Es mandatorio.
          'is_superuser': True|False si el usuario es superuser, Es mandatorio
  """
  usertype = args.get('user',None)
  request = args.get('req',None)  
  target_user = {'client':LABELS_GROUPS_CLIENTE ,'programador':LABELS_GROUPS_PROGRAMADOR,'admin':LABELS_GROUPS_ADMIN}
  
  if(usertype == None or request == None):
    return None

  if(usertype not in target_user.keys() and usertype != 'superuser'):
    return None
  
  is_superuser = False

  try:
    luser = None    
    if(usertype != 'superuser' ):
      luser = User.objects.filter(groups=Group.objects.get(name = target_user[usertype]),username=request.user)[0]
    else:
      luser = User.objects.filter(is_superuser=True,username=request.user)[0]
      is_superuser = bool(luser)
    
  except:    
    luser = None    
    
  finally:    
    if(luser == None and (usertype != 'admin' and usertype != 'superuser' )):      
      return None
    
    elif(luser == None and (usertype == 'superuser' or usertype == 'admin')):
      try:
        luser = User.objects.filter(is_superuser=True,username=request.user)[0]
        is_superuser = bool(luser)

      except:        
        return None

    elif(luser == None):
      return None
   
  return {'user': luser, 'is_superuser':is_superuser}
  
def GetGroupUsers(**args):
  """
    @fn def GetGroupUsers(**args):
    @brief funcion para chequear el usaurio actual
    @param args :    
      + user = client | programador | admin 

    @return 
      + Failure:  
        None        
      + success: 
        dict  { 'user': obj, 'ticket': obj "Opcional"
              , 'ticket_access': {True|False},'': obj}
          'user' : si es cliente User, si es programador Programador, Admin => User, Es mandatorio.
          'is_superuser': True|False si el usuario es superuser, Es mandatorio          
  """
  usertype = args.get('user',None)
  target_user = {'client':LABELS_GROUPS_CLIENTE ,'programador':LABELS_GROUPS_PROGRAMADOR,'admin':LABELS_GROUPS_ADMIN}
  
  if(usertype == None or usertype not in target_user.keys() and usertype != 'superuser'):
    return None

  
  rval = None 
  try:        
    rval = User.objects.filter(groups=Group.objects.get(name = target_user[usertype]))    
  except:
    debug_print(f'error {sys.exc_info()[1]} al obtener el tipo de usuario {usertype}')
    rval = None

  #debug_print(f' rval: {rval}')

  

  return rval
      


def GetEmailList(**args):
  """
    @brief funcion para obtener el listado de meil de un grupo particular
    @param args :    
      + grupo = admin | empresa | programador       
      
    @return 
      + Failure:  
        []

      + success: 
        list ['user': obj, 'ticket': obj, '': obj]
  """
  allUsers = None           
  try:
    allUsers = User.objects.filter(groups=Group.objects.get(name = LABELS_GROUPS_ADMIN))
  except:
    debug_print(f"failure: query User.objects.filter(groups=Group.objects.get(name = {LABELS_GROUPS_ADMIN}) => {sys.exc_info()[0]}")
  
  # targetUser = ('admin' , 'empresas' , 'programador')
  if(allUsers == None or len(allUsers) == 0):
    return []
  rval = []

  for it in allUsers:
    if(it.email in (None,'')):
      continue
    rval.append(it.email)  

  return rval

def executeQuery(**args):
  """
    FIXME copy executeFindQuery() debemos generalizarla, sacaar exclude y agregar where.

    @fn def executeQuery(**args):
    @brief Funcion que ejecuta query
    @args :
      * table     : Objeto ORM que representa la tabla BBDD, Mandatorio.
      * order_by  : { False  'por defecto' creciente | True : orden decreciente } por id.
      * column    : target, Nombre de la columna de la tabla. Por defecto 'all'.
      * value     : Valor de comparacion, si column no es pasado la query se descarta de lo contrario 
                    es mandatorio. Toma un Rol Condicional.

      + exclude   : { False 'por defecto' : True }
      + check_rval : { False 'por defecto' : True cheque el valor devuelto en caso de causualas where distinta a 'equal' }
      FIXME:
        <> Debemos sacar "exclude"
       where : Opcional si no es pasado pero si column y value se toma el la comparacion ==
        *  ==
        *  !=
        *  >
        *  <
        
  """
  object = args.get('table',None)  
  orderdec = args.get('order_by',False)
  target = args.get('column',None)
  query = args.get('value',None)
  ## FIXME debemos sacar este y considerar la variable Target
  inversion = args.get('exclude',False)
  check_rval = args.get('check_rval',False)
  # where = args.get('where','==')

  if((target == None and query != None) or (target != None and query == None)):
    return None

  ## filter LIKE para busqueda
  target = f'{target}__contains'
  rval = None
  try:
    if(target == None ):
      if(orderdec):
        rval = object.objects.all().order_by('-id')
      else:
        rval = object.objects.all()

    elif(inversion == True and orderdec == True):
      rval = object.objects.filter(~Q(**{target:f'{query}'})).order_by('-id')

    elif(inversion == True and orderdec == False):
      rval = object.objects.filter(~Q(**{target:f'{query}'}))

    elif(inversion == False and orderdec == True):
      rval = object.objects.filter(**{target:f'{query}'}).order_by('-id')
    
    else:
      rval = object.objects.filter(**{target:f'{query}'})
  except:
    debug_print(f'fail to query object.objects.filter({target} = {query}), inversion: {inversion} \t orderdec: {orderdec} ')
    return None


  if(check_rval == False or rval == None):
    return rval

  AllColumn = object.objects.all()
  if(len(AllColumn) == len(rval)):
    return None
  
  return rval

def executeFindQuery(**args):
  """
    @fn def executeQuery(**args):
    @brief Funcion que ejecuta query
    @args :
      * table     : Objeto ORM que representa la tabla BBDD, Mandatorio.
      * order_by  : { False  'por defecto' creciente | True : orden decreciente } por id.
      * column    : target, Nombre de la columna de la tabla. Por defecto 'all'.
      * value     : Valor de comparacion, si column no es pasado la query se descarta de lo contrario 
                    es mandatorio. Toma un Rol Condicional.
      * exclude   : { False 'por defecto' : True }
      * check_rval : { False 'por defecto' : True cheque el valor devuelto en caso de causualas where distinta a 'equal' 
      * like      : toma cada fila cuyo contenido, contenga el value ==> Clausula LIKE "SELECT id FROM ... WHERE NAME LIKE '%Cheddar%'"
                    por defecto este esta habilitado, para columnas que sean referencias a otra tablas debemos deshabilitar este
                    'like=False'
      * filter    : un dictionario con pre filtro

    @return el resutlado de la query o None.
  """
  object = args.get('table',None)  
  orderdec = args.get('order_by',False)
  target = args.get('column',None)
  query = args.get('value',None)
  ## FIXME debemos sacar este y considerar la variable Target
  inversion = args.get('exclude',False)
  check_rval = args.get('check_rval',False)
  like = args.get('like',True)
  # where = args.get('where','==')

  # if((target == None and query != None) or (target != None and query == None)):
  if(target == None and query != None):
    return None

  rval = None
  filterQueryMain = args.get('filter',None)
  filterQuery = None

  ## filter LIKE para busqueda del tipo indexado
  if(target != None):
    if(like == True):
      target = f'{target}__contains'
    else:
      target = f'{target}'
    
    if(isinstance(query,str)):
      if(inversion == True):
        filterQuery = ~Q(**{target:f'{query}'})

      else:
        filterQuery = Q(**{target:f'{query}'})

    else:
      if(inversion == True):
        filterQuery = ~Q(**{target:query})

      else:
        filterQuery = Q(**{target:query})

  try:
    if(target == None and filterQueryMain == None):
      rval = object.objects.all()
      # debug_print(f'rval:{rval} ')
      # if(orderdec):
      #   rval = object.objects.all().order_by('-id')
      # else:
      #   rval = object.objects.all()
    elif(target == None and filterQueryMain != None):
      # debug_print(f'filterQuery:{filterQuery} \t filterQueryMain:{Q(filterQueryMain)} ')      
      rval = object.objects.filter(**filterQueryMain)

    elif(target != None and filterQueryMain != None):
      # debug_print(f'filterQuery:{filterQuery} \t filterQueryMain:{Q(filterQueryMain)} ')      
      rval = object.objects.filter(filterQuery, **filterQueryMain)
    else:
      rval = object.objects.filter(filterQuery)
      
  except:    
    err = sys.exc_info()[1]
    debug_print(f'fail "{err}" to query {object}.objects.filter({target} = {query}), inversion: {inversion} \t orderdec: {orderdec} \t like : {like}')
    return None

  if(orderdec):    
    ## invertimos y alamacenamos el nuevo orden
    rval = rval.order_by('-id')    

  if(check_rval == False or rval == None):
    return rval

  AllColumn = object.objects.all()
  if(len(AllColumn) == len(rval)):
    return None
  
  return rval

def getDataFromFilter(**args):
  """
    @fn def getDataFromFilter(**args):
    @brief funcion para obtener datos desde la BBDD
    para una query y objeto especifico.
    @param : args
      * object  : Objeto ORM al cual se le quiere aplicacar al query
      * q       : Query proveniente del filtro de la vista: q = request.GET.get('q', None)
      * rdict   : True|False, Opcional con este habilitamos la devolucion de un diccionario 
                  con el resultado.
      * filter  : Diccionario con el filtro a aplicar, no es mandatorio.

    @return 
      * success : lista de resutlados, en caso de no tener resultados retorna None.
                  Si se habilito rdict = True, retornamos el resultado en un diccionario
                  En este se especifica Nombre de Objeto y resultado de la query. Para llegar al resultado final.
                  {'rval': ResultadoQuery, 'Object':<ResultadoQuery p/Object> , ...}
      * failure : retorna None e inserta msg en el log, respecto
  """
  object = args.get('object',None)
  query = args.get('q',None)
  rv = args.get('rdict',False)
  preFiltro = args.get('filter',None)
  if(object == None or query == None or query == ''):
    return None
  
  """
    Implementacion de Operadores de concatenacion de querys
      + '|'   : or
       FIXME:
      + '^'   : concatenacion, "Cambiamos ya que el numero de telefono lleva '+' delante". 
      + '-'   : Orden descendiente del resultado en funcion del 'id' de la tabla encuestada.                
      + '&'   : and, se realiza una and/interseccion entre query target.
      + '=='  : deshabilita el LIKE en la clausula de busqueda, se espera '==' pero se pregunta por '=' ya que es un 
                caracter especial para el POST/GET
  """
  
  if('|' in query):
    ## tenemos clausual or, devolvemos la primera que arroje resultados
    listQuery = query.split('|')
    # debug_print(f'tmpQuery: {listQuery}')
    rval = None
    for lq in listQuery:
      # rval = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv)
      rval = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv,filter=preFiltro)
      if(rval != None):
        return rval
    if(rval != None and len(rval) == 0):
      return None
    
    return rval
  ## end if

  ## endif
  if('^' in query):
    ## tenemos clausual concatenacion, devolvemos la concatenacion de la query
    listQuery = query.split('^')
    # debug_print(f'tmpQuery: {listQuery}')
    
    rval = None
    # if(rv == True):
    #   rval = {}
    
    for lq in listQuery:
      # rval = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv)
      # lr = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv)
      lr = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv,filter=preFiltro)
      # debug_print(f'lr: {lr}')
      if(lr == None):
        continue

      if(rv == True):
        ## debemos extender los contenidos con la claves
        #  rval
        if(rval == None):
          rval = lr
          # rval.update(lr)
          # rval = lr
        else:
          ## concatenamos dos QuerySet:
          for key in rval.keys():
            if(rval[key] != None and lr[key] != None):
              tmp = rval[key] | lr[key]
              rval[key] = tmp
              continue

            elif(rval[key] == None and lr[key] != None):              
              rval[key] = lr[key]
              continue

            elif(rval[key] != None and lr[key] == None):
              continue

            elif(rval[key] == None and lr[key] == None):
              continue
          # tmp = rval['rval'] | lr["rval"]
          # rval['rval'] = tmp
      else:
        if(rval == None):
          rval = lr
        else:
          tmp = rval | lr
          rval = tmp
        # rval.extend(lr)
      
    if(rval != None and len(rval) == 0):
      return None
    
    # debug_print(f'getDataFromFilter.rval: {getDataFromFilter.rval}')
    return rval
  
  ## end if

  if('&' in query):
    ## tenemos clausual or, devolvemos la primera que arroje resultados
    listQuery = query.split('&')
    # debug_print(f'tmpQuery: {listQuery}')
    
    rval = None

    
    for lq in listQuery:
      # lr = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv)
      lr = getDataFromFilter(q=lq.strip(),object=args.get('object',None),rdict=rv,filter=preFiltro)
      
      # debug_print(f'lr: {lr}')
      if(lr == None):
        continue

      if(rv == True):
        ## debemos extender los contenidos con la claves        
        if(rval == None ):
          rval = lr
          # rval = lr
        else:
          ## concatenamos dos QuerySet:
          for key in rval.keys():
            if(rval[key] != None and lr[key] != None):
              tmp = rval[key] & lr[key]
              rval[key] = tmp
              continue

            elif(rval[key] == None and lr[key] != None):              
              rval[key] = lr[key]
              continue

            elif(rval[key] != None and lr[key] == None):
              continue

            elif(rval[key] == None and lr[key] == None):
              continue
          # tmp = rval['rval'] | lr["rval"]
          # rval['rval'] = tmp
      else:
        if(rval == None ):
          rval = lr

        tmp = rval & lr
        rval = tmp
        # rval.extend(lr)
      
    if(rval != None and len(rval) == 0):
      return None
    
    # debug_print(f'getDataFromFilter.rval: {getDataFromFilter.rval}')
    return rval
  
  ## end if  


  if(query[0] == '='):
    query = query[1:]
    like = False
    
  char_target = {'!': False ,'-': False ,'=':True}  
  i = 0
  
  ## Busqeda iteractiva
  getItem = False
  try:
    while True:
      for it in char_target.keys():
        if(query[0] == it):
          char_target[it] = not char_target[it]
          query = query[1:]                  
          getItem = True
          break
      ## endfor
      if(getItem == True):
        getItem = False
        continue
      break
  except IndexError:
    ## pasamos la cadena solo alguno de los char_target sin quien comparar/buscar
    return None


  # debug_print(f'char_target: {char_target} \t query: {query} \t i:{i}')
  
  inversion = char_target['!']
  orderdec = char_target['-']
  tlike = char_target['=']

 
  # debug_print(f'query : {query} <==> {inversion}')
  ## en caso de habilitar el rdict
  # rdict = None

  # if(isinstance(object, User) == True):
  if(object == User):
    ## busqueda de usuarios por la query, consideramos que son usaurios no Programadores | administradores | root
    
    ## FIXME add filter nested
    # preFiltro = args.get('filter',None)
    # debug_print(f'filtroUser: {preFiltro}')
    if(query in ('all','All','ALL')):
      client_all = executeFindQuery(table=User,exclude=inversion,order_by=orderdec,filter=preFiltro)
      #debug_print(f'client_all:{client_all} ')

    else:
      querySet = ('username','first_name','last_name','email','telefono','id')
      client_all = None
      for it in querySet:
        
        client_all = executeFindQuery(filter=preFiltro,table=User,exclude=inversion\
            ,order_by=orderdec,column=it,value=query,check_rval=True,like=tlike)

        if(client_all != None and len(client_all) > 0 ):
          break 

      ## end for

    if( client_all != None and len(client_all) > 0):
      tmp = User.objects.filter(~Q(empresa = None)) & client_all
      client_all = tmp

    if(client_all == None or (client_all != None and len(client_all) == 0)):
      ## query puede ser el nombre de una empresa 
      empresaid = None


      try:
        if(inversion == True):
          empresaid = Empresa.objects.filter(~Q(nombre__contains=query))[0]
        else:
          empresaid = Empresa.objects.filter(nombre__contains=query)[0]
        # debug_print(f"Query : Empresa.objects.filter(nombre__contains={query})[0] = {empresaid} ")
      except:
        pass
        # debug_print(f"No tenemos Empresa con ese nombre: {query}.")
      if(empresaid != None):
        client_all = executeFindQuery(table=User,order_by=orderdec,column='empresa',value=empresaid,like=False)
        # debug_print(f'client_all: {client_all}')

    ## end if

    if(client_all == None or len(client_all) == 0):
      return None     

    tmp = User.objects.filter(~Q(empresa = None)) & client_all
    client_all = tmp

    # if(len(client_all) < 1):
    #   return None
    
    if(rv == True):
      return {'rval':client_all,'Empresa':empresaid}
      
    return client_all
  ## end if  


  if(object == Contact):
    userAll = None
    empresaAll = None
    programadorAll = None
    all_modulos = None
    all_ticket = None

    CountTicket = 0
    try:
      CountTicket = len(Contact.objects.all())
    except:
      err = sys.exc_info()[1]
      debug_print(f'failure {err} :  len(Tickets.objects.all())')
      return None

    while(1):
      ## 1) id
      td_id = None
      try:
        td_id = int(query)
        all_ticket = executeFindQuery(table=Contact,exclude=inversion,filter=preFiltro \
          ,order_by=orderdec,column='id',value=td_id,check_rval=True,like=tlike)
        break
      except:
        all_ticket = None
        # debug_print(f'all_ticket = [Tickets.objects.get(id={td_id})]')
      
      ## 2) True or false
      # if(all_ticket == None and query in ('True','False')):
      if(query in ('True','False')):
        boolfilter = False
        if(query == 'True'):
          boolfilter = True

        if(inversion == True):
            boolfilter = not boolfilter
        try:          
          all_ticket = object.objects.filter(estado=boolfilter,**preFiltro)
        except:
          all_ticket = None

        if(all_ticket != None and orderdec == True):
          all_ticket = all_ticket.order_by('-id')

        break
      ## 3) None -> attend : Sin atender o sin asistente asigndao
      if(query == 'None'):
        all_ticket = executeFindQuery(table=Contact,exclude=inversion,filter=preFiltro\
            ,order_by=orderdec,column='attend',value=None,check_rval=True,like=False)
        # debug_print(f'all_ticket : {all_ticket}')
        break 

      ## 5) empresa
      """
        inversion = char_target['!']
        orderdec = char_target['-']
        tlike = char_target['=']
      """
      orderWord = None      
      queryTarget = None
      columnTarget = None


      if(tlike == True):
        columnTarget = 'nombre__contains'
      else:
        columnTarget = 'nombre'

      if(inversion == True):
        queryTarget = ~Q(**{columnTarget:f'{query}'})
      else:
        queryTarget = Q(**{columnTarget:f'{query}'})
        

      ticketclient = None
      try: 
        empresapeeq = Empresa.objects.filter(queryTarget).values('nombre')        
        # debug_print(f'userpeeq: {userpeeq}')

        userpeeq = User.objects.filter(**{f'empresa__nombre__in':empresapeeq})
        # debug_print(f'prgpeeq: {prgpeeq}')

        # ticketclient = Tickets.objects.filter(**{f'register__in':userpeeq}).order_by(orderWord)
        ticketclient = Contact.objects.filter(**{f'register__in':userpeeq},**preFiltro)
        # debug_print(f'ticketclient: {ticketclient}')
        if(orderdec == True):
          ticketclient = ticketclient.order_by('-id')

      except:
        err = sys.exc_info()[1]
        debug_print(f'fail: {err} query: {query} it: {it}')

      if(ticketclient != None and (len(ticketclient) < CountTicket and len(ticketclient) > 0)):
        all_ticket = ticketclient     
        break

      ## 4) username | first_name | last_name -> client | attend
      querySet = ('username','first_name','last_name')

      ## TODO REGISTER or ATTEND 
      ticketclient = None
      orderWord = None      
      queryTarget = None
      columnTarget = None

      if(orderdec == True):
        orderWord = '-id'
      else:
        orderWord = 'id'


      if(tlike == True):
        columnTarget = 'nombre__contains'
      else:
        columnTarget = 'nombre'

      if(inversion == True):
        queryTarget = ~Q(**{columnTarget:f'{query}'})
      else:
        queryTarget = Q(**{columnTarget:f'{query}'})

      '''
        SELECT ... WHERE blog.id IN (SELECT id FROM ... WHERE NAME LIKE '%Cheddar%')

        inner_qs = Blog.objects.filter(name__contains='Ch').values('name')
        entries = Entry.objects.filter(blog__name__in=inner_qs)
      '''              
      for it in querySet:
        
        userpeeq = None
        try:
          if(tlike == True):
            columnTarget = f'{it}__contains'
          else:
            columnTarget = it

          if(inversion == True):
            queryTarget = ~Q(**{columnTarget:f'{query}'})
          else:
            queryTarget = Q(**{columnTarget:f'{query}'})

          userpeeq = User.objects.filter(queryTarget).values(it)
          # userpeeq = User.objects.filter(Q(**{f'{it}__contains':f'{query}'})).values(it)
          debug_print(f'userpeeq: {userpeeq}')

        except:
          err = sys.exc_info()[1]
          debug_print(f'fail: {err} User.objects.filter(Q("{it}__contains" = {query})).values({it})')
          continue

        try:
          # ticketclient = Tickets.objects.filter(**{f'register__{it}__in':userpeeq}).order_by(orderWord)
          ticketclient = Tickets.objects.filter(**{f'register__{it}__in':userpeeq},**preFiltro)
          if(orderdec == True):
            ticketclient.order_by('-id')

          # debug_print(f'ticketclient: {ticketclient}')
          if(len(ticketclient) < CountTicket and len(ticketclient) > 0):
            break
        except:
          err = sys.exc_info()[1]
          debug_print(f'fail: {err} query: {query} it: {it}')

        try:          
          prgpeeq = Programador.objects.filter(**{f'programador__{it}__in':userpeeq}).order_by(orderWord)
          debug_print(f'prgpeeq: {prgpeeq}')       
          ticketclient = Tickets.objects.filter(**{f'attend__in':prgpeeq},**preFiltro)
          debug_print(f'ticketclient: {ticketclient}')
          if(len(ticketclient) >= 0):
            break
        except:
          err = sys.exc_info()[1]
          debug_print(f'fail: {err} query: {query} it: {it}')

      ## endfor

      if(ticketclient != None and (len(ticketclient) < CountTicket and len(ticketclient) > 0)):
        all_ticket = ticketclient
        break
      
            
      ## 6) Module = Nombre de Modulo      
      orderWord = None      
      queryTarget = None
      columnTarget = None

      if(orderdec == True):
        orderWord = '-id'
      else:
        orderWord = 'id'

      if(tlike == True):
        columnTarget = 'nombre__contains'        
      else:
        columnTarget = 'nombre'

      if(inversion == True):
        queryTarget = ~Q(**{columnTarget:f'{query}'})
      else:
        queryTarget = Q(**{columnTarget:f'{query}'})
        

      ticketclient = None
      try: 
        modulospeeq = Modulos.objects.filter(queryTarget).values('nombre')        
        # debug_print(f'userpeeq: {modulospeeq}')

        # ticketclient = Tickets.objects.filter(**{f'brief__nombre__in':modulospeeq}).order_by(orderWord)
        ticketclient = Tickets.objects.filter(**{f'brief__nombre__in':modulospeeq},**preFiltro)
        # debug_print(f'ticketclient: {ticketclient}')

        if(orderdec == True):
          ticketclient = ticketclient.order_by('-id')

      except:
        err = sys.exc_info()[1]
        debug_print(f'fail: {err} query: {query} it: {it}')

      if(ticketclient != None and (len(ticketclient) < CountTicket and len(ticketclient) > 0)):
        all_ticket = ticketclient     
        break

      ## fin del bucle
      break
    # end while(1)

    ## default
    if(all_ticket != None and len(all_ticket) == 0):
      return None
    
    if(rv == True):
      return {'rval':all_ticket,'Modulos':all_modulos,'User':userAll,'Empresa':empresaAll,'Programador':programadorAll}

    return all_ticket
  ## end if

  ## FIXME: add filters
  if(object == Modulos):
    querySet = ('nombre','id',)
    modulo_all = None
    for it in querySet:
      modulo_all = executeFindQuery(table=Modulos,exclude=inversion,order_by=orderdec,column=it,value=query,check_rval=True,like=tlike)
      if(modulo_all != None and len(modulo_all) > 0 ):
        break  
    ## end for    

    if(modulo_all == None or len(modulo_all) == 0):
      return None

    
    if(rv == True):
      return {'rval':modulo_all,}
      
    return modulo_all        
  ## end if

  if(object == Empresa):
    querySet = ('nombre','id','email','telefono1')
    empresa_all = None

    # debug_print(f'query: {query}')

    for it in querySet:
      empresa_all = executeFindQuery(table=Empresa,exclude=inversion,order_by=orderdec,column=it,value=query,check_rval=True,like=tlike)
      if(empresa_all != None and len(empresa_all) > 0 ):
        break        
    ## end for

    if(empresa_all == None or len(empresa_all) == 0):
      return None
    
    if(rv == True):
      return {'rval':empresa_all,}
      
    return empresa_all
  ## end if

  return None


letterToNumber = {'a':4 , 'b':8, 'e':3, 'i':1, 'o':0, 'q':9,'s':5 , 'p':2}
numberToLetter = {'4':'a' , '8':'b', '3':'e', '1':'i', '0':'o', '9':'q','5':'s' , '2':'p' }

def cifra2name(cifra:int) -> str:
  """
    Funcion para convertir una cifra numerica en string
    en una cifra de nombre conformada por numero y letras, dentro de un string
    * cifra : cifra numerica como string
  """
  scifra = str(cifra)
  rval = ''
  for it in scifra:    
    if it in numberToLetter.keys():
      rval += numberToLetter[it]
    else:
      rval += it
  return rval

def getPassFromUsername(**args) -> str:
  """
    @param args:
      * username : user name
  """
  username = args.get('username',None)
  if(username == None or isinstance(username,str) == False):
    return None

  rval = ''
  for it in username.lower():    
    if it in letterToNumber.keys():
      rval += str(letterToNumber[it])
    else:
      rval += it
  ##endfor
  if(len(rval) < 5):
    random.seed(int(datetime.now().strftime('%Y%m%d%H%M%S%f')))    
    a = random.randrange(1, ((1024*1024)/pow(2,len(rval))) )
    #a = random.randrange(1, pow(2,pow(2,len(rval))))
    rval += cifra2name(a)
    #rval += datetime.now().strftime('%Y%m%d')
  return rval

  

'''
  Clase para obtener el 
  choice de forma estatica, para no perder la seleccion
  cuando se desea reordenar una columna
  en particular
'''
class Choice:
  _id_choice = None

  def get(self,**args):
    """
      @fn
      @brief
      @param args:
        * post
        * groups
    """
    post = args.get('post',None)
    groups = args.get('groups','choice')

    if(groups in post.keys()):
      type(self)._id_choice=post[groups]
    else:
      return None
    return type(self)._id_choice

  def set(self,**args):
    if('id_choice' in args.keys()):
      type(self)._id_choice = args['id_choice']
      return 
    else :
      return

  id_choice = property(get)



class EmailThread(threading.Thread):
  def __init__(self,**args):
    """
      @param args :
        + attend : False|True , indicamos 'True' si debemos mandarle el meil al programador y no al cliente. Por defecto es False
        + registro
        + msg
        + header        
        + email : dict {}
              'headerbody': <>
              'body':<>
              'from':<>
              'tolist':<>
              'reply':<>
              'header':<>
        + object : object con arg         'email_status' and 'err_email' 
    """
    self.retry = EMAIL_SEND_RETRY
    registro = args.get('registro',None)
    msg = args.get('msg','')
    # attend = args.get('attend',False)
    self.header = args.get('header','')    
    password = args.get('password',None)
    self.meilList = None
    self.email = None
    self.object = args.get('object',None)

    if(registro != None):
      '''
      if(attend == False and isinstance(registro,RegisterWork) == True):
        if(isinstance(registro.ticket.email,str)):
          self.meilList = registro.ticket.email.split()
        else:
          self.meilList = registro.ticket.email

        

        if(not registro.ticket.register.email in self.meilList and registro.ticket.register.email != '' ):
          self.meilList.append(registro.ticket.register.email)

        # debug_print(f'self.meilList : {self.meilList}')

        # emailinfo = { 'tolist':listMailClient
        #   ,'headerbody': f'{header}' \
        #   ,'body': f'{msg}' \
        #   ,'header' : {'Message-ID': f'REG-{registro.id}'} }

        # emailinfo['body'] += f'\nMensaje: \n{registro.msg}'
        self.msgBody = f'{msg} url: {HOSTING_URL}/register_ticket/expand_ticket/{registro.ticket.id}/'
        self.msgBody += f'\nMensaje: \n{registro.msg}'
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return

      if(attend == True and isinstance(registro,RegisterWork) == True):

        url = None
        # meilList = None
        if(registro.ticket.attend != None):
          self.meilList = [registro.ticket.attend.programador.email]
          url = f'url: {HOSTING_URL}/attend_ticket/expand_attend_ticket/{registro.ticket.id}/'
        else:
          self.meilList = GetEmailList(grupo='admin')
          ## FIXME debemos ajustarlo a RegisterWork, esta url es del ticket
          url = f'url: {HOSTING_URL}/login/edit_ticket_register/{registro.ticket.id}/'
        # debug_print(f'self.meilList : {self.meilList}')
        self.msgBody = f'{msg} {url}'
        self.msgBody += f'\nMensaje: \n{registro.msg}' 
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return

      if(attend == False and isinstance(registro,Tickets) == True):
        url = None
        # meilList = None
        if(isinstance(registro.email,str)):
          self.meilList = registro.email.split()
        else:
          self.meilList = registro.email 
        
        if(not registro.register.email in self.meilList and registro.register.email != ''):
          self.meilList.append(registro.register.email)

        url = f'{HOSTING_URL}/register_ticket/expand_ticket/{registro.id}/'

        self.msgBody = f'{msg} {url}'
        self.msgBody += f'\nModulo: \n\t{registro.brief}'
        self.msgBody += f'\nMensaje: \n\t{registro.detail}'

        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return
        
      if(attend == True and isinstance(registro,Tickets) == True):

        url = None        
        if(registro.attend != None):
          self.meilList = [registro.attend.programador.email,]
          url = f'url: {HOSTING_URL}/attend_ticket/expand_attend_ticket/{registro.id}/'
        else:
          self.meilList = GetEmailList(grupo='admin')
          url = f'url: {HOSTING_URL}/login/edit_ticket_register/{registro.id}/'

        # debug_print(f'self.meilList : {self.meilList}')
          
        

        self.msgBody = f'{msg} {url}'
        self.msgBody += f'\nModulo: \n\t{registro.brief}'
        self.msgBody += f'\nMensaje: \n\t{registro.detail}'
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return
      '''


      if(isinstance(registro,User) == True):
        ## Consultamos a que tipo de user corresponde, superuser | Administrador | Programador | Cliente
        
        grupo = GetGroupCurrentUser(user=registro)
        if(grupo == None):
          debug_print(f'Usuario {registro} con grupo fuera de rango')
          threading.Thread.__init__(self)
          return
        
        url = f'url: {HOSTING_URL}/login/view_users/{registro.id}/'
        if(registro.email not in (None,'')):
          self.meilList = [registro.email]            
          self.msgBody = f'{msg} {url}'

        else:
          if(grupo == 'client'):          
            if(registro.empresa != None and registro.empresa.email not in (None,'')):
              self.msgBody = f'{msg}'
              self.meilList = [registro.empresa.email]
            else:
              ## No tenemos listado de meil para el
              threading.Thread.__init__(self)
              return
            """
              if(registro.email != None):
                self.meilList = [registro.email]
                # url = f'url: {HOSTING_URL}/login/view_users/{registro.id}/'
                self.msgBody = f'{msg} {url}'
              elif(registro.empresa != None and registro.empresa.email != None):
                self.msgBody = f'{msg}'
                self.meilList = registro.empresa.email
              
              else:
                ## No tenemos listado de meil para el
                threading.Thread.__init__(self)
                return
            """
            # self.msgBody += f'\nNombre Usuario: \n\t{registro.username}'
            # self.msgBody += f'\nUsuario: \n\t{registro.get_full_name()}'
            
            # self.email = EmailMessage(self.header,self.msgBody\
            #       ,EMAIL_HOST_USER,self.meilList\
            #       ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
            # threading.Thread.__init__(self)
            # return

          elif(grupo in ('programador','admin','superuser')):          
            self.msgBody = f'{msg}'
            self.meilList = GetEmailList(grupo='admin')
            """ 
              if(registro.email != None):
                self.meilList = [registro.email]
                # url = f'url: {HOSTING_URL}/login/view_users/{registro.id}/'
                self.msgBody = f'{msg} {url}'
              else:
                self.msgBody = f'{msg}'
                self.meilList = GetEmailList(grupo='admin')
            """
          else:
            ## El usuario no pertenece a un grupo valido
            debug_print(f'Usuario {registro} Grupo {grupo} email: {self.meilList}, no pertenece a un grupo valido')
            threading.Thread.__init__(self)
            return

        if(self.meilList == None):
          threading.Thread.__init__(self)
          return
        self.msgBody += f'\nNombre Usuario: \t{registro.username}'
        ## password = {'old_password': "old_password" ,'new_password':"new_password2"}
        if(password != None and 'old_password' in password and 'new_password' in password):
          self.msgBody += f'\nContraseña: \t Antigua: {password["old_password"]} , Nueva: {password["new_password"]}'

        elif(password != None and 'new_password' in password):
          self.msgBody = f'{msg} url: {HOSTING_URL}/login/'
          
          self.msgBody += f'\nContraseña Nueva: {password["new_password"]}'

        self.msgBody += f'\nNombre Completo: \t{registro.get_full_name()}'
        self.msgBody += f'\nDireccion Correo: \t{registro.email}'
        
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return

      '''
      if(attend == False and isinstance(registro,Desarrollo) == True):
        self.meilList = GetEmailList(grupo='admin')
        url = f'url: {HOSTING_URL}/login/view_desarrollos_works/{registro.id}/'

        if(self.meilList == None):
          self.meilList = []
        
        if(registro.email != None and len(registro.email) > 0):
          if(isinstance(registro.email,str)):
            self.meilList.extend(registro.email.split())
          else:
            self.meilList.extend(registro.email)          
        

        self.msgBody = f'{msg} {url}'        
        self.msgBody += f'\nMensaje: \n\t{registro.descripcion}'
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return
      ##endif
      if(attend == True and isinstance(registro,Desarrollo) == True):
        # debug_print(f'registro.email : {registro.email}')
        # debug_print(f'self.meilList : {self.meilList}')
        url = None        
        if(registro.asistente != None):
          self.meilList = [registro.asistente.programador.email]
          url = f'url: {HOSTING_URL}/attend_ticket/view_desarrollos_works/{registro.id}/'

        self.msgBody = f'{msg} {url}'        
        self.msgBody += f'\nMensaje: \n\t{registro.descripcion}'
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return
      ##endif
      if(attend == False and isinstance(registro,RegistroTrabajo) == True):
        self.meilList = GetEmailList(grupo='admin')
        url = f'url: {HOSTING_URL}/login/view_desarrollos_works/{registro.id}/'

        if(self.meilList == None):
          self.meilList = []
        
        if(registro.desarrollo.email != None and len(registro.desarrollo.email) > 0):
          if(isinstance(registro.desarrollo.email,str)):
            self.meilList.extend(registro.desarrollo.email.split())
          else:
            self.meilList.extend(registro.desarrollo.email)
        

        self.msgBody = f'{msg} {url}'        
        self.msgBody += f'\nMensaje: \n\t{registro.msg}'
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return
      ##endif
      if(attend == True and isinstance(registro,RegistroTrabajo) == True):
        # debug_print(f'registro.email : {registro.email}')
        # debug_print(f'self.meilList : {self.meilList}')
        url = None        
        if(registro.desarrollo.asistente != None):
          self.meilList = [registro.desarrollo.asistente.programador.email]
          url = f'url: {HOSTING_URL}/attend_ticket/view_desarrollos_works/{registro.id}/'

        if(self.meilList == None):
          self.meilList = []
        
        if(registro.desarrollo.email != None and len(registro.desarrollo.email) > 0):
          if(isinstance(registro.desarrollo.email,str)):
            self.meilList.extend(registro.desarrollo.email.split())
          else:
            self.meilList.extend(registro.desarrollo.email)

        self.msgBody = f'{msg} {url}'        
        self.msgBody += f'\nMensaje: \n\t{registro.msg}'
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro.id}'}) 
        threading.Thread.__init__(self)
        return
      ##endif
      '''


      if(isinstance(registro,str) == True):
        ## Consultamos a que tipo de user corresponde, superuser | Administrador | Programador | Cliente
        if( not 'admin' in registro ):
          debug_print(f'registro {registro} no contemplado')
          threading.Thread.__init__(self)
          return
        
        self.msgBody = f'{msg}'
        # self.meilList = GetEmailList(grupo='admin')
        self.meilList = GetEmailList(grupo='admin')
        debug_print(F'self.meilList: {self.meilList}')

        ## si no tenemso email cargados aun, o cuerpo para el meil salimos
        if(self.meilList == None or self.msgBody == None):
          threading.Thread.__init__(self)
          return
        
        self.email = EmailMessage(self.header,self.msgBody\
              ,EMAIL_HOST_USER,self.meilList\
              ,reply_to=[EMAIL_REPLY_TO],headers={'Message-ID': f'REG-{registro}'}) 
        threading.Thread.__init__(self)
        return
      ##endif
    ##endif 
        
    body = args.get('email',None)
    if(body != None and len(body['tolist']) > 0):
      '''
        emailinfo = { 'tolist':listMailClient, 'from':EMAIL_HOST_USER \
        ,'reply':[EMAIL_REPLY_TO] , 'headerbody': f'Ticket "{lticket.id}" actualizado' \
        ,'body': f'update ticket {lticket.id} url: {HOSTING_URL}/register_ticket/expand_ticket/{lticket.id}/'        
        ,'header' : {'Message-ID': f'REG-{t1.id}'} }
      '''
      """
      self.email = EmailMessage(body['headerbody'],body['body']\
            ,body['from'],body['tolist']\
            ,reply_to=body['reply'],headers=body['header']) 
      """
      self.email = EmailMessage(body['headerbody'],body['body']\
            ,EMAIL_HOST_USER,body['tolist']\
            ,reply_to=[EMAIL_REPLY_TO],headers=body['header']) 

      debug_print(f'Lista de email {body["tolist"]}')
    else:
      self.email = None
    threading.Thread.__init__(self)

  def __str__(self):
    #return f'Email List: "{self.meilList}" | Header: "{self.header}" '
    return f'Email List {self.meilList} | Header {self.header} | msg: {self.msgBody}\n'

  def run(self):
    # self.email.send()      
    if(self.email == None ):
      ## no pudo armar el objeto email      
      debug_print(f'Falta el Objeto email, Faltan parametros en la inicializacion.')
      if(self.object != None):
        self.object.email_status = False
        self.object.err_email = 'Falta el Objeto email, Faltan parametros en la inicializacion.'
        self.object.save()
      return

    ## verificamos si tenemos meils vacios en la lista:
    if(self.meilList != None ):
      i = len(self.meilList)
      j = 0
      while j < i:        
        if(self.meilList[j] == ''):
           self.meilList.pop(j)
           i -= 1
        j += 1
      ## debe estar el valor para poder removerlo 
      # self.meilList.remove('')
    #endif

    if(self.meilList == None or len(self.meilList) == 0):
      debug_print(f'No tenemos Correos para enviar el Mensaje. "{self}"')
      if(self.object != None):
        self.object.email_status = False
        self.object.err_email = f'No tenemos Correos para enviar el Mensaje. "{self}"'
        self.object.save()
      return
    
 

    while(self.retry > 0 and self.meilList != None and self.email != None ):
      try:
        self.email.send()
        debug_print(f'Envio de Email Sastifactorio {self}')
        if(self.object != None):
          self.object.email_status = True
          self.object.err_email = ''
          self.object.save()
        return
      except Exception as e:
        debug_print(f'Fallo el envio de Email {self}, error: {sys.exc_info()[0]}, wait = 100 ms')      
        if(self.object != None):          
          self.object.err_email = f'Fallo envio de Email {self}, {e}'

        self.retry -= 1
        time.sleep(0.100)
    ##endwhile
    if(self.object != None):
      self.object.email_status = False
      self.object.save()

    

