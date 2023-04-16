from django.db import models
from django.db.models.base import Model

## insertar current data
from django.utils import timezone
# Create your models here.

from Login.models import User

from django.db.models.query import QuerySet

## add custom field to user
from config.settings import COMPANY_NAME_MAXLEN,TELEPHONE_NUMBER_MAXLEN,\
                            PRODUCT_NAME_MAXLEN,PRODUCT_BRIEF_MAXLEN,\
                            COMMENT_MAX_LEN,ERR_MAIL_MAX_LEN


 
class Contact(models.Model):
  """ Descripcion del modelo    
    * name      : Name
    * emails    : Correo o lista de correos electronicos para contactar
    * telephone : Numero de telefono de contacto
    * comment   : Comentario
    
    * attend    : Quien atendera el contacto
    * date_open : Fecha de creacion
    * date_update : fecha de actualizacion
    * date_close : fecha de cierre
    * status    : Estado del contacto, si se pudo contactar y se cerro el vinculo.
    * email_status : estado del envio de email interno, a los asistentes
    * err_email : Mensaje de error, si ocurrio, al enviar internamente el email
    
  """    
  name = models.CharField(max_length=COMPANY_NAME_MAXLEN,blank=False,null=True)
  comment=models.CharField(max_length=COMMENT_MAX_LEN,blank=False)
  email = models.EmailField(blank=False,null=True)
  telephone = models.CharField(max_length=TELEPHONE_NUMBER_MAXLEN,blank=False,null=True)   
  ##
  ## uso interno
  attend = models.ForeignKey(User,on_delete=models.DO_NOTHING,blank=True,null=True) 
  date_open = models.DateField(default=timezone.now)  
  date_update = models.DateField(default=timezone.now,null=True,blank=True)    
  date_close = models.DateField(null=True,blank=True)  
  status = models.BooleanField(default=True)
  email_status = models.BooleanField(default=True)  
  err_email = models.CharField(max_length=ERR_MAIL_MAX_LEN,blank=False)
  

  class Meta:
    ## para acceder a los miembros : 
    ordering = ['id']
    verbose_name = 'contact'
    verbose_name_plural='contact'
    """
      Definimos los permisos 
      sobre esta tabla
    """
    permissions = [
      ##(codename, name) 
        ('admin', 'Puede Administrar los Contact (ver historial, dar de baja)'),
        ('attend', 'Puede Atender un Contact'),
        ('register', 'Puede Registrar un nuevo Contact'),
    ] 
  
  def __str__(self):
    return f'{self.id} | {self.name} | {self.comment} |{self.email} | {self.telephone} | {self.date_open}'

  
