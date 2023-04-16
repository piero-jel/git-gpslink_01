from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from pathlib import Path
import os

from .contexto import Choice


from django.core.mail import EmailMessage
from config.apps import debug_print , createReportExcel 


## -- para el cambio de pass 
from django.contrib.auth.forms import PasswordChangeForm , SetPasswordForm ,  UserCreationForm
from Login.models import User

## -- import para el formulario contacto
from Login.forms import CustomUserCreationForm , FormularioContacto, FormEditUser, FormSendComment

from django.contrib.auth import update_session_auth_hash
from Buttons.apps import BtnWithImage
from django.db.models import Q

from django.contrib.auth.models import Group , Permission ,PermissionsMixin
from Contact.models import Contact 

from django.views.defaults import page_not_found

from Login import contexto
from .forms import FormularioCheckUser,CustomAuthenticationForm
from .query import empresa_query
from Contact.forms import FormEditContact
from Login.contexto import LABELS_GROUPS_PROGRAMADOR, LABELS_GROUPS_CLIENTE,LABELS_GROUPS_ADMIN \
                          ,LABELS_PERM_PROGRAMADOR,LABELS_PERM_CLIENTE,LABELS_PERM_ADMIN \
                          , CheckCurrentUser ,GetGroupUsers,GetGroupCurrentUser , getDataFromFilter

from Contact.forms import FormContact
import sys
from Login.contexto import EmailThread

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


from django.utils import timezone
from .contexto import getPassFromUsername



# @staff_member_required
@login_required(login_url='/login/login/')
def home_page(request):
  '''
    @fn home_page(request)
    @brief Funcion para redireccionar el usaurio logeado en funcion de los 
    permisos asignados:
      - admin     'Puede administrar los Contact (ver historial, dar de baja)'
      - attend    'Puede atender un Contact'
      - register  'Puede registrar un nuevo Contact'
    @param request : Request desde el Template.
    @return
  '''

  if request.user.has_perm('Contact.admin'):
    ## FIXME: debemos considerar sacar el acceso Admin desde el login
    # debug_print(f'root login')
    # return redirect('/login/admin/')
    return redirect('/login/view_admin/')

  ## redireccionamos a una pagina con un mensaje sobre la condicion del usuario
  debug_print('No tine los permisos suficientes')
  messages.warning(request, 'No tine los permisos suficientes')
  return redirect('/login/login/',name='login')


# @staff_member_required
@login_required(login_url='/login/login/')
def ChangePassword(request):
  '''
    @fn home_page(request)
    @brief Funcion para redireccionar el usaurio logeado en funcion de los 
    permisos asignados:
      - admin     'Puede administrar los Contact (ver historial, dar de baja)'
      - attend    'Puede atender un Contact'
      - register  'Puede registrar un nuevo Contact'
    @param request : Request desde el Template.
  '''
  contexto = {'tab_title': 'change pass','head_title': f'Cambiando la Clave "{request.user}"'}

  if request.method == 'POST':

    if(not request.POST.get("ok") and not request.POST.get("nok")):
      debug_print(f'request.POST: {request.POST}')

      return render(request, 'Login/change_password.html', 
          {'form': PasswordChangeForm(request.user,request.POST)} )
      
      
    if(request.POST.get("nok")):      
      return render(request, 'Login/change_password.html', 
          {'form': PasswordChangeForm(request.user)} )


    form = PasswordChangeForm(request.user, request.POST)

    if( form.is_valid() ):
        user = form.save()
        ## Emviamos el meil del cambio de contraseña
        # debug_print(f'old_password: {request.POST["old_password"]} new_password: {request.POST["new_password2"]}')
        EmailThread(registro=user \
          ,password = {'old_password':request.POST["old_password"] ,'new_password':request.POST["new_password2"]}\
          ,msg=f'change of password user {user}',header=f'Cambio de Contraseña User "{user}"').start()
        ## Important!
        ## Actualizamos la seccion para el usuario que cambio la contraseña
        update_session_auth_hash(request, user)  
        messages.success(request, 'Su contraseña se Modifico de forma Sastifactoria!')
        return redirect('/login/login/',name='login')
        # return redirect('/login/logout')
    else:
        messages.error(request, 'Por Favor Corrija el error y vuelva a intentarlo.')
        contexto['form'] = PasswordChangeForm(request.user, request.POST)
        return render(request, 'Login/change_password.html', contexto)
  
  contexto['form'] = PasswordChangeForm(request.user)

  return render(request, 'Login/change_password.html', contexto)



def Login(request):
  '''
    @fn Login(request)
    @brief Funcion para realizar el login de usuario.
    @param request : Request desde el Template.
    @return
  '''
  
  if (request.method == 'POST'):
    # form = AuthenticationForm(request, data=request.POST)
    form = CustomAuthenticationForm(request, data=request.POST)

    if(form.is_valid()):
      ## Obtenemos los campos desde el formulario
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      ## autentificamos el usauraio
      user = authenticate(username=username, password=password)

      if( user is not None):
        login(request, user)
        ## Obtenemos en una lista los grupos al cual pertenece 
        # el usuario logueda sastifactoriamente, redireccionamos a home de login
        return redirect('/login/')
    else:
      return render(request, 'Login/login.html', {'form': form})          

  # form = AuthenticationForm()
  form = CustomAuthenticationForm()
  return render(request, 'Login/login.html', {'form': form})


def Logout(request):
  '''
    @fn Logout(request)
    @brief Funcion para realizar el logout de la cuenta.
    @param request : Request desde el Template.
    @return
  '''
  logout(request)
  return redirect('/login/')


def PasswordChangeRequest(request):
  '''
    @fn PasswordChangeRequest()
    @brief Funcion para renderizar el formulario de pedido de cambio 
    de clave.
    @param request : Request desde el Template.
    @return
  '''
  listbtn = (BtnWithImage(path='go-previous.svg',url='/login/login/',label='Volver', msg = 'Volver a login')
    ,BtnWithImage(path='home.svg',url='/',label='Home', msg = 'Ir a la pagina Principal Home') )
  contexto = {'listbtn':listbtn}
  

  if(request.method == 'POST'):
    # debemos rescatar la info desde el formulario luego de que realiza el submit
    formularioCntacto=FormularioContacto(data=request.POST)

    if(not request.POST.get("ok") and not request.POST.get("nok")):      
      contexto['miFormulario'] = FormularioContacto()
      return render(request,"Login/password_change_request.html",contexto)

    if(request.POST.get("nok")):  
      ## Se preciono el clean del formulario
      contexto['miFormulario'] = FormularioContacto()
      return render(request,"Login/password_change_request.html",contexto)
      
    ## Si el formulario es valido, obtenemos los datos.
    luser = None
    if(formularioCntacto.is_valid()):
   
      luser = User.objects.get(username = request.POST.get('nombre'))
      ## Obtenemos el permiso, para luego usarlo en has_perm()
      new_pass = getPassFromUsername(username=luser.username)
      #debug_print(f'luser: {luser} pass: {new_pass}')
      luser.set_password(new_pass)
      luser.save()
      EmailThread(registro=luser \
          ,password = {'new_password':new_pass}\
          ,msg=f'Pedido de Blanqueo de Contraseña, Nombre de Usuario {luser}',header=f'Clean de Contraseña User "{luser}"').start()
      
      ## queda el envio de la observacion a los Admins y programadores
      if(request.POST.get('contenido') != None and request.POST.get('contenido') != ''):
        mensage = f'Pedido de Blanqueo de Contraseña, Nombre de Usuario {luser}'
        #password = {'new_password':new_pass}\
        mensage += f" Contenido del Mensage: \n{request.POST.get('contenido')}"
        EmailThread(registro='admin',msg=mensage,header=f'Msg from clean of Pass, User "{luser}"').start()



      contexto['email'] = request.POST.get('email')
      return render(request,"Login/password_change_request.html",contexto)      

    else:
      ## valid check que el nombre de usuario este en user      
      messages.error(request, 'Por Favor Corrija el error y vuelva a intentarlo.')
      contexto['miFormulario'] = formularioCntacto
      return render(request,"Login/password_change_request.html",contexto)

  contexto['miFormulario'] = FormularioContacto()
  return render(request,"Login/password_change_request.html",contexto)







@login_required(login_url='/login/login/')
def ViewAdmin(request):
  """
    @fn def ViewDataClients(request,**arg):
    @brief Funcion para visualizar los datos del Cleinte
    @param request  :
    @parama arg     :
    @return
  """
  superuser = CheckCurrentUser(req=request,user='superuser') 
  if(superuser == None):
    val = CheckCurrentUser(req=request,user='admin')
    if(val == None or val['user'] == None):
      debug_print(f'El usuario "{request.user}" no esta en el grupo Administrador ')
      return redirect('/login/')
  else:
    val = superuser
  
  list_btn = None

  if(superuser != None):
    list_btn = (      
      BtnWithImage(path='Config_02.svg',url='/login/admin/',label='Sys Admin', msg='Ingresar al Administrador del Sistema')
      ,BtnWithImage(path='config.png',url=f'/login/view_users/{val["user"].id}/',label='config user'\
        , msg='Configuracion del usaurio')
      # ,BtnWithImage(path='list-add-symbolic.svg',url=f'/login/new_administrador/',label='add admin', msg='Crear un Nuevo Administrador')
      ,BtnWithImage(path='preferences-system-search.png',url=f'/login/view_useradmin/',label='users admins'\
        , msg='Usuarios Administradores')
      
      ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')    
    )
  else:
    list_btn = (      
      BtnWithImage(path='Config_02.svg',url='/login/admin/',label='Sys Admin', msg='Ingresar al Administrador del Sistema')
      ,BtnWithImage(path='config.png',url=f'/login/view_users/{val["user"].id}/',label='config user', msg=f'Configuracion del usuario {val["user"]}')
      # ,BtnWithImage(path='list-add-symbolic.svg',url=f'/login/new_administrador/',label='add admin', msg='Crear un Nuevo Administrador')
      ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')    
    )

  listlink = [
    # {'name':'Empresas', 'link': '/login/view_business/'}          
   {'name':'Contact', 'link': '/login/view_contact/','title':'Contact'}   
   ## FIXME test only      
   #,{'name':'Reporte', 'link': '/login/view_reporte/','title':'Generacion de Reporte'}
   
  ]
  
  contexto = {'tab_title': 'admin','head_title':'Administracion', 'listlink':listlink,'listbtn':list_btn }
  return render(request,"Login/view_admin.html",contexto)




@login_required(login_url='/login/login/')
def ViewUserAdmin(request):  
  """
    @fn 
    @brief Funcion para visualizar los Admistradores
    @param request  :
    @parama arg     :
    @return
  """
  superuser = CheckCurrentUser(req=request,user='superuser')  
  if(superuser == None or superuser['is_superuser'] == False):
    debug_print(f'El usuario "{request.user}" no esta en el grupo Root.')
    return redirect('/login/')
  


  list_btn = [ 
     BtnWithImage(path='go-previous.svg',url='/login/view_admin/',label='Volver', msg = 'Volver a la Vista de Admin')
    ,BtnWithImage(path='config.png',url='/login/admin/',label='Sys Admin', msg='Ingresar al Administrador del Sistema')
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')    
    ]


  ## Si no encuentra devuelve None
  userGroups = GetGroupUsers(user='admin')


  contexto = {'tab_title': 'users admin','head_title':'Lista de Asistentes'}
  contexto['user_amdins'] = userGroups 
  ## No tenemso en la bbdd, aun
  #contexto['user_amdins'] = None


  contexto['listbtn'] = list_btn

  ## si el link a la vista no existe el template rompe
  contexto['urllink'] = 'ViewConfigUsers'
  contexto['urltitle'] = 'Click para ver informacion de '

  contexto['urlbtn_add'] = '/login/new_administrador/'
  contexto['titlebtn_add'] = "Agregar Nuevo Programador"

  
  
  return render(request,"Login/view_user_admins.html",contexto)




@login_required(login_url='/login/login/')
def ViewDataClients(request,**arg):
  """
    @fn def ViewDataClients(request,**arg):
    @brief Funcion para visualizar los datos del Cleinte
    @param request  :
    @parama arg     :
    @return
  """
  rval = CheckCurrentUser(req=request,user='admin')
  if (rval == None):
    debug_print(f'El usuario "{request.user}" no esta en el grupo Administrador ')
    return redirect('/login/')


  userId = arg.get('id',None)
  if(userId == None):
    debug_print("No se paso un id valido.")
    return redirect('/login/')
  
  try:
    luser =  User.objects.get(id=userId)
  except:
    debug_print(f"No tenemos un usuario con el ID {userId}, dentro de la tabla User")
    return redirect('/login/view_admin/')

  try:
    all_Contact = Contact.objects.filter(register=luser)
  except:
    debug_print(f"El usuario {luser}, No tiene Contact Registrados.")
    
  try:
    # rootuser = User.objects.filter(is_superuser=True,username=request.user)
    rootuser = User.objects.filter(groups=Group.objects.get(name = LABELS_GROUPS_ADMIN),username=request.user)
  except:
    debug_print(f' Fallo el intetno al intentar obtener el rootuser ')

  if(rootuser != None and len(rootuser) > 0):
    debug_print(f'rootuser: {rootuser[0]} request.user: {request.user}')


  contexto = {'tab_title': 'user data','head_title': f'Datos del Usuario {luser}'}

  list_btn = (     
    #  BtnWithImage(path='go-previous.svg',url='/login/view_clients/',label='Volver', msg = 'Volver a la Vista de Admin')
    #  BtnWithImage(path='go-previous.svg',url='javascript:history.back()',label='Volver', msg = 'Volver a la Vista de Admin')
     BtnWithImage(path='go-previous.svg',url=f'/login/view_clients/{luser.empresa.id}',label='Volver', msg = 'Volver a la Vista de Admin')
    ,BtnWithImage(path='home.svg',url='/login/view_admin/',label='Home', msg = 'Administracion, Vista Principal')
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
    )

  contexto['listbtn'] = list_btn
  contexto['luser'] = luser
  contexto['all_Contact'] = all_Contact
  contexto['urlbtn_edit'] = 'CleanPassword'
  contexto['titlebtn_edit'] = 'Click para realizar el clean del Password de'

  if(request.method == 'POST'):
    # debemos rescatar la info desde el formulario luego de que realiza el submit
    auth_form=FormularioCheckUser(data=request.POST)

    if(not request.POST.get("ok") and not request.POST.get("nok")):      
      contexto['auth_form'] = auth_form
      return render(request,"Login/view_data_user.html",contexto)

    if(request.POST.get("nok")):  
      ## Se preciono el clean del formulario
      contexto['auth_form'] = FormularioCheckUser()
      return render(request,"Login/view_data_user.html",contexto)
      
    ## Si el formulario es valido, obtenemos los datos.
    if(auth_form.is_valid() and auth_form.check_pass(user=rootuser[0])):      
      debug_print(f"Validamos, ahora podemos borrar el usuario {luser}")
      emp_id = luser.empresa.id
      luser.delete()
      return redirect(f'/login/view_clients/{emp_id}')
    else:
      messages.error(request, f'La Contraseña Ingresada para "{rootuser[0]}" es incorrecta.')

  auth_form = FormularioCheckUser()
  contexto['auth_form'] = auth_form  
  return render(request,"Login/view_data_user.html",contexto)




@login_required(login_url='/login/login/')
def CleanPassword(request,**args):
  """
    @fn def ViewDataClients(request,**arg):
    @brief Funcion para visualizar los datos del Cleinte
    @param request  :
    @parama arg     :
    @return
  """
  val = CheckCurrentUser(req=request,user='admin')
  if (val == None):
    debug_print(f'El usuario "{request.user}" no esta en el grupo Administrador ')
    return redirect('/login/')
  user_id = args.get('user_id',None)

  if(user_id == None):
    debug_print('No se paso un ID valido')
    return redirect('/login/')

  try:
    luser =  User.objects.get(id=user_id)
  except:
    debug_print(f' No tenemos un usuario con el ID{user_id}, dentro de la tabla User')
    return redirect('/login/view_admin/')
    
  urlbtn_cancel = None
  if(luser.empresa != None):
    head_title = f'Clean del Password "{luser.empresa}, {luser.username}"'
    urlbtn_cancel = f'/login/view_users/{luser.id}/'
  elif(luser.is_staff == False):
    head_title = f'Clean del Password Programador "{luser.username}"'
    urlbtn_cancel = '/login/view_programmers/'
  else:
    head_title = f'Clean del Password "{luser.username}"'
    urlbtn_cancel = f'/login/view_users/{luser.id}/'

  contexto = {'tab_title': 'clean password','head_title': head_title,'urlbtn_cancel':urlbtn_cancel}

  list_btn = ( 
     BtnWithImage(path='go-previous.svg',url=urlbtn_cancel ,label='Volver', msg = 'Volver a la Vista de Admin')
    ,BtnWithImage(path='home.svg',url='/login/',label='Home', msg = 'Administracion, Vista Principal')
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')    
    )
  contexto['listbtn'] = list_btn

  if (request.method == 'POST'):

    if(not request.POST.get("ok") and not request.POST.get("nok")):
      debug_print(f'request.POST: {request.POST}')
      contexto['form'] = SetPasswordForm(user=luser, data=request.POST )
      return render(request,"Login/clean_password.html",contexto)  
      
    if(request.POST.get("nok")):      
      contexto['form'] = SetPasswordForm(user=luser)
      return render(request,"Login/clean_password.html",contexto)  

    form = SetPasswordForm(user=luser, data=request.POST )

    if(form.is_valid()):
      user = form.save()
      ## Enviamos el Email de Cambio de Contraseña, solo tenemos la nueva clave ya que es un clean
      EmailThread(registro=user \
          ,password = {'new_password':request.POST["new_password2"]}\
          ,msg=f'clean of password user {user}',header=f'Clean de Contraseña User "{user}"').start()

      ## Important!
      ## se actualiza la seccion para el usuario que cambio su password
      update_session_auth_hash(request, user)  
      messages.success(request, f"La Contraseña para el usuario '{luser.username}' se modifico de forma Sastifactoria!")
      return redirect('/login/view_admin/')
        # return redirect('/login/logout')
    else:
      messages.error(request, 'Por Favor Corrija el error y vuelva a intentarlo.')
      contexto['form'] = form
      return render(request,"Login/clean_password.html",contexto)

  # contexto['form'] = FormularioCleanPass()
  contexto['form'] = SetPasswordForm(user=luser)
  
  return render(request,"Login/clean_password.html",contexto)  




@login_required(login_url='/login/login/')
def NewAdministrador(request):
  """
    @fn def ViewDataClients(request,**arg):
    @brief Funcion para visualizar los datos del Cleinte
    @param request  :
    @parama arg     :
    @return
  """
  val = CheckCurrentUser(req=request,user='superuser')
  if (val == None):
    debug_print(f'El usuario "{request.user}" no es root')    
    return redirect('/login/')

  contexto = {'tab_title': 'new admin','head_title':'Agregando un Nuevo Asistente'}
  list_btn = (
     BtnWithImage(path='go-previous.svg',url='/login/view_useradmin/',label='Volver', msg = 'Volver a la Vista de Admin') 
    ,BtnWithImage(path='home.svg',url='/login/view_admin/',label='Home', msg = 'Administracion, Vista Principal')
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')    
    )
  contexto['listbtn'] = list_btn

  if (request.method == 'POST'):
    # debemos rescatar la info desde el formulario luego de que realiza el submit
    if(not request.POST.get("ok") and not request.POST.get("nok")):
      debug_print(f'request.POST: {request.POST}')
      contexto['form'] = CustomUserCreationForm(request.POST )      
      return render(request,"Login/form_new_user.html",contexto)

    if(request.POST.get("nok")):
      ## cancelamos la creacion del nuevo usuario
      contexto['form'] = CustomUserCreationForm( )      
      return render(request,"Login/form_new_user.html",contexto)
    ## por defecto request.POST.get("ok")
    form = CustomUserCreationForm(request.POST )
    if(form.is_valid()):      
      nuser = form.save()
      ## ahora le damos el permiso de staff
      nuser.is_staff = True
      nuser.save()
      ## Asignamos al nuevo usuario al Grupo Administrador      
      try:
        nuser.groups.add(Group.objects.get(name = LABELS_GROUPS_ADMIN))
      except:
        
        debug_print(f"No tenemos un Grupo con el nombre '{LABELS_GROUPS_ADMIN}' y etiqueta 'Contact | Contact | Puede Administrar los Contact'.")

        try:
          new_group, created = Group.objects.get_or_create(name =LABELS_GROUPS_ADMIN)
          permission = Permission.objects.get(codename='admin') 
          new_group.permissions.add(permission)
          ## volvemos a intentar agregar al grupo
          nuser.groups.add(Group.objects.get(name = LABELS_GROUPS_ADMIN))
          debug_print(f"Se creo de forma sastifactoria el Grupo '{LABELS_GROUPS_ADMIN}', con los permisos necesarios.")          
        except:
          debug_print(f"Error '{sys.exc_info()[1]}' en la creacion del Grupo '{LABELS_GROUPS_ADMIN}'.")
          messages.error(request,f"No tenemos un Grupo con el nombre '{LABELS_GROUPS_ADMIN}' y etiqueta 'Contact | Contact | Puede Administrar los Contact'.")
          return redirect('/login/view_admin/')        

      # user = form.save()
      # update_session_auth_hash(request, user)  # Important!
      #debug_print(f"Se crea un nuevo Administrador '{nuser}' de forma Sastifactoria!")            
      return redirect('/login/view_useradmin/')
      # return redirect('/login/view_admin/')
        
    else:
      messages.error(request, 'Por Favor Corrija el error y vuelva a intentarlo.')
      contexto['form'] = form
      return render(request,"Login/form_new_user.html",contexto)
  
  contexto['form'] = CustomUserCreationForm()
  # debug_print(f"contexto['form'] {contexto['form']}")

  return render(request,"Login/form_new_user.html",contexto)



@login_required(login_url='/login/login/')
def ViewConfigUsers(request,**arg):
  """
    @fn def ViewConfigUsers(request,**arg):
    @brief Funcion para visualizar los datos de un Cliente de una comapnia
    @param request  :
    @parama arg     :
    @return
  """
  id_emp = arg.get('id',None)
  if(id_emp == None):
    debug_print("No se paso un id de empleado")
    return redirect('/login/view_admin/')

  val = CheckCurrentUser(req=request,user='admin')
  rootuser = None
  if(val != None):
    rootuser = val['user']
  

  try:
    luser = User.objects.get(id=id_emp)
  except:
    debug_print(f"No tenemos un usuario con el ID{id_emp}, dentro de la tabla User")
    return redirect('/login/view_admin/')

  if(rootuser == None):    
    try:
      # rootuser =  User.objects.get(username=request.user)
      if(User.objects.get(username=request.user) != luser):
        debug_print(f'El usuario {rootuser} esta intendo editar el usaurio {luser}')
        return redirect('/login/')
    except:
      debug_print(f'failure: User.objects.get(username={request.user})')
      return redirect('/login/')



  ## FIXME add filter
  query = request.GET.get('q', None)
  
  all_Contact = getDataFromFilter(object=Contact,q=query,filter={'register':luser})
  if(all_Contact == None):
    if(not query in (None, '') ):
      messages.success(request,f"Sin Resultados para la busqueda: \"{query}\"")
    try:
        all_Contact = Contact.objects.filter(register=luser).order_by('-id')
    except:
      debug_print(f"El usuario {luser}, No tiene Contact Registrados.")



  head_title = f'Administrador: {luser}'
  tab_title = f' config user'
  # tab_title = f' admin {str(luser).lower()}'


  contexto = {'tab_title': str(tab_title).lower(),'head_title': head_title}

  
  
  if(luser.empresa == None ):
    ## luser es el admin user y esta editandose a si mimso       
    if(CheckCurrentUser(req=request,user='superuser') != None):
      list_btn = (         
        BtnWithImage(path='go-previous.svg',url=f'/login/view_admin',label='Volver', msg = f'Volver a la Vista Anterior')        
        ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
        )
      contexto['rootuser'] = True
      contexto['urlbtn_resetpass'] = 'CleanPassword'
      contexto['titlebtn_resetpass'] = 'Click para realizar el clean del Password de'
      contexto['labelbtn_resetpass'] = 'Reset Pass'
    else:
      list_btn = (         
        BtnWithImage(path='go-previous.svg',url=f'/login/view_admin',label='Volver', msg = f'Volver a la Vista principal')
        ,BtnWithImage(path='home.svg',url='/login/view_admin/',label='Home', msg = 'Administracion, Vista Principal')
        ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
        )
      contexto['rootuser'] = False
      contexto['urlbtn_cleanpass'] = 'ChangePassword'
      contexto['titlebtn_cleanpass'] = 'Click para realizar el cambio de Contraseña'
      contexto['labelbtn_cleanpass'] = 'Change Pass'

    
  # else:
  #   list_btn = (         
  #   BtnWithImage(path='go-previous.svg',url=f'/login/view_company/{luser.empresa.id}',label='Volver', msg = f'Volver a la Vista con informacion de la empresa {luser.empresa}')
  #   ,BtnWithImage(path='home.svg',url='/login/view_admin/',label='Home', msg = 'Administracion, Vista Principal')
  #   ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
  #   )
      


  #   ## url para editar el Contact
  #   contexto['urledit'] = 'EditContactRegister'
  #   contexto['urledittitle'] =f'Click para Editar el Contact: '
  #   ## url para ver los registro completos, de trabajo, sobre el Contact
  #   contexto['urlview'] = 'ViewRegisterWorks'
  #   contexto['urlviewtitle'] = f'Click para Ver el registro completo de trabajo sobre el Contact '
    
    






  contexto['titlebtn_edit'] = f'Click para editar el usuario {luser}'
  contexto['labelbtn_edit'] = 'Editar' 

  contexto['listbtn'] = list_btn
  contexto['luser'] = luser
  if(all_Contact != None and len(all_Contact)>0):
    contexto['all_Contact'] = all_Contact

  

  if(request.method == 'POST'):
    # debemos rescatar la info desde el formulario luego de que realiza el submit
    if(not request.POST.get("ok") and not request.POST.get("edit_ok") and not request.POST.get("edit_nok")):
      debug_print(f'request.POST: {request.POST}')
      contexto['auth_form'] = FormularioCheckUser()      
      # contexto['user_form'] = CustomUserCreationForm(instance=luser)      
      contexto['user_form'] = FormEditUser(data=luser)      
      return render(request,"Login/view_company_clients.html",contexto)
      
    if(request.POST.get("ok") and rootuser != None):
      auth_form=FormularioCheckUser(data=request.POST)
      ## Si el formulario es valido, obtenemos los datos.
      if(auth_form.is_valid() and auth_form.check_pass(user=rootuser)):      
        debug_print(f"Validamos, ahora podemos borrar el usuario {luser}")
        if(luser.empresa != None):
          emp_id = luser.empresa.id
          luser.delete()        
          return redirect(f'/login/view_clients/{emp_id}')
        luser.delete()        
        return redirect(f'/login/')
      else:
        messages.error(request, f'La Contraseña Ingresada para "{rootuser}" es incorrecta.')

    if(request.POST.get("edit_nok") ):
      contexto['auth_form'] = FormularioCheckUser()      
      # contexto['user_form'] = CustomUserCreationForm(instance=luser)
      contexto['user_form'] = FormEditUser(data=luser)      
      return render(request,"Login/view_company_clients.html",contexto)

    if(request.POST.get("edit_ok") ):
      # user_form=CustomUserCreationForm(request.POST)
      user_form = FormEditUser(request.POST)
      if(user_form.is_valid(instance=luser)):
        user_form.save(instance=luser)
        contexto['head_title'] = f'{luser.empresa}, {luser}'
        return redirect(f'/login/view_users/{luser.id}')
        # debug_print(f'user_form: {user_form}')
      else:
        debug_print(f'Form No validado')
        contexto['auth_form'] = FormularioCheckUser()  
        contexto['user_form'] = user_form
        contexto['user_form_popUp'] = True        
        messages.error(request, f' Error al ntentar editar "{luser.empresa}, {luser}", Corrija y vuelva a intentarlo.')
        return render(request,"Login/view_company_clients.html",contexto)


  contexto['auth_form'] = FormularioCheckUser()
  # contexto['user_form'] = CustomUserCreationForm(instance=luser)
  contexto['user_form'] = FormEditUser(data=luser)

  return render(request,"Login/view_company_clients.html",contexto)  
  


@login_required(login_url='/login/login/')
def ViewContact(request,**arg):
  """
    @fn def ViewContact(request,**arg):
    @brief Funcion para visualizar los datos de un Cliente de una comapnia
    @param request  :
    @parama arg     :
    @return
  """  
  
  val = CheckCurrentUser(req=request,user='admin')
  if (val == None):
    debug_print(f'El usuario "{request.user}" no esta en el grupo Administrador ')
    return redirect('/login/')
  ##
  all_Contact = None

  contexto = {'tab_title': 'Contact','head_title': 'Lista de Contactactos'}

  list_btn = (         
     BtnWithImage(path='go-previous.svg',url=f'/login/view_admin',label='Volver', msg = 'Administracion, Vista Principal')    
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
   )


  try:
    all_Contact = Contact.objects.all().order_by('-id')
  except Exception as e:
    debug_print(f"Error {e}, Contact.objects.all().order_by('-id')")
    return redirect('/login/view_admin/')


  contexto['listbtn'] = list_btn  
  contexto['all_Contact'] = all_Contact
  contexto['urllink'] = '/login/view_expand_contact'
  contexto['urltitle'] = 'Click para expandir informacion del Contact '

  return render(request,"Login/view_contact.html",contexto)  


from Contact.forms import FormSetContact
@login_required(login_url='/login/login/')
def ViewExpandContact(request,**arg):
  """
    @fn def ViewContact(request,**arg):
    @brief Funcion para visualizar los datos de un Cliente de una comapnia
    @param request  :
    @parama arg     :
    @return
  """  
  
  val = CheckCurrentUser(req=request,user='admin')
  if (val == None):
    debug_print(f'Login.ViewExpandContact(): El usuario "{request.user}" no esta en el grupo Administrador')
    return redirect('/login/')

  word = arg.get('word',None)
  lid = arg.get('id',None)
  if(lid == None ):
    debug_print('Login.ViewExpandContact(): No se paso el id')
    return redirect('/login/')

  
  contexto = {'tab_title': f'ExpandContact {lid}',}

  list_btn = (         
     BtnWithImage(path='go-previous.svg',url=f'/login/view_contact/',label='Volver', msg = 'Administracion, Vista Principal') 
    ,BtnWithImage(path='home.svg',url='/login/view_admin/',label='Home', msg = 'Ir a la pagina Principal Home')    
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
   )


  contexto['listbtn'] = list_btn    
  contexto['urllink'] = '/login/view_expand_contact'
  contexto['urltitle'] = 'Click para editar la Informacion del Contact '

  try:
    lContact = Contact.objects.get(id=lid)
  except:
    debug_print(f"fallo la query al intentar obtener el Contact con el id {lid}.")
    return redirect('/login/view_admin/')
  contexto['lContact'] = lContact

  
  if(request.method == 'POST'):
    
    if(request.POST.get("edit_nok") ):
      contexto['Contact_form'] = None
      return redirect(f'/login/view_expand_contact/{lContact.id}')

    elif(request.POST.get("edit_ok") ):      
      Contact_form = FormEditContact(request.POST)
      
      if(Contact_form.is_valid()):        
        Contact_form.save(instance=contexto['lContact'])
        # debug_print(f'user_form: {user_form}')
        return redirect('/login/view_expand_contact/')
      
      else:
        debug_print(f'Form No validado: {Contact_form}')        
        contexto['Contact_form'] = Contact_form                
        #messages.error(request, f' Error al intentar editar "{contexto["lContact"].id}", Corrija y vuelva a intentarlo.')
        return render(request,"Login/view_expand_contact.html",contexto)

    elif(request.POST.get("okpopUp02")):
      formulario = FormSetContact(data=request.POST)

      
      if(formulario.is_valid()):  
        formulario.save(instance=lContact)
        return redirect(f'/login/view_expand_contact/{lContact}/')
      else:
        messages.warning(request, 'Datos Invalidos')
        # debug_print(f'Formulario no Valido: {formulario} ')
        contexto['form_popup02'] = formulario
        return render(request,"Login/view_expand_contact.html",contexto)    
    else:
      debug_print(f'request.POST: {request.POST}')      
      if('lContact' in contexto.keys()):
        contexto['Contact_form'] = FormEditContact(instance=contexto['lContact'])
      else:
        contexto['Contact_form'] = FormEditContact(request.POST)        
      
      return render(request,"Login/view_expand_contact.html",contexto)

  if(word == 'edit' and 'lContact' in contexto.keys()):
    contexto['Contact_form'] = FormEditContact(instance=contexto['lContact'])

  contexto['form_popup02'] = FormSetContact(instance=lContact)

  return render(request,"Login/view_expand_contact.html",contexto)  






@login_required(login_url='/login/login/')
def EditContactRegister(request,**arg):
  """
    @fn def EditContactRegister(request,**arg):
    @brief Funcion para visualizar los datos de un Cliente de una comapnia
    @param request  :
    @parama arg     :
  """
  rval = CheckCurrentUser(req=request,user='admin')
  if (rval == None):
    debug_print(f'El usuario "{request.user}" no esta en el grupo Administrador ')
    return redirect('/login/')


  ContactId = arg.get('id',None)
  if(ContactId == None):
    debug_print("No se paso un id ")
    return redirect('/login/view_admin/')
  
  lContact = None
  try:
    lContact = Contact.objects.get(id=ContactId)
  except:
    debug_print(f"Fallo la Query : Contact.objects.get(id={ContactId})")
    return redirect('/login/')

  ## el get falla si el item no existe, estaria demas
  if(lContact == None):
    debug_print(f"El Contact con ID : {ContactId}, No esta Registrado.")
    return redirect('/login/')


  head_title = f'{lContact.register.empresa} {lContact.register.username}, Editando Contact'    
  contexto = {'tab_title': 'edit Contact','head_title': head_title}
  
  list_btn = (         
    BtnWithImage(path='go-previous.svg',url=f'/login/view_users/{lContact.register.id}/',label='Volver', msg = f'Volver a la Vista anterior')
    ,BtnWithImage(path='home.svg',url='/login/view_admin/',label='Home', msg = 'Administracion, Vista Principal')
    ,BtnWithImage(path='exit.png',url='/login/logout',label='Salir')
    )    
  contexto['listbtn'] = list_btn 

  
  if(request.method == 'POST'):
    # debemos rescatar la info desde el formulario luego de que realiza el submit
    if(not request.POST.get("ok") and not request.POST.get("nok")):
      debug_print(f'request.POST: {request.POST}')      
      contexto['Contact_form'] = FormEditContact(instance=lContact)      
      return render(request,"Login/form_edit_Contact.html",contexto)

    
    if(request.POST.get("nok") ):      
      return redirect(f"/login/view_users/{lContact.register.id}/")

    if(request.POST.get("ok") ):      
      Contact_form = FormEditContact(request.POST)      
      if(Contact_form.is_valid()):        
        Contact_form.save(instance=lContact)        
        return redirect(f"/login/view_users/{lContact.register.id}/")
      else:
        debug_print(f'Form No validado')        
        contexto['Contact_form'] = Contact_form                
        messages.error(request, f' Error al intentar editar "{lContact.id}", Corrija y vuelva a intentarlo.')
        return render(request,"Login/form_edit_Contact.html",contexto)

  contexto['Contact_form'] = FormEditContact(instance=lContact)

  return render(request,"Login/form_edit_Contact.html",contexto)

# 'Empresa': {'url':'/login/view_business/','Template':'Login/view_business.html','Models':Empresa}.upate({'tab_title': 'companies','head_title':'Lista de Empresas Registradas'})
TABLA_and_VIEWS_RET = {    
   'Contact': {'url':'#','Models':Contact}  
  ,'Cliente':{'url':'/login/view_clients/','Models':User}
}

@login_required(login_url='/login/login/')
def DeleteRegister(request,**args):
  """
    @fn
    @brief 
    @param 
    @return  
  """
  rval = CheckCurrentUser(req=request,user='admin')
  if (rval == None):
    debug_print(f'El usuario "{request.user}" no esta en el grupo Administrador ')
    return redirect('/login/')

  regid = args.get('id',None)
  tablaname = args.get('word',None)
  if(regid == None or tablaname == None):
    debug_print(f'No tenemos Id "{regid}" o Tabla "{tablaname}" para realizar el delete del Registro')
    return redirect('/login/view_admin/')
  
  debug_print(f'Id "{regid}" Tabla "{tablaname}" para realizar el delete del Registro')

  register = TABLA_and_VIEWS_RET[tablaname]
  debug_print(f'register "{register}" register["url"] \"{register["url"]}\" para realizar el delete del Registro')
  try:
    # Empresa.objects.get(id=regid).delete()
    register['Models'].objects.get(id=regid).delete()
  except:
    debug_print(f'No se pudo elimino el Registro Id "{regid}" de la Tabla "{tablaname}".')
    return redirect(register['url'])  

  debug_print(f'Se elimino el Registro Id "{regid}" de la Tabla "{tablaname}".')
  return redirect(register['url'])
  



def Error_404(request,exception):
  """
    @fn
    @brief 
    @param 
    @return  
  """
  tamplate_name = 'Login/404.html'
  return page_not_found(request,exception=None, template_name=tamplate_name)
"""
  def handler404(request, exception, template_name="404.html"):
    response = render_to_response(template_name)
    response.status_code = 404
    return response
"""

def Error_500(request, *args, **argv):
  """
    @fn
    @brief 
    @param 
    @return  
  """
  return render(request, 'Login/500.html', status=500)  
