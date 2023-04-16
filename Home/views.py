from django.shortcuts import render, redirect
from django.http import HttpResponse
#from django.views.generic import TemplateView
# Create your views here.
from Contact.apis import FromSendComment
from Contact.forms import FormContact



#class HomePageView(TemplateView):
def ViewHomePage(request):
  contexto = {'tab_title': 'HOFFSEL'}

  if(request.method == 'POST'):
    rval = FromSendComment(solicitud=request)

    if(rval == None):
      contexto['formulario'] = FormContact()
      return render(request,"Home/home.html",contexto)

    if(rval['status'] == True):      
      return redirect('/contact/?valid')
    
    if(rval['status'] == False):      
      contexto['formulario'] = rval['form']
      return render(request,"Home/home.html",contexto)
  
  contexto['formulario'] = FormContact()
  # contexto['formulario'] = FormSendComment()


  return render(request,"Home/home.html",contexto)
