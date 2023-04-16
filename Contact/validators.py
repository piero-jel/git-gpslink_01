from django.core.exceptions import ValidationError

# SIZE_MAX_FILE = 10485760
SIZE_MAX_FILE = 1048576

# SIZE_MAX_FILE = 10485760


def GetStrSize(value):
  return '1[MB]'

def FileSize(value):
  filesize= value.size  
  if filesize > SIZE_MAX_FILE:
      raise ValidationError(f"El tamaño Maximo para el Archivo no puede Superar {GetStrSize(SIZE_MAX_FILE)}")
  else:
      return value