from logging import debug
from django import forms

from django.core.validators import validate_email
from Contact.models import Contact


from django.forms import ModelForm ,Textarea ,DateInput,SelectDateWidget
from django.forms.widgets import ChoiceWidget

from datetime import datetime

## para choices select
from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _
from config.apps import debug_print,validatinEmails

from django.contrib import messages
import os
from django.core.mail import EmailMessage

from Login.models import User
from django.contrib.auth.models import Group

from config.settings import HOSTING_URL, EMAIL_HOST_USER,EMAIL_REPLY_TO,EMAIL_SEND_RETRY
import sys
from Login.contexto import EmailThread,LABELS_GROUPS_PROGRAMADOR,LABELS_GROUPS_CLIENTE
from django.db.models import Q
# from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField

from datetime import datetime, time ,timedelta

from config.settings import FORM_TITLE_NAME ,FORM_TITLE_USERNAME,FORM_TITLE_FIRSTNAME,FORM_TITLE_LASTNAME,FORM_TITLE_EMAIL ,\
  FORM_TITLE_TELEPHONE,FORM_TITLE_COMMENT,FORM_LENGTH_COMMENT,FORM_TITLE_COMPANYNAME,FORM_TITLE_COMPANYTEL1,FORM_TITLE_COMPANYTEL2

from config.settings import FORM_PLACEHOLDER_NAME,FORM_PLACEHOLDER_USERNAME, FORM_PLACEHOLDER_FIRSTNAME,FORM_PLACEHOLDER_LASTNAME,\
  FORM_PLACEHOLDER_EMAIL,FORM_PLACEHOLDER_TELEPHONE,FORM_PLACEHOLDER_COMMENT,FORM_PLACEHOLDER_COMPANYNAME,\
  FORM_PLACEHOLDER_COMPANYTEL1,FORM_PLACEHOLDER_COMPANYTEL2


class FormContact(ModelForm):
  '''
    name : Nombre         
    comment : Comentario
    email : Correo o lista de correos electronicos para contactar
    telephone : Numero de telefono de contacto

    attend : Quien atendera el contacto
    date_open : Fecha de creacion
    date_update : fecha de actualizacion
    date_close : fecha de cierre
    status : Estado del contacto, si se pudo contactar y se cerro el vinculo.
    email_status : estado del envio de email interno, a los asistentes
    err_email : Mensaje de error, si ocurrio, al enviar internam
  '''
  class Meta:
    model = Contact
    fields = ['name','comment','email','telephone']

    labels = {'name': 'Nombre'
             ,'comment': 'Mensaje'
             ,'email': 'E-mail'
             ,'telephone': 'Teléfono'}

    widgets = {
             'name': forms.TextInput(attrs={'autofocus': False ,'placeholder':FORM_PLACEHOLDER_NAME,\
                       'title':FORM_TITLE_COMPANYNAME})
            
            ,'telephone': forms.TextInput(attrs={ 'autofocus': False ,'placeholder':FORM_PLACEHOLDER_TELEPHONE,\
                       'title':FORM_TITLE_TELEPHONE})                                   

            ,'comment': Textarea(attrs={'cols': 35, 'rows': 6\
              ,'title': f'Ingrese un mensaje de hasta {FORM_LENGTH_COMMENT} caracteres','placeholder': FORM_PLACEHOLDER_COMMENT\
                ,'title':FORM_TITLE_COMMENT })          

            ,'email': forms.TextInput(attrs={'title':FORM_TITLE_EMAIL,'placeholder': FORM_PLACEHOLDER_EMAIL})
        }

  def is_valid(self):
    """
      @fn 
      @brief
      @return 
        * True
        * False
    """
    valid = super(FormContact,self).is_valid()     
    if(valid == False):      
      return False


    debug_print(f'self.data: {self.data["email"]}')

    rval = validatinEmails(email=self.data['email'])
    if(rval == False):
      self.add_error('email', f"La direccion de Correo electronico '{self.data['email']}' no existe actualmente.")
      return False
      
    return True

    ## es opcional la carga del ""
    debug_print(f'self.data: {self.data}')


    if(mod == None):
      return False

    return True

  def save(self,**arg):
    """
      @parma arg:
        - instance
        - register
    """    
    '''
      name : Nombre      
      attend : Quien atendera el contacto
      comment : Comentario
      email : Correo o lista de correos electronicos para contactar
      telephone : Numero de telefono de contacto

      date_open : Fecha de creacion
      date_update : fecha de actualizacion
      date_close : fecha de cierre
      status : Estado del contacto, si se pudo contactar y se cerro el vinculo.
      email_status : estado del envio de email interno, a los asistentes
      err_email : Mensaje de error, si ocurrio, al enviar internam
    '''
    t1 = None
    okInstance = False
    t1 = arg.get('instance',None)
    if(t1 != None):
      ## tenemos una instancia
      t1.name = self.data['name']      
      t1.comment = self.data['comment']
      t1.email = self.data['email']
      t1.telephone = self.data['telephone']
      ##
      t1.date_update = timezone.now()
      t1.status = True
      t1.email_status = False
      t1.err_email = None
      okInstance = True
    else:
      t1 = Contact(name = self.data['name'],comment = self.data['comment']\
          ,email = self.data['email'], telephone = self.data['telephone']\
          ,status = True,email_status = False )

    ## Salvamos el objeto
    t1.save()    
    """
      Enviamos el Meil
    """
    if(okInstance == True):
      emailMsg = f'update Contact {t1.id}\n'
      headerEmail = f'Contact "{t1.id}" Actualizado'      
    else:      
      emailMsg = f'created Contact {t1.id}\n'
      headerEmail = f'Contact "{t1.id}" Creado'

    emailMsg += f"Nombre: {t1.name}\n"
    emailMsg += f"Telefono: {t1.telephone}\n"
    emailMsg += f"Email: {t1.email}\n"
    emailMsg += f"Comentario: {t1.comment}\n"
    

    EmailThread(registro='admin',msg=emailMsg,header=headerEmail,object=t1).start()

    # EmailThread(registro=t1,msg=emailMsg,header=headerEmail).start()
    # EmailThread(attend=True,registro=t1,msg=emailMsg,header=headerEmail).start()
    ## Envio de email a attend     

class FormEditContact(ModelForm):  
  '''
      name : Nombre      
      attend : Quien atendera el contacto
      comment : Comentario
      email : Correo o lista de correos electronicos para contactar
      telephone : Numero de telefono de contacto

      date_open : Fecha de creacion
      date_update : fecha de actualizacion
      date_close : fecha de cierre
      status : Estado del contacto, si se pudo contactar y se cerro el vinculo.
      email_status : estado del envio de email interno, a los asistentes
      err_email : Mensaje de error, si ocurrio, al enviar internam

    ## private
    date_open : Fecha de creacion
    date_update : fecha de actualizacion
    date_close : fecha de cierre
    status : Estado del contacto, si se pudo contactar y se cerro el vinculo.
    email_status : estado del envio de email interno, a los asistentes
    err_email : Mensaje de error, si ocurrio, al enviar internamente el email
  '''
  class Meta:
    model = Contact

    fields = [ 'name','comment','email','telephone'\
             , 'attend','date_open','date_update','date_close','status'\
             , 'email_status','err_email'  ]

    labels = {'name': 'Nombre'
             ,'comment': 'Mensaje'
             ,'email': 'E-mail'
             ,'telephone': 'Teléfono'             
             , 'date_open' : 'Fecha de creacion'
             , 'date_update' : 'fecha de actualizacion'
             , 'date_close' : 'fecha de cierre'
             , 'status' : 'Estado del contacto, si se pudo contactar y se cerro el vinculo.'
             , 'email_status' : 'estado del envio de email interno, a los asistentes'
             , 'err_email' : 'Mensaje de error, si ocurrio, al enviar internamente el email'
             }

    widgets = {            
             'name': forms.TextInput(attrs={ 'title':FORM_TITLE_COMPANYNAME,'placeholder': FORM_PLACEHOLDER_COMPANYNAME })
            ,'comment': Textarea(attrs={'cols':40,'rows':5,'title':FORM_TITLE_COMMENT,'placeholder': FORM_PLACEHOLDER_COMMENT })
            ,'telephone': forms.TextInput(attrs={ 'title':FORM_TITLE_TELEPHONE,'placeholder': FORM_PLACEHOLDER_TELEPHONE })            
            ,'email': Textarea(attrs={'title':FORM_TITLE_EMAIL,'placeholder': FORM_PLACEHOLDER_EMAIL})
        }   

  def is_valid(self,**args):
    """
    """
    if(self.data['emails'] == ''):
      ## self.add_error(field, error_message)
      self.add_error('emails', f"Debe cargar al menos una direccion de correo electronico.")
      return False
    return True
    valid = super(FormEditContact,self).is_valid()
    if(valid == False):
      return False
    
    return True
    
  def save(self,**arg):
    """
      @parma arg:
        - instance
        - register
    """    
    
    t1 = arg.get('instance',None)
    if(t1 == None):
      debug_print(f'No se paso la instancia "instance="')
      return None
    
    attend = None
    try:
      attend = User.objects.get(id=self.data['attend'])
    except Exception as e:
      debug_print(f"Error {e} ,al verificar User: {self.data['attend']}.")
      
    t1.name = self.data['name']         
    t1.telephone = self.data['telephone']
    t1.email = self.data['email']
    t1.comment = self.data['comment']
    
    ##    
    if(attend != None):
      t1.attend = attend

    if('status' in self.data.keys()):
      t1.status = True
    else:
      t1.status = False

    if('email_status' in self.data.keys()):
      t1.email_status = True
    else:
      t1.email_status = False

    
    t1.date_update = timezone.now()
    ## Salvamos el objeto
    t1.save()
    ## verificamos si debemos enviar el meil 
    """
      Enviamos el Meil
    """
    
    emailMsg = f'update Contact {t1.id}'
    headerEmail = f'Contact "{t1.id}" Actualizado'
    emailMsg += f"Nombre: {t1.name}\n"

    if(t1.attend != None):
      emailMsg += f"Asistente Actual: {t1.attend}\n"    

    emailMsg += f"Mensaje: {t1.comment}\n"
    emailMsg += f"E-mail: {t1.email}\n"
    emailMsg += f"Telefono: {t1.telephone}\n"

    EmailThread(registro='admin',msg=emailMsg,header=headerEmail,object=t1).start()

class FormSetContact(ModelForm):  
  '''    
        attend : Quien atendera el contacto    
    ## private    
    status : Estado del contacto, si se pudo contactar y se cerro el vinculo.
    email_status : estado del envio de email interno, a los asistentes    
  '''
  class Meta:
    model = Contact

    fields = [ 'date_open','date_update','date_close','status'\
             , 'email_status'  ]

    labels = { 'date_open' : 'Fecha de creacion'
             , 'date_update' : 'fecha de actualizacion'
             , 'date_close' : 'fecha de cierre'
             , 'status' : 'Estado del contacto, si se pudo contactar y se cerro el vinculo.'
             , 'email_status' : 'estado del envio de email interno, a los asistentes'             
             }

  def is_valid(self,**args):
    """
    """
    valid = super(FormEditContact,self).is_valid()
    if(valid == False):
      return False
    
    rval = validatinEmails(email=self.data['email'])
    if(rval == False):
      self.add_error('email', f"La direccion de Correo electronico '{self.data['email']}' no existe actualmente.")
      return False

    return True
    
  def save(self,**arg):
    """
      @parma arg:
        - instance
        - register
    """    
    t1 = arg.get('instance',None)
    if(t1 == None):
      debug_print(f'No se paso la instancia "instance="')
      return None   
    
    
    ##
    t1.date_update = timezone.now()      
    ##    
    if('status' in self.data.keys()):
      t1.status = True
    else:
      t1.date_close = timezone.now()
      t1.status = False

    if('email_status' in self.data.keys()):
      t1.email_status = True
    else:
      t1.email_status = False

    
    t1.date_update = timezone.now()
    ## Salvamos el objeto
    t1.save()
    ## verificamos si debemos enviar el meil 
    """
      Enviamos el Meil
    """
    
    emailMsg = f'update Contact {t1.id}'
    headerEmail = f'Contact Set "{t1.id}"'
    

    emailMsg += f"Nombre: {t1.name}\n"
    

    if(t1.attend != None):
      emailMsg += f"Asistente Actual: {t1.attend}\n"    

    emailMsg += f"Mensaje: {t1.comment}\n"
    emailMsg += f"E-mail: {t1.email}\n"
    emailMsg += f"Telefono: {t1.telephone}\n"

    EmailThread(registro='admin',msg=emailMsg,header=headerEmail,object=t1).start()