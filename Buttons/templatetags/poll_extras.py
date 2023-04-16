## para ser valido el modulo debemos agragar la instancia, de lo contrario 
## tendremos un error 
from django import template
import re
register = template.Library()

'''
  ex:
  <small><a href="{{it.url}}" class="d-md-block"> {{it.label|find:" "}}</a></small>
'''
@register.filter(name='find')
def find(value, arg):
  count = 0
  for it in value:
    if(it == ' '):
      return count    
    count += 1
  return -1

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