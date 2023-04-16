from Contact.models import Contact
from Login.models import User
from config.apps import debug_print
 

def get_nticket_register(user:User,type:str):
  """
   @param user
   @param type :
    * nticket_total
    * nticket_activos
    * nticket_pendientes
    * nticket_cerrados
  """
  if(type == 'nticket_total'):
    try:
      insticket = Contact.objects.filter(register=user)
    except:
      debug_print(f'Fallo la query: Contact.objects.filter(register={user})')
      return False
  elif(type == 'nticket_activos'):
    try:
      insticket = Contact.objects.filter(register=user,estado=True)
    except:
      debug_print(f'Fallo la query: Contact.objects.filter(register={user},estado=True)')
      return False
  elif(type == 'nticket_pendientes'):
    try:
      insticket = Contact.objects.filter(register=user,register_estado=False,estado=True)
    except:
      debug_print(f'Fallo la query: Contact.objects.filter(register={user},register_estado=False)')
      return False

  elif(type == 'nticket_cerrados'):
    try:
      insticket = Contact.objects.filter(register=user,register_estado=False,estado=False)
    except:
      debug_print(f'Fallo la query: Contact.objects.filter(register={user},register_estado=False)')
      return False

  return insticket


def empresa_query(**args):   
  """
    @param query:
      * 'nempleados'
      * 'nticket_total'
      * 'nticket_activos'
      * 'nticket_cerrados'
      
    @param args :
     * id: id de empresa
     * empresa: instancia de empresa    
     * users : listado de usuarios de la empresa
  """
  query_target = ('nempleados','nticket_total','nticket_activos','nticket_pendientes','nticket_cerrados')

  query = args.get('query',None)
  if(query == None or not query in query_target):
    return None

  insempresa = args.get('empresa',None)
  id_empresa = args.get('id',None)
  nuser = args.get('users',None)
  if(nuser == None and insempresa == None and id_empresa == None):
    debug_print(f'Argumentos Invalidos {args}')
    return False  

  if(nuser == None):
    if(insempresa == None and id_empresa != None):
      try:
        insempresa = Empresa.objects.get(id=id_empresa)
      except:
        debug_print(f'No localizamos una Empresa con el id: {id_empresa}')
        return False   

    try:
      nuser = User.objects.filter(empresa=insempresa)
    except:
      return 0

  

  if(query == 'nempleados'):
    return len(nuser)
  
  if(query in query_target[1:] ):
    nticket = 0
    for it in nuser:
      # try:
      #   insticket = Contact.objects.filter(register=it)
      # except:
      #   debug_print(f'Fallo la query: Contact.objects.filter(register={it})')
      #   return False
      nticket += len(get_nticket_register(it,query))

    return nticket

  return None  

    