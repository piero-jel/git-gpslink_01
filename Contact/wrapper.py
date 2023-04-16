from config.apps import debug_print
from .models import Contact, RegisterWork

## para querys elaboradas ej: Tickets.objects.filter(~Q(attend=currentProgrmmind))
#   SELECT * from Tickets where attend <> currentProgrmmind
from django.db.models import Q

from django.db.models.query import QuerySet

from django.core.exceptions import FieldError

import sys


def executeQuerys(**args):
  """
    @fn def executeQuerys(**args):
    @brief 
    @param args:
      * filter
      * order_by
  """
  Filter = args.get('filter',None)
  OrderBy = args.get('order_by',None)

  ## si no tenemos target realizamos la query por defecto
  # if(OrderBy == None and Filter == None):
  #   try:
  #     return Tickets.objects.all()
  #   except:
  #     debug_print(f'error {sys.exc_info()[1]} Tickets.objects.all()')
  #     return None

  # 1) (Filter)? Filtramos
  # 2) (OrderBy)? Ordenamos
  rval = None
  ## Deberiamos verificar, en caso de que sean pasados, si los mismos son instancia de dict
  if(Filter != None and not isinstance(Filter,dict)):
    debug_print(f'Arg filter is not dict instance "[{Filter}] type => {type(Filter)}"')
    return None

  if(OrderBy != None and not isinstance(OrderBy,str)):
    debug_print(f'Arg order_by is not dict instance "[{OrderBy}] type => {type(OrderBy)}"')
    return None

  if(Filter != None):
    filtro={}
    nfiltro={}

    if(len(Filter.keys()) > 1):

      for key,it in Filter.items():
        if('!' in key):
          nfiltro.update({key[1:]:it})
        else:
          filtro.update({key:it})
      
    elif(len(Filter.keys()) == 1):
      if('!' in list(Filter.keys())[0]):
        nfiltro = {list(Filter.keys())[0][1:] : Filter[list(Filter.keys())[0]]}
      else:
        filtro = Filter
    
    # debug_print(f' Filter: {Filter}  filtro: {filtro}  nfiltro: {nfiltro}')

    try:
      # debug_print(Tickets.objects.filter(**{}))
      # debug_print(f' Filter: {bool(Filter)}  filtro: {bool(filtro)}  nfiltro: {bool(nfiltro)}')

      if(bool(nfiltro) == False and bool(filtro) == True):
        rval = Tickets.objects.filter(**filtro)

      elif(bool(nfiltro) == True and bool(filtro) == False):
        # rval = Tickets.objects.filter(~Q(**nfiltro))
        for key,it in nfiltro.items():
          if(rval == None):
            rval = Tickets.objects.filter(~Q(**{key:it}))
          else:
            rval = rval & Tickets.objects.filter(~Q(**{key:it}))

        # keys = list(nfiltro.keys())
        # rval = Tickets.objects.filter(~Q(**{keys[0]:nfiltro[keys[0]]}),~Q(**{keys[1]:nfiltro[keys[1]]}))

      else:          
        # rval = Tickets.objects.filter(~Q(**nfiltro),**filtro)
        rval = Tickets.objects.filter(**filtro)
        for key,it in nfiltro.items():
          rval = rval & Tickets.objects.filter(~Q(**{key:it}))
        

      # debug_print(rval)
    # except FieldError:
    except:
      '''fallo el order by, posiblemente por campo '''
      debug_print(f'error {sys.exc_info()[1]} Tickets.objects.filter({Filter})')
      return None
  else:
      # Filter = None
    try:
      rval = Tickets.objects.all()
    except:
      debug_print(f'error {sys.exc_info()[1]} Tickets.objects.all()')
      rval = None
  ## endif
  if(rval != None and OrderBy):
    rval = rval.order_by(OrderBy)
  
  return rval



class wrapper_tickets():
  def __init__(self):
    pass
    # self.model1

  def object2map(**args):
    Object = args.get('item_query',None)
    # if('item_query' in args.keys()):
    #   Object = args['item_query']
    # else:
    #   Object = None

    rmap = Tickets.object2map(item_query = Object)
    if(rmap['id'] == None):
      rmap['fecha_update'] = None
      rmap['ticket_history'] = None
      return rmap

    '''
    if(Object == None):
      ## si no tenemso id, no se lleno la BBDD
      # print(f'Object: {Object}')
      return { 'id':None, 'empresa':None ,'register':None, 'attend':None ,'brief':None \
             , 'detail':None,'email':None,'fecha_creacion':None\
             , 'fecha_cierre':None,'file1':None,'file2':None,'estado':None,'fecha_update':None}

    ## Obtenemos los campos fuera de la Tabla Tickets, TicketsHistory    
    '''
    fecha_update = None
    rQuery = None
    
    try:      
      registerQuery = RegisterWork.objects.filter(ticket=Object.id).order_by('-id')[0]      
    except IndexError:      
      registerQuery = None      

    if(registerQuery != None):
      fecha_update = registerQuery.date_creacion.date()
    # except TicketsHistory.DoesNotExist:
    #   pass    

    ## debemos obtener el map desde el Modelo ORM, para encapsular 
    ## rmap = Tickets.object2map(item_query)

    ## debemos mapear la query resultante de Histry para anexarla como mapa
    ## y de esta forma obtener los datos para armar el link a un vista
    rmap[ 'fecha_update'] = fecha_update
    # rmap['ticket_history'] = rQuery    
    rmap['register_work'] = RegisterWork.object2map(item_query = registerQuery)
    
    # rmap['ticket_history'] = TicketsHistory.object2map(item_query = rQuery)
    return rmap
    
    '''
      return { 'id':Object.id, 'empresa':Object.register.empresa
              ,'register':Object.register, 'attend':Object.attend ,'brief':Object.brief \
              ,'detail':Object.detail,'email':Object.email,'fecha_creacion':Object.fecha_creacion\
              ,'fecha_cierre':Object.fecha_cierre,'file1':Object.file1,'file2':Object.file2\
              ,'estado':Object.estado,'fecha_update':fecha_update , 'ticket_history':rQuery}
    '''
  '''
    Retorna la query que genere el cuerpo de la tabla, cada una de las resultante
    puede ser utilizada por object2map() para completar la tabla. En caso de 
    chain dentre tablas
  '''
  def query(**args):
    ## almacenamos los target de la query 
    OrderBy = args.get('order_by',None)

    # if('order_by' in args.keys()):
    #   OrderBy = args['order_by']
    # else:
    #   OrderBy = None
    
    Filter = args.get('filter',None)
    # debug_print(f'OrderBy: {OrderBy}  Filter: {Filter}')
    return executeQuerys(filter=Filter,order_by=OrderBy)

    # if('filter' in args.keys()):
    #   Filter = args['filter']
    # else:
    #   Filter = None

    ## Salida por Default targets:
    # -- nos sirve contemplar None como filtro para los casos no atendidos aun
    # if(Filter != None and Filter['target'] == None):
    #   return None

    if(OrderBy != None and OrderBy == ''):
      return None

    ## si no tenemos target realizamos la query por defecto
    if(not OrderBy and not Filter):
      return Tickets.objects.all()

    return executeQuerys(filter=Filter,order_by=OrderBy)
    ## FIXME : Pasos para update
    # 1) (Filter)? Filtramos
    # 2) (OrderBy)? Ordenamos
    
    rval = executeQuerys(filter=Filter,order_by=OrderBy)
    if(Filter):
      filtro=None
      nfiltro=None
      if(len(Filter.keys()) > 1):
        filtro={}
        nfiltro={}
        for key,it in Filter.itmes():
          pass
        
      elif(len(Filter.keys()) == 1):
        if('!' in list(Filter.keys())[0]):
          nfiltro = {list(Filter.keys())[0][1:] : Filter[list(Filter.keys())[0]]}
          debug_print(f'filtro: {nfiltro}  Filter: {Filter}')

        else:
          filtro = Filter
        

      try:
        if(nfiltro == None and filtro != None):
          rval = Tickets.objects.filter(**filtro)

        elif(nfiltro != None and filtro == None):
          rval = Tickets.objects.filter(~Q(**nfiltro))

        else:          
          rval = Tickets.objects.filter(~Q(**nfiltro),**filtro)

      # except FieldError:
      except:
        '''fallo el order by, posiblemente por campo '''
        debug_print(f'error {sys.exc_info()[1]} Tickets.objects.filter({Filter})')
        return None

    if(rval != None and OrderBy):
      rval = rval.order_by(OrderBy)
    
    return rval
      
      
    ## Solo tenemos Order By
    if(OrderBy and not Filter):
      try:
        return Tickets.objects.order_by(OrderBy)
      except FieldError:
        '''fallo el order by, posiblemente por campo '''
        debug_print(f'except FieldError: OrderBy: {OrderBy}')
        return None

      except:
        '''fallo la query'''
        debug_print(f'except: return Tickets.objects.order_by({OrderBy})')
        return None


    ## Solo tenemos Filter pero no Order By
    '''
      filter example
      queryFilter = {'field': 'register', 'target':request.user }  
    '''
    if(Filter and not OrderBy ):
      if('type' not in Filter.keys()):
        # filterTag = {Filter["field"]:f'{Filter["target"]}'}
        try:
          # Tickets.objects.filter(f'{Filter["field"]}={Filter["target"]}')
          # Tickets.objects.filter(filterTag)

          if(Filter['field'] == 'register' and not 'field2' in Filter.keys()):
            return Tickets.objects.filter(register=Filter['target'])
          
          if(Filter['field'] == 'register' and 'field2' in Filter.keys()):

            if(Filter['field2'] == 'estado' and Filter['target2'] == True):
              # debug_print(f'query: Tickets.objects.filter(register={Filter["target"]},estado=True)')
              ## Ticket Ticket Abiertos
              return Tickets.objects.filter(register=Filter['target'],estado=True)

            if(Filter['field2'] == 'estado' and Filter['target2'] == False):
              # debug_print(f'query: Tickets.objects.filter(register={Filter["target"]},estado=False)')
              # Ticket Cerrados
              return Tickets.objects.filter(register=Filter['target'],estado=False)

            if(Filter['field2'] == 'register_estado' and Filter['target2'] == False):
              # Ticket Pendientes
              # debug_print(f'query: Tickets.objects.filter(register={Filter["target"]},estado=False)')
              return Tickets.objects.filter(register=Filter['target'],estado=True,register_estado=False)


          if(Filter['field'] == 'attend'):
            return Tickets.objects.filter(attend=Filter['target'])

        ## el field del filter no existe
        except ValueError:
          filterTag = {Filter["field"]:f'{Filter["target"]}'}
          debug_print(f'except ValueError: Filter Register: {Filter["field"]}, Filter Target: {Filter["target"]}')
          debug_print(f'except ValueError: filterTag: {filterTag}')
          return None
        except :
          filterTag = {Filter["field"]:f'{Filter["target"]}'}
          debug_print(f'except: Tickets.objects.filter({Filter["field"]}={Filter["target"]})')
          debug_print(f'except: filterTag: {filterTag}, {type(filterTag)}')
          return None
        # except:          
        #   pass

      if('type' in Filter.keys() and Filter['type'] == '!='):
        try:
          if(Filter['field'] == 'register'):
            return Tickets.objects.filter(~Q(register=Filter['target']))

          if(Filter['field'] == 'attend'):
            return Tickets.objects.filter(~Q(attend=Filter['target']))

        ## el field del filter no existe
        except ValueError:
          return None

      ## en caso de usar para otros campos debemos definir los demas

      ## FIXME : dejamos por defecto el all
      return Tickets.objects.all()
      
    retry = 0
    ## Tenemos Ambos Filtro y Order
    while( retry < 2 and 'type' not in Filter.keys()):      
      try:      
        if(Filter['field'] == 'register'):
          return Tickets.objects.filter(register=Filter['target']).order_by(OrderBy)

        if(Filter['field'] == 'attend'):
          return Tickets.objects.filter(attend=Filter['target']).order_by(OrderBy)
    
      except ValueError:                
        # print(f'Error field: {Filter["field"]} filter: {Filter["target"]} OrderBy {OrderBy}')
        return None
    
      except:
        print(f'Error field: {Filter["field"]} filter: {Filter["target"]} OrderBy {OrderBy}')
        if(OrderBy == 'empresa'):
          OrderBy = 'register'
        elif( OrderBy == '-empresa'):
          OrderBy = '-register'
        retry += 1
        continue

    if(retry == 2):
      return None
        

    if( Filter['type'] == '!='):
      try:      
        if(Filter['field'] == 'register'):
          return Tickets.objects.filter(~Q(register=Filter['target'])).order_by(OrderBy)

        if(Filter['field'] == 'attend'):
          return Tickets.objects.filter(~Q(attend=Filter['target'])).order_by(OrderBy)
    
      except ValueError:
        return None
    
      except:
        print(f'Error field: {Filter["field"]} filter: {Filter["target"]} OrderBy {OrderBy}')
        return None

    ## Por defecto   
    return Tickets.objects.all()
    
  def begin(**args):    
    Filter = args.get('filter',None)
    return executeQuerys(filter=Filter)

