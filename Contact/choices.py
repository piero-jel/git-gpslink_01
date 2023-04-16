TICKET_BRIEF_CHOICE = [('emslog','emsLog')
                        ,('rlcrux','rlcrux')
                        ,('ems','ems')
                        ,('hsm','hsm') ]


                                                
TICKET_BRIEF_LEN_MAX = 10
TICKET_HISTROY_BRIEF_CHOICE = [ ('emslog','emsLog')
                              , ('rlcrux','rlcrux')
                              , ('autorizador','auth')
                              , ('ems','ems')
                              , ('hsm','hsm') ]

TICKET_HISTROY_BRIEF_CHOICE_ALL = [ (None,'----------')
                              , ('emslog','emslog')
                              , ('rlcrux','rlcrux')
                              , ('autorizador','auth')
                              , ('Ems','ems')
                              , ('Hsm','hsm') ]

TICKET_STATUS_CHOICES = ((True, 'Yes'), (False, 'No'))
                 
"""
    @var BRIEF_MAX_LEN
    @brief variable global para establecer la longitud maxima para la 
    descripcion breve del asunto del ticket
"""
BRIEF_MAX_LEN = 50


"""
    @var DETAIL_MAX_LEN
    @brief variable global para establecer la longitud maxima para la 
    descripcion detallada del asunto del ticket
"""
DETAIL_MAX_LEN = 500


def TicketHistory_Choice2Brief(choice:str)-> str:
  """
    @fn TicketHistory_Choice2Brief(choice:str):
    @brief Funcion para realizar el traslate desde opcion corta 
    a larga.
    @param choice  : Etiqueta del choice que se quiere traducir    
    @return resultado del traslate, o None en su defecto
  """
  # choice, elemento 0 -> Brief 1
  rval = 0
  for it in TICKET_HISTROY_BRIEF_CHOICE_ALL:
    print(f'cmp:: {it[0]} == {choice}')
    if(it[0] == choice):      
      print(f'brief : {choice} rval : {it[1]}, rval : {rval}')
      return it[1]
    rval += 1
  return ''

def TicketHistory_Brief2Choice(brief:str):
  """
    @fn TicketHistory_Brief2Choice(brief:str):
    @brief Funcion para realizar el traslate desde opcion larga a 
    corta.
    @param brief  : Etiqueta del choice que se quiere traducir    
    @return resultado del traslate, o None en su defecto
  """
  # choice, elemento 0 -> Brief 1
  for it in TICKET_HISTROY_BRIEF_CHOICE_ALL:
    print(f'cmp:: {it[1]} == {brief}')
    if(it[1] == brief):
      print(f'brief : {brief} rval : {it[0]}')
      return it[0]
  return None

def TicketHistory_traslate(opt:str,type:bool):
  """
    @fn TicketHistory_traslate(opt:str,type:bool):
    @brief Funcion para realizar el traslate de un choice
    @param opt  : Etiqueta del choice que se quiere traducir
    @param type : Tipo de traduccion
      - False : Choice2Brief, opcion corta a larga
      - True  : Brief2Choice, Opcion larga a corta
    @return resultado del traslate, o None en su defecto
  """
  target = 0
  rval = 1
  if(type):  
    target = 1
    rval = 0
  # choice, elemento 0 -> Brief 1
  for it in TICKET_HISTROY_BRIEF_CHOICE:
    if(it[target] == opt):
      return it[rval]
  return None  