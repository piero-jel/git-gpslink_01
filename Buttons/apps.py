from django.apps import AppConfig


class ButtonsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Buttons'


"""
  # folder img: Buttons/static/Buttons/img
  # python3 manage.py collectstatic

  # view.py
  def Vista_btn(request):
    list_btn = [ BtnWithImage(path='botonchico_carga.png',url='/attend_ticket/',label='Carga')
              , BtnWithImage(path='botonchico_reporte.png',url='#',label='Reportes')
              , BtnWithImage(path='botonchico_adm.png',url='#',label='Administración') ]
    return render(request,"AppName/template.html",\
        {'listbtn':list_btn } )


  # template.html
  {% block content %}
    <div id="navbarSupportedContent_small" class="sticky-top shadow">
      <div class="container-fluid">
        <div class="container">
          <div class="row justify-content-center">

            {% for it in listbtn %}          
            <div class="col-2 text-center col-sm-1 col-md-3 col-lg-2">
              <div>
                <a href="{{it.url}}" class="d-none d-sm-none d-md-block">
                  <img src="{% static 'Buttons/img/'%}{{it.path}}" />
                </a>
                <a href="{{it.url}}" class="d-none d-sm-none d-md-block">              
                  {{it.label}}
                </a>
              </div>
            </div>
            {% endfor %}  

          </div>
        </div>
      </div>
  {% endblock %}  
"""
class BtnWithImage:
  def __init__(self,**args):
    self.path = args.get('path',None)
    self.url = args.get('url',None)
    self.label = args.get('label',None)
    self.msg = args.get('msg',self.label)

    # self.path = args['path']
    # self.url = args['url']
    # self.label = args['label']
    # self.msg = args['msg']

  def __iter__(self):
    return self
    
  def __str__(self):    
    return f'path: {self.path} | url: {self.url} | label: {self.label} | msg: {self.msg} '

"""
  <button class= 'btn btn-login space-top' type="submit" name= "nok" value="nok" >    
    <div class="col-2 text-center col-sm-1 col-md-3 col-lg-2">
      <img src="{% static 'Buttons/img/'%}{{it.path}}" />
    </div>
    {% if it.label %} 

    <div class="text-center">        
      {{it.label}}
    </div>                    
    {% endif %}
  </button>     

"""
class BtnFormWithImage:
  def __init__(self,**args):
    ## perfil css, opcional
    if( 'css' in args.keys()):
      self.css = args['css']

    ## si no lo pasamos colocamos su valor por defecto
    if( 'type' in args.keys()):
      self.type = args['type']
    else:
      self.type = 'submit'
    
    ## path de la imagen, no es mandatorio
    if( 'path' in args.keys()):
      self.path = args['path']

    ## campos mandatorios, deben venir si o si
    # en caso de que no vengan debemso lanzar una excepcion
    self.name = args['name']
    if( 'label' in args.keys()):
      self.label = args['label']
    ## name, este es opcional en caso de no venir lo igualamos a 'value'
    if( 'value' in args.keys()):
      self.value = args['value']
    else:
      self.value = self.name

    
class BtnForm:
  def __init__(self,**args):
    ## perfil css, opcional
    if( 'css' in args.keys()):
      self.css = args['css']

    ## si no lo pasamos colocamos su valor por defecto
    if( 'type' in args.keys()):
      self.type = args['type']
    else:
      self.type = 'submit'
    
    ## campos mandatorios, deben venir si o si
    # en caso de que no vengan debemos lanzar una excepcion
    self.name = args['name']
    if( 'label' in args.keys()):
      self.label = args['label']
    ## value, este es opcional en caso de no venir lo igualamos a 'value'
    if( 'value' in args.keys()):
      self.value = args['value']
    else:
      self.value = self.name