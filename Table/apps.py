from django.apps import AppConfig
## importamos las utilidades 
from config.apps import debug_print
# import json
# import jsonpickle


class TableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Table'




class ButtonsUpDown():
  def __init__(self,**args):
    self.field = args['field']
    self.label = args['label']
    self.button = args['button']    
    self.st = args['status']
    self.img_up = args['img_up']
    self.img_down = args['img_down']

    if('tag' in args.keys()):
      self.tag = args['tag']
    else:
      self.tag = None

  def __str__(self):
    return f'field: {self.field} | label: {self.label} | button: {self.button} | status: {self.st} | status: {self.tag} | tag: {self.tag}'

  def up(self):
    self.status = True

  def down(self):
    self.status = False

  def enable(self):
    return self.button

  def status(self):
    return self.st

class TablaWithUpDownButtons():    
  '''
    @class TablaWithUpDownButtons()
    @brief Objeto para construir una Tabla con Botones Up/Down en el head   
     - table_head
     - table_body
     - update_body(request)
  '''
  def __init__(self,**args):
    '''
      Contructor para los objetos del tipo TablaWithUpDownButtons    
        - table_head
        - table_body
        - update_body(request)
        
      @param map      : Mapa de la tabla, en formato 'key:value', ex row 'id' : {'label' : 'Id', 'button':True , 'status':False } 
        - 'id'    : Nombre que se corresponde con la clave de la columna, puede ser un campo de una tabla.
        - 'label':'Id'    : Par Clave valor para indicar la etiqueta de la columna en este caso 'Id'.
        - 'button':True   : Par Clave valor para Habilitar (True)/Deshabilitar (False) el boton en una columna.
        - 'status':False  : Par Clave valor para Habilitar/Deshabilitar el Up/Down de las flechas orden descendente por defecto si es False.

      @param wrapper  : Funcion intermediaria para realizar las query de actualizacion sobre la tabla en caso de que necesite realizar querys no comunes
      @param img_up   : path a la imagen up, es opcional.
      @param img_down : path a la imagen down, es opcional.
      @param link_msg : Mensaje para ell link
      @param 
    '''
    '''
      model   -> Modelo ORM
      
      map = { 'field' : {'label' : Label, 'button':True|False , 'status':False|True } 
              'field1' : {'label' : Label, 'button':True|False , 'status':False|True } 
              'field2' : {'label' : Label, 'button':True|False , 'status':False|True } 
            }
      img_up    path/image_name
      img_down  path/image_name  
    '''
    ## los unico args mandatorio
    # if('model' not in args.keys()):
    #   return None
    # self.model = args['model']

    ## Mapa para conformar y actualizar la tabla
    self.map = args.get('map',None)
    # if('map' not in args.keys()):
    #   return None
    # self.map = args['map']

    ## Objeto que contiene las interfaces para realizar las querys y
    #  mapeos de los campos
    self.wrapper = args.get('wrapper',None)
    # if('wrapper' not in args.keys()):
    #   return None
    # self.wrapper = args['wrapper']

    ## path/name a la imagen para la flecha up/down
    pimg_up = args.get('img_up','Buttons/img/go-up.svg')
    pimg_down = args.get('img_down','Buttons/img/go-down.svg')

    # pimg_down = 'Buttons/img/go-down.svg'
    # pimg_up = 'Buttons/img/go-up.svg'
    # if('img_up' in args.keys()):
    #   pimg_up = args['img_up']

    # if('img_down' in args.keys()):
    #   pimg_down = args['img_down']



    ## Longitud de filtro para los campos, en caso de campos largos que 
    ## dificultan el posicionado de columnas
    self.filter_leng = args.get('filter_leng',None)
    # if('filter_leng' in args.keys()):
    #   self.filter_leng = args['filter_leng']
    # else:
    #   self.filter_leng = None
    
    ## FIXME
    self.row_ref = args.get('row_ref',False)
    # if('row_ref' in args.keys()):
    #   self.row_ref = args['row_ref']
    # else:
    #   self.row_ref = False


    ## la url a la nueva vista, la cual le pasaremos como 
    ## arg la primer columna (ex id )
    self.url = args.get('url',None)
    # if('url' in args.keys()):
    #   self.url = args['url']
    # else:
    #   self.url = None
    
    self.link_msg = args.get('link_msg',None)
    # if('link_msg' in args.keys()):
    #   self.link_msg = args['link_msg']
    # else:
    #   self.link_msg = None

    ## para la query (filtrado del tipo where)
    self.filter = args.get('query_filter',None)
    # if('query_filter' in args.keys()):
    #   self.filter = args['query_filter']
    # else:
    #   self.filter = None

    ## para identificar la tabla, en caso de varias en un solo tempalte
    self.id = args.get('id',None)
    # if('id' in args.keys()):
    #   self.id = args['id']
    #   ## anexamos el id si existe para la referencia
    #   # for field in self.map.keys():
    #   #   self.map[field]['tag']=f'{self.id}{self.map[field]["label"]}'

    # else:
    #   self.id = None
    #   # for field in self.map.keys():
    #   #   self.map[field]['tag']=self.map[field]["label"]
        
   
        
    ## debemos comparar los campos FIXME debemos usar un loop??
    # if( map.keys() not in model().get_map().keys()):
    # objectMap = self.model.object2map(self.model()).keys()
    objectMap = self.wrapper.object2map(item_query = None).keys()
    for it in self.map.keys():
      # if( it not in self.model().get_map().keys()):
      if( it not in objectMap):             
        # print('No localizado')
        debug_print(f' {it} No localizado')
        debug_print(f'{self.map.keys()}')
        debug_print(f'{self.wrapper.object2map(item_query = None).keys()}')
        self.table_body = None
        return

    
    self.table_head = []
    for field in self.map.keys():  
      if(self.id == None):
        self.table_head.append(ButtonsUpDown(field=field ,label=self.map[field]['label'] \
          ,button =self.map[field]['button'] , status=self.map[field]['status'] \
          # ,tag=self.map[field]['label'],img_up=pimg_up,img_down=pimg_down  ))
          ,tag=field,img_up=pimg_up,img_down=pimg_down  ))
      else:
        self.table_head.append(ButtonsUpDown(field=field ,label=self.map[field]['label'] \
          ,button =self.map[field]['button'] , status=self.map[field]['status'] \
          ,tag=f'{self.id}{self.map[field]["label"]}' ,img_up=pimg_up,img_down=pimg_down  ))

      # self.table_head.append(ButtonsUpDown(field=field ,label=self.map[field]['label'] \
      #   ,button =self.map[field]['button'] , status=self.map[field]['status']))      
      # self.table_head.append(ButtonsUpDown(field=field ,label=self.map[field]['label'] \
      #     ,button =self.map[field]['button'] , status=self.map[field]['status'] \
      #     ,tag=self.map[field]['tag'] ))
  
    '''
      for it in self.table_head:    
        if( not it.enable() ):
          continue

        fieldQuery = ''
        if( it.status() ):
          fieldQuery = f'{it.field}'        
        else:
          fieldQuery = f'-{it.field}'
    ''' 
    
    
    # rQuery = self.wrapper.query(oreder_by = None,filter=self.filter)
    rQuery = self.wrapper.begin(filter=self.filter)
    # rQuery = None
    self.table_body = []
    ## en caso de que la query falle
    if(rQuery == None):      
      return 
          
    for it in rQuery:
      mapa = self.wrapper.object2map(item_query=it)
      fila = []
      for td in self.map.keys():
        # print(type(mapa[td]))
        if(isinstance(mapa[td], dict)):
          # print('Es un Diccionario')
          fila.append(mapa[td][td])
        else:
          fila.append(mapa[td])

      self.table_body.append(fila)
  
  # def object2json(self):
  #   return jsonpickle.encode(self, unpicklable=False)
  #   return json.dumps(self, default=lambda o: o.__dict__)

  def object2map(self):
    """
      * self.map 
      * self.wrapper
      * self.filter_leng
      * self.row_ref
      * self.url
      * self.link_msg
      * self.filter
      * self.id
      * self.table_head
      * self.table_body
    """
    return {'map':self.map 
        ,'wrapper':self.wrapper
        ,'filter_leng':self.filter_leng
        ,'row_ref':self.row_ref
        ,'url':self.url
        ,'link_msg':self.link_msg
        ,'filter':self.filter
        ,'id':self.id
        ,'table_head':self.table_head
        ,'table_body':self.table_body}
    
    pass
  def update_body(self,**args):
    """
      @fn def update_body(self,**args):
      @brief
      @param args
        * request
    """
    resquesGet = args.get('request',None)
    # debug_print(' execute: def update_body(self,**args):')

    fieldQuery = None

    if(resquesGet != None):      
      for it in self.table_head:    
        if( it.tag not in resquesGet.keys()):
          continue

        if( not it.enable() ):
          continue

        fieldQuery = ''
        if(resquesGet[it.tag] == '-1'):
          fieldQuery = f'-{it.field}'
          it.up()
          
        else:
          fieldQuery = f'{it.field}'
          it.down()
    ## endif

    # rQuery = self.model.objects.order_by(fieldQuery)
    ##    self.wrapper  => wrapper
    ##    self.filter   => query_filter
    if(resquesGet != None):
      rQuery = self.wrapper.query(order_by=fieldQuery,filter=self.filter)
    else:
      rQuery = self.wrapper.query(filter=self.filter)
    # debug_print(f'order_by: {fieldQuery}  self.filter: {self.filter}')
    if(rQuery == None):
      # debug_print(f'rQuery : {rQuery}')
      return self

    self.table_body = []      
    for it in rQuery:
      mapa = self.wrapper.object2map(item_query = it)
      fila = []
      for td in self.map.keys():
        if(isinstance(mapa[td], dict)):
          # print('Es un Diccionario')
          fila.append(mapa[td][td])
        else:
          fila.append(mapa[td])

      self.table_body.append(fila)

    # print(f'body table: {self.table_body}')
    # debug_print(f'self : {self}')
    return self