# python/pipenv
Pasos para correr el proyecto, en caso de necesitar instalar python considere [estos pasos](#python-install).

~~~ bash
  ## 1. Habilitamos el ambiente
  pipenv --python /usr/bin/python3 shell

  ## 1.b En caso de ser la primera ejecucion  ejecutamos
  ##     la instalacion de los packages del proyecto
  pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r 0D-Dockerfiles/requerimientos.txt

  ## 2. ejecutamos el proyecto
  ### Opcion uno
  python test.py

  ### Opcion dos
  ./test.py
~~~

Para detener el mismo solo debemos precionar la combinación ```Ctrl``` + ```c```.

En caso de necesitar finalizar __pipenv__ debemos usar la combinación ```Ctrl``` + ```d```, o ingresar el comando __exit__.

***En caso de falla debemos ejecutar algunos de los pasos siguentes.***

# python install
~~~ bash
  sudo apt-get update && sudo apt-get upgrade -y
  sudo apt-get install -y python3
  sudo apt-get install -y python3-pip
~~~ 

# Instalando pipenv
~~~ bash
 python3 -m pip install pipenv
~~~

# Enable virtual enviroment
Habilitando el Entorno Virtual:

**Linux :**

~~~ bash
  pipenv shell
~~~

# Disable virtual enviroment

~~~ bash
  exit
  ## o (Presionar la convinacion de teclas) Ctrl + D
  # Ctrl + d

~~~

# Project Test:
 1. Enable virtual enviroment
 2. Run/Ejecuion del script **test.py** :

  - opcon 1:
  
  ~~~ bash
    $ python test.py 
  ~~~
  
  - Opcion 2
  ~~~ bash
    $ ./test.py
  ~~~

O directamente podemos correr el script de django, considerando un puerto valido por ejemplo 8080 u 8000:

~~~ bash
  $ python manage.py runserver 0.0.0.0:{port} 
~~~

# Install package from requeriments
Para esto necesitamos tener el archivo pipfile, quien contine los package necesarios para poder desplegar el proyecto.

**pipenv**

~~~ bash
  $ pipenv install -r /path/requerimientos.txt  
~~~

**pip**

~~~ bash
  $ pip install -r /path/requerimientos.txt  
~~~

# Creting requeriments file for pipfile or pip
Antes de crear el archivo **pipfile**, debemos instalar dentro del entonrno virtual los package mediante el comando **pipenv install \<package\>** o **pip install**

Esto lo podemos realizar de dos formas diferentes, desde un entorno aislado ya sea con **pipenv** u otro disponible (virtualenv).

**pipenv**

~~~ bash
  $ pipenv lock -r > requeriments.txt
~~~

**pip**

~~~ bash
  $ pip freeze > requeriments.txt
~~~


# views current package
Visualizando los package instalados actualmente.

**usando pip**

~~~ bash
  $ pip freeze
~~~

**usando pipenv**

~~~ bash
  $ pipenv lock -r 
~~~
