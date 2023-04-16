from django.db.models.fields import NullBooleanField
from django.shortcuts import redirect, render

# Create your views here.
from Contact.models import Contact 
from Contact.forms import FormContact
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from Buttons.apps import BtnWithImage, BtnForm ,BtnFormWithImage
## para debug sobre los templates
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.conf import settings

from Login.contexto import CheckCurrentUser 
from config.apps import debug_print

from Contact.apis import FromSendComment




def SendComment(request):
  """
    @fn PasswordChangeRequest()
    @brief Funcion para renderizar el formulario de pedido de cambio 
    de clave.
    @param request : Request desde el Template.
    @return
  """
  

  if('valid' in request.GET.keys()):
    contexto = {'tab_title': 'send comment'}
  else:
    listbtn = (BtnWithImage(path='home.svg',url='/',label='Home', msg = 'Ir a la pagina Principal Home'),)
    contexto = {'listbtn':listbtn,'tab_title': 'send comment','head_title': 'Envio de Comentario'}  

  
  
  if(request.method == 'POST'):
    rval = FromSendComment(solicitud=request)

    if(rval == None):
      contexto['miFormulario'] = FormContact()
      return render(request,"Contact/send_comment.html",contexto)

    if(rval['status'] == True):
      return redirect('/contact/?valid')
    
    if(rval['status'] == False):      
      contexto['miFormulario'] = rval['form']
      debug_print(f'failure {rval["form"]}')
      return render(request,"Contact/send_comment.html",contexto)
  
  contexto['miFormulario'] = FormContact()
  # contexto['miFormulario'] = FormSendComment()
  return render(request,"Contact/send_comment.html",contexto)


##
## Empresa
def ViewsEmpresa(request):
  contexto = {}
  return render(request,"Contact/views_empresa.html",contexto)

def ViewsEmpresaTrabajaEnHoffsel(request):
  contexto = {}
  return render(request,"Contact/views_empresa_trabaja_en_hoffsel.html",contexto)

def ViewsEmpresaAlianzasSociosEmpresa(request):
  contexto = {}
  return render(request,"Contact/views_empresa_alianzas_socios.html",contexto)

##
## Productos
def ViewsProductos(request):
  contexto = {}
  return render(request,"Contact/views_productos.html",contexto)

def ViewsProductosGPSlink(request):
  contexto = {}
  return render(request,"Contact/views_productos_gps_link.html",contexto)
  


def ViewsProductosVirtualC(request):
  contexto = {}
  return render(request,"Contact/views_productos_virtual_c.html",contexto)

##
## Servicios
def ViewsServicios(request):
  contexto = {}
  return render(request,"Contact/views_servicios.html",contexto)


def ViewsServiciosPortalOperativo(request):
  contexto = {}
  return render(request,"Contact/views_servicios_portal_operativo.html",contexto)


def ViewsServiciosGestionTransporte(request):
  contexto = {}
  return render(request,"Contact/views_servicios_gestion_transporte.html",contexto)


