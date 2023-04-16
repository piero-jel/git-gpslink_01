# Docker/Dockerfile
Pasos para correr el proyecto desde docker
## 1. Nos movemos al directorio donde estan los Dockerfile
~~~ bash
  cd 0D-Dockerfiles/
~~~

## 2. Construimos la imagen, dentro del directorio actual:
~~~ bash
  docker build -t="jeluccioni/debian-django" -f DebianDJango .
~~~

## 3. Nos movemos al directorio donde esta el workspace, creamos y corremos el contenedor
~~~ bash
  cd ..
  docker run --name DebianDJango-gpslink -i -t -v $PWD/:/home/user:rw jeluccioni/debian-django /bin/bash
~~~

### 3.b En caso de necesitar un puerto diferente entre el host y el contendor (aplicacion)
~~~ bash
  docker run -p <HOST_PORT>:<CONTAINER_PORT> --name DebianDJango-gpslink -i -t -v $PWD/:/home/user:rw jeluccioni/debian-django /bin/bash
~~~

El puerto configurado para exponer por defecto es el puerto __8080__, podemos modificar la linea involucrada o utilizar esta opcion a la hora de crear el container.

## 4. Iniciamos el contenedor
En caso de terminar la seccion iniciada al crear el conedor, para iniciar esta nuevamene
~~~ bash
  docker start -i DebianDJango-gpslink
~~~

## 5. Start del proyecto
Para este paso contamos con varias opciones, para ambas siempre se muestra en pantalla la url para acceder a la pagina web principal.

### 5.a. Opcion uno, corremos directamente el script python de testing
~~~ bash
root@b60766109a23:/home/user# ./test.py 
~~~

### 5.b. Uso del script de servicios 
~~~ bash
root@b60766109a23:/home/user# bash servicio.sh --test
~~~

## 6. Stop del servicio
Para esto solo debemos presionar la combinación ```Ctrl``` + ```c```.
