from config.apps import debug_print
from django.db import models

# Create your models here.
from django.db import models
from .managers import CustomUserManager
# Create your models here.
## insertar current data
from django.utils import timezone
"""
  extended user field 
"""
from django.contrib.auth.models import AbstractUser
## para usar los objetos dentro del settings.py del proyecto
from django.conf import settings
from config.settings import COMPANY_NAME_MAXLEN,TELEPHONE_NUMBER_MAXLEN
                            


class User(AbstractUser):
  """ Descripcion del modelo
    * id          : Identifcacion primary key
    * username    : Nombre de usuario 
    * first_name  : Primer Nombre
    * last_name   : Segundo Nombre, Apellido
    * email       : Dirreccion de Correo
    * empresa     : Empresa 'Empresa'
    * telefono    : Numero de Telefono
  """
  ## establecemos el default para la tabla ya creada  
  empresa = models.CharField(max_length=COMPANY_NAME_MAXLEN,blank=True,null=True)
  telefono = models.CharField(max_length=TELEPHONE_NUMBER_MAXLEN,blank=True,null=True)
  fecha_inicio =  models.DateField(default=timezone.now)
  
  objects = CustomUserManager()

  def __str__(self):
    return self.username

  def get(self,name):
    """ 
      metodo get, para implementar el modelo dentro de un 'forms.Form' para la inicializacion
      mediante:
        contexto['user_form'] = FormEditUser(data=luser)
    """
    target_User = {'id':self.id,'username':self.username ,'first_name':self.first_name \
          ,'last_name':self.last_name,'email':self.email,'empresa':self.empresa\
          ,'telefono':self.telefono }

    # debug_print(f'a:{self}')
    # debug_print(f'name {name}')
    if(name not in target_User.keys()):
      return None
    return target_User[name]

  class Meta:
    ## para acceder a los miembros : 
    ordering = ['id']
    verbose_name = 'user'
    verbose_name_plural='users'
  

