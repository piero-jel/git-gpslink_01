## para ser valido el modulo debemos agragar la instancia, de lo contrario 
## tendremos un error 
from django import template
import re

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from config.apps import debug_print
'''
  Si es la primera ves que se llama el modulo y crea
  debemos reinciar el server
'''
register = template.Library()

'''
  ex:
  <small><a href="{{it.url}}" class="d-md-block"> {{it.label|find:" "}}</a></small>
'''


'''
  ex:
    <small>
      <a href="{{it.url}}" class="d-md-block"> 
        {%for it in it.label|getList %}
          <div>
            {{it}}
          </div>
        {%endfor%}                    
      </a>
    </small>
'''
''' 
@register.filter(name='getList')
def getList(value):
  return value.split()

@register.filter(name='getLenList')
def getLenList(value):
  return len(value.split())



@register.filter(name='cleanTag')
def cleanTag(value):
  return re.sub('<[^>]*>','', value)


@register.filter
def lower(value):
    return value.lower()
'''

@register.simple_tag
def ExplotItem(text):
  """
    ex:
      {% ExplotItem "Modulo Id Fecha" %}
  """
  listVal = text.split()
  rval = ''
  '''
    <div  class="row "> <div class="col-md-12 center-block"> Id  </div> </div>
  '''
  for it in listVal:
    rval += f'<div class="row"><div class="col-md-12 center-block">{it}</div></div>'
  return mark_safe(rval)


@register.filter(needs_autoescape=True)
def initial_letter_filter(text, autoescape=True):
    first, other = text[0], text[1:]
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    result = '<strong>%s</strong>%s' % (esc(first), esc(other))
    return mark_safe(result)

from datetime import datetime

@register.filter(name='str_time')
def str_time(value):
  """
    @fn def str_time(value):
    @brief funcion que retorna un string con fomrato de 
    time => Hh:Mm:Ss

    ex:
    {{it_th.tiempo|str_time}}
  """
  return f'{value}'

@register.filter(name='get_item')
def get_item(value,index):
  """
    @fn def def get_item(value,index):
    @brief funcion que retorna un item, util dentro de for loops "foreach"
    ex:
      {% for it in company_all %}
        ...
        {{ company_enum_items|get_item:forloop.counter0 }}
        ...
      {% endfor %}      
  """
  rval = None
  try:
    rval = value[index]
  except IndexError:
    debug_print(f'La variable "{value}" no puede ser indexable')
  except TypeError:
    debug_print(f'El tipo de la variable "{value}" no corresponde')
  return f'{rval}'  
