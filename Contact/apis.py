
from django.contrib import messages

from Contact.forms import FormContact


def FromSendComment(**args):
  '''
    @fn FromSendComment()
    @brief Funcion para atender el formulario form_send_comment    
    @param args
      * request

    @return return {'status': {True|False}, 'form': formulario ,'request':request}
      <> {'status': True, 'form': None ,'request':request}
      <> {'status': False, 'form': miFomr ,'request':request}

  '''
  request = args.get('solicitud',None)
  if(request == None):
    return None
  
  if(request.method == 'POST'):
    # debemos rescatar la info desde el formulario luego de que realiza el submit
    # formularioCntacto=FormSendComment(data=request.POST)
    formularioCntacto=FormContact(data=request.POST)

    if((not request.POST.get("ok") and not request.POST.get("nok")) or request.POST.get("nok")):
      return {'status': False, 'form': FormContact() ,'request':request}
    
    ## Si el formulario es valido, obtenemos los datos.    
    if(formularioCntacto.is_valid() == True):
      formularioCntacto.save()
      messages.success(request, f"Su mensaje fue enviado de forma Satisfactoria.\n Muchas Gracias.")
      return {'status': True, 'form': None,'request':request }      

    else:
      ## valid check que el nombre de usuario este en user      
      messages.error(request, 'Por Favor Corrija el error y vuelva a intentarlo.')      
      return {'status': False, 'form': formularioCntacto, 'request':request }      
  
  return None 
  