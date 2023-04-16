from django.contrib.auth.forms import UserCreationForm, UserChangeForm 
from django import forms 

from .models import User
from django.forms import ModelForm ,Textarea ,BaseForm
from django.utils import timezone
# from django.core.exceptions import ValidationError
from config.apps import debug_print, check_phoneNumber,validatinEmails
from django.contrib.auth.hashers import check_password
from Login.contexto import EmailThread
import re
from Login.contexto import LABELS_PERM_PROGRAMADOR,LABELS_PERM_CLIENTE,LABELS_PERM_ADMIN

from config.settings import FORM_TITLE_USERNAME,FORM_TITLE_FIRSTNAME,FORM_TITLE_LASTNAME,FORM_TITLE_EMAIL ,\
  FORM_TITLE_TELEPHONE,FORM_TITLE_COMMENT,FORM_TITLE_COMPANYNAME,FORM_TITLE_COMPANYTEL1,FORM_TITLE_COMPANYTEL2

from config.settings import FORM_PLACEHOLDER_USERNAME, FORM_PLACEHOLDER_FIRSTNAME,FORM_PLACEHOLDER_LASTNAME,\
  FORM_PLACEHOLDER_EMAIL,FORM_PLACEHOLDER_TELEPHONE,FORM_PLACEHOLDER_COMMENT,FORM_PLACEHOLDER_COMPANYNAME,\
  FORM_PLACEHOLDER_COMPANYTEL1,FORM_PLACEHOLDER_COMPANYTEL2     



class CustomUserCreationForm(UserCreationForm):

  class Meta:
    model = User
    fields = ['username','first_name','last_name','telefono','email','empresa']
    # fields = ('username',)
    labels = {'username': 'Nombre de Usuario'
             ,'first_name': 'Primer Nombre'
             ,'last_name': 'Apellido del contacto'
             ,'telefono': 'Numero Telefono'             
             ,'email': 'Direccion de Correo electronico '             
             ,'empresa' : 'Empresa'
             }

    widgets = {
            # 'detail': Textarea(attrs={'cols': 50, 'rows': 10}),
             'username': forms.TextInput(attrs={'title':FORM_TITLE_USERNAME,'placeholder':FORM_PLACEHOLDER_USERNAME})
            ,'first_name': forms.TextInput(attrs={'title':FORM_TITLE_FIRSTNAME,'placeholder':FORM_PLACEHOLDER_FIRSTNAME})
            ,'last_name': forms.TextInput(attrs={'title':FORM_TITLE_LASTNAME,'placeholder': FORM_PLACEHOLDER_LASTNAME })
            ,'telefono': forms.TextInput(attrs={'title':FORM_TITLE_TELEPHONE,'placeholder':FORM_PLACEHOLDER_TELEPHONE})
            ,'email': forms.TextInput(attrs={'title':FORM_TITLE_EMAIL,'placeholder':FORM_PLACEHOLDER_EMAIL})
            
        }

  def is_valid(self):
    valid = super(CustomUserCreationForm,self).is_valid()     
    if(valid == False):      
      return False
        
    rval = validatinEmails(email=self.data['email'])
    if(rval == False):
      self.add_error('email', f"La direccion de Correo electronico '{self.data['email']}' no existe actualmente.")
      return False

    return True   
    

### coustom autentificacion del formulario
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
  ### eliminamos la etiquetas, formato de bootstrap
  # username=forms.CharField(label='Nombre Usuario',required =True,\
  #   widget=forms.TextInput(attrs={'autofocus': True ,'placeholder':'Nombre de Usaurio','title':'Ingrese su Nombre de Usaurio'}))

  # password = forms.CharField(label='Contraseña',min_length=5, max_length=30, 
  #   widget=forms.PasswordInput(render_value=False,attrs={'placeholder':'Contraseña','title':'Ingrese Su Contraseña'}))

  username=forms.CharField(required =True,label='None',\
    widget=forms.TextInput(attrs={'autofocus': True ,'placeholder':'Nombre de Usaurio','title':'Ingrese su Nombre de Usaurio/Username'}))

  password = forms.CharField(required =True,label='',min_length=5, max_length=30, 
    widget=forms.PasswordInput(render_value=False,attrs={'placeholder':'Contraseña','title':'Ingrese Su Clave/Contraseña'}))
  

    
class CustomUserChangeForm(UserChangeForm):

  class Meta:
      model = User
      fields = ('username',)

"""
  Formulario para el pedido de cambio de contraseña
"""
class FormularioContacto(forms.Form):
  """
    * nombre : Nombre de Usuario
    * email  : Direcion de email donde notificara
    * contenido : Mensaje
  """
  nombre=forms.CharField(label='Nombre Usuario',required =True,\
    widget=forms.TextInput(attrs={'autofocus': True ,'placeholder':FORM_PLACEHOLDER_USERNAME,'title':FORM_TITLE_USERNAME}))

  email=forms.EmailField(label='Email',required =True,\
    widget=forms.TextInput(attrs={'autofocus': True ,'placeholder':FORM_PLACEHOLDER_EMAIL,'title':FORM_TITLE_EMAIL}))

  contenido=forms.CharField(label='Observaciones',required=False,max_length=500,\
    widget=forms.Textarea(attrs={'autofocus': True ,'placeholder':FORM_PLACEHOLDER_COMMENT,'title':FORM_TITLE_COMMENT}))

  def is_valid(self,**args):    
    valid = super(FormularioContacto,self).is_valid()     
    if(valid == False):      
      return False
    user = None
    try:
       user = User.objects.get(username = self.data['nombre'] )
    except Exception as e:
      debug_print(f'Error {e}')
      # self.add_error('nombre', f"Fail {e},  Usuario '{self.data['nombre']}' No Existe.")
      self.add_error('nombre', f"El Usuario '{self.data['nombre']}' No Existe.")
      return False      
    
    if(user.email == None or user.email == ''):
      self.add_error('nombre', f"El usuario '{self.data['nombre']}' no tiene una direccion de correo electronico cargada, contacte al administrador.")
      return False
    else:
      if(user.email != self.data['email']):
        self.add_error('email', f"La direccion de Correo Electronico '{self.data['email']}' no coincide con la cargada actualmente, contacte al administrador.")
        return False
    ## No se debe permitir al root cambia la clave de esta forma
    try:
      if(user.is_superuser == True):
        self.add_error('nombre', f"La clave para el Usuario '{self.data['nombre']}' no puede ser blanqueada de esta forma.")
        return False        
    except:
      pass 
    
    # if( user.has_perm(LABELS_PERM_ADMIN) == True or\
    #     user.has_perm(LABELS_PERM_PROGRAMADOR) == True or\
    #     user.has_perm(LABELS_PERM_CLIENTE) == False):
    #   self.add_error('nombre', f"La clave para el Usuario '{self.data['nombre']}' no puede ser blanqueada de esta forma.")
    #   return False

    

    if(user != None):
      debug_print(f'user: {user}')
      return True
    self.add_error('nombre', f"El Usuario '{self.data['nombre']}' No Existe.")
    return False
    

class FormSendComment(forms.Form):
  """
    * firstname : Primer nombre 
    * lastname  : Apellido
    * email     : Direccion de Correro electronico
    * comment   : Comentario
  """  
  firstname = forms.CharField(label='Nombre Usuario',required =True,\
    widget=forms.TextInput(attrs={'autofocus': True ,'placeholder':FORM_PLACEHOLDER_FIRSTNAME,'title':FORM_TITLE_FIRSTNAME }) )

  lastname = forms.CharField(label='Apellido',required =True,\
    widget=forms.TextInput(attrs={'autofocus': False ,'placeholder':FORM_PLACEHOLDER_FIRSTNAME,'title':FORM_TITLE_LASTNAME}) )  

  email=forms.EmailField(label='Dirreccion de Correo Electronico',required =True ,\
    widget=forms.TextInput(attrs={'autofocus': False ,'placeholder':FORM_PLACEHOLDER_EMAIL, 'title':FORM_TITLE_EMAIL}) )

  comment=forms.CharField(label='Comentario',required=True,max_length=500,\
    widget=forms.Textarea(attrs={ 'autofocus': False ,'placeholder':FORM_PLACEHOLDER_COMMENT,'cols': 50, 'rows': 5,
      'title':FORM_TITLE_COMMENT}) )



  def is_valid(self,**args):    
    valid = super(FormSendComment,self).is_valid()
    if(valid == False):      
      return False
    return True
    
  def get_msg(self) -> str:    
    rval = f"firstname: {self.data['firstname']}\n"
    rval += f"lastname: {self.data['lastname']}\n"
    rval += f"email: {self.data['email']}\n"
    rval += f"comment: {self.data['comment']}\n"
    return rval


"""
  Formulario para check de contraseña
"""
class FormularioCheckUser(forms.Form):
  password = forms.CharField(label='Contraseña',min_length=5, max_length=30, widget=forms.PasswordInput(render_value=False))
  # confirm_password = forms.CharField(label='Confirme Contraseña',max_length=30, widget=forms.PasswordInput(render_value=False))  
  # def __init__(self, **args) -> None:
  #   pass
  def check_pass(self,**args):
    user=args.get("user",None)
    if(user == None):
      debug_print('No se paso un user valido')  
      return False
    # debug_print(f'Formulario valido: {self.data["password"]}')  
    # debug_print(f'user valido: {user.password}')

    return check_password(password=self.data["password"],encoded=user.password)
  
class FormEditUser(forms.Form):
  username = forms.CharField(required = True,label='Nombre Usuario', max_length=150,\
    widget=forms.TextInput(attrs={'autofocus': True ,'placeholder':FORM_PLACEHOLDER_USERNAME,'title':FORM_TITLE_USERNAME}))

  first_name = forms.CharField(required = False,label='Nombre', max_length=30,\
    widget=forms.TextInput(attrs={'autofocus': False ,'placeholder':FORM_PLACEHOLDER_FIRSTNAME,'title':FORM_TITLE_FIRSTNAME}))

  last_name = forms.CharField(required = False,label='Apellido', max_length=150,\
    widget=forms.TextInput(attrs={'autofocus':False ,'placeholder':FORM_PLACEHOLDER_LASTNAME,'title':FORM_TITLE_LASTNAME}))

  telefono = forms.CharField(required = False,label='Numero Telefono', max_length=50,\
    widget=forms.TextInput(attrs={'autofocus':False,'placeholder':FORM_PLACEHOLDER_TELEPHONE,'title':FORM_TITLE_TELEPHONE}))

  email = forms.EmailField(required = False,label='Direccion de Correo',\
    widget=forms.TextInput(attrs={'autofocus':False,'placeholder':FORM_PLACEHOLDER_EMAIL,'title':FORM_TITLE_EMAIL}))

  def save(self,**args):
    # debug_print(f'self.data {self.data}')
    instance = args.get('instance',None)
    if(instance == None):
      debug_print(f'Falta la instance donde almacenar el form')
      return 
    instance.username = self.data['username']
    instance.first_name = self.data['first_name']
    instance.last_name = self.data['last_name']
    instance.telefono = self.data['telefono']
    instance.email = self.data['email']
    instance.save()
    ## add emvio de email cunaod se edite un usuario
    EmailThread(registro=instance,msg=f'update user {instance}',header=f'User "{instance}" Actualizado').start()

  def is_valid(self,**args):
    # instacompany = args.get("instance",None)
    # data = self.data
    instance = args.get('instance',None)
    valid = super(FormEditUser,self).is_valid()     
    if(valid == False):      
      return False

    ## FIXME add check tel number
    if('telefono' in self.data.keys()):
      if(check_phoneNumber(number=self.data['telefono']) == False):
        self.add_error('telefono', f"Numero de telefono invalido.")
        return False      
    ##endif
    if(instance == None or self.data['username'] == instance.username):
      return True

    
    luser = None
    try:
      luser = User.objects.filter(username=self.data['username'])
    except:
      luser = None
      debug_print(f'Fallo la query: User.objects.filter(username={self.data["username"]})')

    if(luser == None):
      self.add_error('username', f"Fallo la quey para verificar el Nombre de usuario: {self.data['username']}.")
      return False
    
    if(len(luser) == 0 ):
      return True
    else:
      self.add_error('username', f"Ya tenemos un Nombre de Usuario registrado con {self.data['username']}, vuelva a editar el mismo.")
      return False

