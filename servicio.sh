#!/bin/bash
#=====================================================================================================
##
## Copyright 2015 - 2021, Luccioni Jesus Emanuel "J.E.L"
## All rights reserved.
#
#=====================================================================================================
#
#=====================================================================================================
### BEGIN setting GLOBAL VARs 
DEBUG_ENABLE=1
PATH_SETTING_FILE='./config/settings.py'
RETRY=0
USER_SERVER="root"

DDBB_DIR='backups'
DDBB_NAME='db_gpslink_02'
#DDBB_NAME='db_ticketsys'
POSTGRESQL_DIR='/var/lib/postgresql'
DEPLOY_FILE="/etc/nginx/sites-available/ticketsys"
KEY_PASS="154b3l"


IP=127.0.0.1
PORT=8080
## stdinp  0
## stdout  1
## stderr  2
CMD_APT=apt-get
CMD_PYTHON=python3
LOG=$PWD/install.log
LOG_ERR=$PWD/install_err.log
### END   setting GLOBAL VARs


function set_console_color()
{
    local color_name
    local prefix
    if [ "$#" -eq "0" ]; 
        then echo -ne "\e[0m"
        TERMINAL_COLOR=0
        return 1
    else
        color_name=$1
    fi    
    if [ "$#" -eq "2" ]; 
    then 
        case "$2" in
        text|Text|TEXT) prefix=3 ;;
        texto|Texto|TEXTO) prefix=3 ;;
        background|Background|BACKGROUND) prefix=4 ;;
        back|Back|BACK) prefix=4 ;;
        fondo|Fondo|FONDO) prefix=4 ;;
        *) prefix=3 ;; 
        esac
    else
        prefix=3 
    fi
    case "$color_name" in
        negro|Negro|NEGRO|BLACK) echo -ne "\e[1;${prefix}0m"; TERMINAL_COLOR=${prefix}0 ; return 0 ;;
        rojo|Rojo|ROJO|RED) echo -ne "\e[1;${prefix}1m" ;TERMINAL_COLOR=${prefix}1 ; return 0 ;;
        verde|Verde|VERDE|GREEN) echo -ne "\e[1;${prefix}2m" ; TERMINAL_COLOR=${prefix}2 ;return 0 ;;
        amarillo|Amarillo|AMARILLO|YELLOW) echo -ne "\e[1;${prefix}3m" ; TERMINAL_COLOR=${prefix}3 ; return 0 ;;
        azul|Azul|AZUL|BLUE) echo -ne "\e[1;${prefix}4m"; TERMINAL_COLOR=${prefix}4 ;return 0 ;;
        magenta|Magenta|MAGENTA) echo -ne "\e[1;${prefix}5m" ; TERMINAL_COLOR=${prefix}5 ; return 0 ;;
        cyan|Cyan|CYAN) echo -ne "\e[1;${prefix}6m" ;TERMINAL_COLOR=${prefix}6 ;return 0 ;;
        blanco|Blanco|BLANCO|WHITE) echo -ne "\e[1;${prefix}7m" ; TERMINAL_COLOR=${prefix}7 ;return 0 ;;
        reset|Reset|RESET) echo -ne "\e[0m" ; TERMINAL_COLOR=0 ; return 0 ;;
        *) echo -ne "\e[0m" ; TERMINAL_COLOR=0 ; return 1 ;;
    esac        
}

function printfontcolor() # mensaje color
{
    local msj
    local color
    local retValue
    if [ "$#" -eq "2" ]
    then
        msj=$1
        color=$2        
    elif [ "$#" -eq "1" ] && [ "${#1}" -ne "0" ]; then
        msj=$1
        echo -ne "$msj"
        return 2
    else
        return 3
    fi    
    set_console_color $color 
    retValue=$?
    echo -ne "$msj"
    set_console_color "reset"
    return $retValue  
}

## $@ arg for print
function pdebug()
{
  if [ "$DEBUG_ENABLE" -eq "0" ]; then
    return 0
  fi
  printfontcolor "$@\n" "BLUE"
  return 0  
}


confirmacion_DEFAULT_MENSSAGE="\tDesea Continuar (y/n): "
function confirmacion()
{
  local arg1 arg2
  case "$#" in
    "2")
        arg1=$1
        arg2=$2
        if [ "${#arg2}" -eq "0" ]
        then
            printfontcolor "$arg1" "BLUE";
        else
            printfontcolor "$arg1" "$arg2"                
        fi        
    ;;
    "1")
        printfontcolor "$1";
    ;;
    "0")
        printfontcolor "$confirmacion_DEFAULT_MENSSAGE"
    ;;
  esac       
  ##
  ##
  read -n1 ret
  echo ""
  case "$ret" in
  y|Y|s|S)
      return 0
  ;;
  n|N)
      return 1    
  ;;
  *)
      return 1
  ;;
  esac
}

function check_command()
{
  local command msgerr msginst 
  if [ "$#" -ne "3" ]; then return 1 ; fi
  command=$1
  msgerr=$2
  msginst=$3
  ## 
  if ! command -v $command &> /dev/null
  then
    printfontcolor "$msgerr" "RED"
    printfontcolor "$msginst" "YELLOW"
    return 1          
  fi
  if [ "$DEBUG_ENABLE" -eq "1" ] 
  then
    printfontcolor "Comando success : \"$command\"\n" "GREN"
  fi
  return 0
}

function net_list_port()
{
  check_command "lsof" "\t\"lsof\" no localizado en el sistema\n" ""
  if [ "$?" -eq "0" ]
  then
    printfontcolor "\tListando Ports 'lsof'\n" "BLUE"
    sudo lsof -i -P -n | grep LISTEN
    return 0
  fi
  
  check_command "ss" "\t\"ss\" no localizado en el sistema\n" ""
  if [ "$?" -eq "0" ]
  then
    printfontcolor "\tListando Ports 'ss'\n" "BLUE"
    sudo ss -tulwn | grep LISTEN
    return 0
  fi
  
  check_command "netstat" "\t\"netstat\" no localizado en el sistema\n" ""
  if [ "$?" -eq "0" ]
  then
    printfontcolor "\tListando Ports 'netstat'\n" "BLUE"
    sudo netstat -tulpn | grep LISTEN
    return 0
  fi
  printfontcolor "\tNo localizamos comando para lsitar ls puertos disponibles\n" "RED"
  
}



RESTORE_DDBB=""
function get_restore_ddbb()
{
  local listddbb i tmp zz
  declare -a array arrdate

  #listddbb=`sudo ls -l $POSTGRESQL_DIR/$DDBB_DIR/*.sql | cut -d " " -f 9`
  ## -t reciente al mas viejo (ultimo)
  listddbb=`su -l postgres -c "ls -t $POSTGRESQL_DIR/$DDBB_DIR/*.sql"`
  ## -tr del mas viejo al mas reciente (ultimo)
  #listddbb=`su -l postgres -c "ls -tr $POSTGRESQL_DIR/$DDBB_DIR/*.sql"`
  
  ##
  i=0  
  for line in $listddbb
  do
    # file="$(basename "${0}")"
    ## stat -c '%y' /var/lib/postgresql/backups/db_ticketsys20211116.sql | cut -d ' ' -f 1,2
    array[$i]=$(basename ${line})
    tmp=`stat -c '%y' ${line} | cut -d ' ' -f 1,2`
    arrdate[$i]=`echo "$tmp" | cut -d '.' -f 1`
    #arrdate[$i]=`stat -c '%y' ${line} | cut -d ' ' -f 1,2`}
    
    i=`expr $i \+ 1`
  done
  ##
  printfontcolor "\tLista de DDBB Salvadas:\n" "BLUE"    
  ##
  #printfontcolor "\tlistddbb $listddbb \n" "BLUE" 
  
  for (( x=0 ,y=1; x<${#array[@]} ; x++,y++ ))  
  do
    printfontcolor "\t $y - ${array[$x]} (${arrdate[$x]})\n" "YELLOW"    
  done
  
  #printfontcolor "\tArray ${array[@]} \n\t List Array : ${#array[@]}" "BLUE"
  #printfontcolor "\tSeleccione el nombre de DDBB SAVE: " "BLUE"
  printfontcolor "\n\tSeleccione Una (Ingrese Numero 1 ... ${#array[@]}) : " "BLUE"
  read readvalue
  if (( $readvalue < 1 || $readvalue > ${#array[@]} ))
  then
    printfontcolor "\t Opcion $readvalue incorrecta, no existe en la enumeracion.\n" "RED"
    return 1
  fi  
  
  readvalue=`expr $readvalue \- 1`
  RESTORE_DDBB=${array[$readvalue]}
  
  #printfontcolor "\t Opcion Correcta, RESTORE_DDBB: $RESTORE_DDBB \n" "GREEN"
  #     read -n3 UNIDAD
  #   read RESTORE_DDBB
  #printfontcolor "\n" "BLUE"
  return 0
}


function current_user_isroot()
{
  local user arg1 arg2
  if [ "$#" -eq '1' ] ; then arg1=$1 ; fi
  if [ "$#" -eq '2' ]
  then
    arg1=$1 
    arg2=$2 
  fi
  
  user=$(id -n -u)  
  if [ "$user" == "root" ] ; then return 0 ; fi    
  if [ "$#" -eq '0' ]
  then
    printfontcolor "\tEl Usuario Actual No es root, intente con 'sudo $0 cmd'\n" "RED"
    exit 0
  fi
  
  if [ "$#" -eq '1' ] 
  then
    ## tenemos solo un arg no es necesario la query
    if [ "$arg1" -eq '0' ] ; then return 1 ; fi
    
    exit 0
  fi
    
  if [ "$#" -eq '2' ] 
  then
    printfontcolor "$arg2" "RED"
    if [ "$arg1" -eq '0' ] ; then return 1 ; fi    
    if [ "$arg1" -eq '1' ] ; then exit 0 ; fi
    
    printfontcolor "\tArgumento 1 ($arg1) para 'current_user_isroot()' incorrecto\n" "RED"
    return 1
  fi
  
  printfontcolor "\tNro de Argumentos para 'current_user_isroot()' es incorrecto\n" "RED"
  return 1
}


function check_daemonfile()
{
  ## FIXME debe ejecutarse como SUDO
  ## Comprobamos si el archivo existe
  [ -f $DEPLOY_FILE ] ## 
  if [ "$?" -ne "0" ]
  then
    cp ./ticketsys /etc/nginx/sites-available/
  else
    return 0
  fi
  [ -f $DEPLOY_FILE ] ## 
  if [ "$?" -ne "0" ]
  then 
    return 1
  fi
  ln -s $DEPLOY_FILE /etc/nginx/sites-enabled
  
}



##
## $1 single target valor por defecto -h/--help
## $2 <$1> target
function msg_help()
{
  local app arg1
  app=${0##*/}
  if [ "$#" -eq "2" ];then
    arg1=$2
  else
    arg1="-h"
  fi

  arrHelp=( '--install' 
            '--test'
            '--migrate'
            '--mirgration-merge'            
          )

  case "$arg1" in
  --install)
    cat << EOH >&2
--install
  Instala los package python necesarios.
EOH
  return 0
  ;;

  --test)
    cat << EOH >&2
--test
  Ejecuta el test de la aplicacion web '$CMD_PYTHON manage.py runserver $IP:$PORT'.
EOH
  return 0
  ;;
  
  --migrate)
    cat << EOH >&2
--migrate
  Realiza la migracion de los modelos ORM (actualiza la Tablas, composicion) y de los archivos templates (images, templates html, etc).
EOH
  return 0
  ;;
  --mirgration-merge)
    cat << EOH >&2
--mirgration-merge
  Realiza el mergue de la migracion, antes de este intentar con '--migrate'.
EOH
  return 0
  ;;
  
  -a)
    cat << EOH >&2
--all <ID_DEBIN>              
  Obtiene la información actual del DEBIN, para todas las version disponibles actualmete ('$URL_EPCOELSA_DEBIN/Debin/DebinX/{id_debin}').
EOH
  return 0
  ;; 
  --help|-h)
  cat << EOH >&2
  $app {--help | -h }        Visualiza Help General
  $app {--help | -h } --all  Visualiza Help Especifico para todos los Targets

  Para Visualizar Help Especifico Intente con:
EOH
  for it in ${arrHelp[@]}
  do
    cat << EOH >&2
    $app {--help | -h} $it
EOH
  done

  return 0
  ;;

  --all)
    msg_help "-h"
    echo
    for it in ${arrHelp[@]}
    do
      #echo "msg_help -h $it"
      msg_help "-h" "$it"
      echo
    done
    return 0
  ;;
  *)
cat << EOH >&2
    -h                             : llamado a help con parametro <$arg1> incorrecto (no documentado).
EOH
    msg_help "-h" "-all"    
    return 0
  ;;  
  esac
}


function main()
{
   
  case "$1" in
    start|START|Start)
      check_daemonfile
      printfontcolor "\tIniciando los servicio\n" "GREEN"
      sudo systemctl start gunicorn.socket && sudo systemctl start gunicorn.service && sudo systemctl start nginx
      return 0
    ;;
    stop|STOP|Stop)
      printfontcolor "\tDeteniendo los Servicio\n" "GREEN"
      sudo systemctl stop gunicorn.socket && sudo systemctl stop gunicorn.service && sudo systemctl stop nginx
      return 0
    ;;
    status|Status|STATUS)
      sudo systemctl status gunicorn.socket && sudo systemctl status gunicorn.service && sudo systemctl status nginx
      return 0
    ;;
    log|Log|LOG)
      tail -f ./log/app.log
      return 0
    ;;
    log_clean|LogClean)
      echo "" > ./log/app.log
      return 0
    ;;
    access|Access)
      tail -f /var/log/nginx/access.log
      return 0
    ;;
    config|Config|CONFIG)
      vi ${PATH_SETTING_FILE}
      return 0
    ;;
    error|Error|ERROR)
      tail -f /var/log/nginx/error.log
      return 0
    ;;
    clean)
      git reset .
      git reset --hard  HEAD~1
      return 0
    ;;
    update)
      main "stop"
      main "status"
      main "log_clean"
      main "clean"
      git pull
      main "start"
      main "status"
      main "stop"
      return 0
    ;;
    
    test)
      local port user type ips default 
      user=$(id -n -u) 
      ips=$(ip -o addr show up primary scope global | while read -r num dev fam addr rest; do echo ${addr%/*}; done)
      
      case $user in
       "jesus"|"jel")
          type=0
       ;;
       "user")
          type=0
       ;;
       $USER_SERVER)
        type=1        
       ;;       
       *)
        printfontcolor "\t Current user [$user] is not in target list try with sudo $0 test.\n" "RED"
        return 0        
       ;;
      esac
      
      printfontcolor "\tSeleccionando el puerto:\n" "BLUE"
      printfontcolor "\t\t 1 - Usar el Puerto 80 (Solo si 'sudo $0 test')\n" "CYAN"
      printfontcolor "\t\t 2 - Usar el Puerto 8080\n" "CYAN"
      printfontcolor "\t\t 3 - Usar el Puerto 8000\n" "CYAN"
      printfontcolor "\t\t 4 - Default test production disable in the Port 8080\n" "CYAN"
      printfontcolor "\t\t 5 - Default test production disable in the Port 8000\n" "CYAN"
      printfontcolor "\t\t " "GREEN"
      read opt
      case $opt in
       1)
        port=80        
        default=0
       ;;
       2)
        port=8080        
        default=0
       ;;
       3)
        port=8000
        default=0
       ;;     
       4)
        port=8080
        default=1
       ;;
       5)
        port=8000
        default=1
       ;;
       *)
        printfontcolor "\tOpcion [$opt] incorrecta \n" "RED"
        return 0        
       ;;
      esac
      
      if [ "$type" -eq '1' ] ; then main "stop" ; fi 
      
      
      if [ "$type" -eq '0' ] ; then printfontcolor "\tGlobal: http://$ips:$port/\n" "CYAN" ; fi
      
      source ../bin/activate      
      if [ "$default" -eq '0' ]
      then 
        python manage.py runserver 0.0.0.0:$port --insecure
      else
        python manage.py runserver 0.0.0.0:$port        
      fi      
      deactivate
      return 0
    ;;
    port)
      local opt port
      printfontcolor "\tSeleccione la opcion:\n" "BLUE"
      printfontcolor "\t\t 1 - Listar los puertos habilitados\n" "CYAN"
      printfontcolor "\t\t 2 - Mostrar el log/dump de un Puerto\n" "CYAN"      
      printfontcolor "\t\t " "GREEN"
      read opt
      case $opt in
       1)
        main "port_list"
        return 0
        
       ;;
       2)
        main "port_log"
        return 0
        
       ;;
       
       *)
        printfontcolor "\tOpcion [$opt] incorrecta \n" "RED"
        return 0        
       ;;
      esac
    ;;    
    port_list)      
      net_list_port
      return 0
    ;;
    port_log)
      local opt port
      printfontcolor "\tSeleccione el Puerto:\n" "BLUE"
      printfontcolor "\t\t 1 - puerto 80\n" "CYAN"
      printfontcolor "\t\t 2 - puerto 443\n" "CYAN"      
      printfontcolor "\t\t " "GREEN"
      read opt
      case $opt in
       1)
        port=80
        
       ;;
       2)
        port=443
        
       ;;
       
       *)
        printfontcolor "\tOpcion [$opt] incorrecta \n" "RED"
        return 0        
       ;;
      esac
      printfontcolor "\t run command in port: $port\n" "BLUE"
      printfontcolor "\t presiones Ctrl+c o Ctrl+z para salir del log\n" "BLUE"
      sudo -S tcpdump port $port
      return 0
    ;;
    --test)
      $CMD_PYTHON test.py
      return 0
    ;;    
    --migrate)
      local target
      if [ "$#" -ge 2 ]; then
        target=$2
      else
        target='default'
      fi
      ## add target -a|--all , -m|--make, -c|--collect, default value only migrate
      case "$target" in
        default)
          $CMD_PYTHON manage.py migrate
        ;;
        -c|--collect)
          $CMD_PYTHON manage.py collectstatic
        ;;
        -m|--make)
          $CMD_PYTHON manage.py makemigrations
        ;;
        -a|--all)
          $CMD_PYTHON manage.py makemigrations
          $CMD_PYTHON manage.py migrate
          $CMD_PYTHON manage.py collectstatic
        ;;
      esac
      return 0
    ;;
    --mirgration-merge)
      $CMD_PYTHON manage.py makemigrations --merge
      return 0
    ;;
    --start-ddbb)
      local status key
      if [ "$#" -ge "2" ];then
        key=$2
        su -l postgres -c "echo \"ALTER USER postgres PASSWORD '$key';\" | psql"
      fi

      status=$(service postgresql status)
      if [ "$?" -ne "0" ];then
        pdebug "services 'postgresql' not run, starting"
        service postgresql start
      else
        pdebug "services 'postgresql' running '$status'"
      fi

      ddbb_name='db_ticketsys'
      su -l postgres -c "echo \"create database $ddbb_name ;\" | psql"


      #su - postgres && psql -c "ALTER USER postgres PASSWORD '1234';"
      #su - postgres psql -c "ALTER USER postgres PASSWORD '1234';"
      #su -l postgres psql -c "ALTER USER postgres PASSWORD '1234';"
      #su -l postgres -c "echo \"ALTER USER postgres PASSWORD '1234';\" | psql"

      return 0
    ;;
    -h|--help)
      msg_help $@
      return 0
    ;;    
    *)
      printfontcolor "\tError en el llamado \"$0 $@\"\n" "RED"
      main "help"
      return 0
    ;;
  esac
    return 0
}

main "$@" && exit 0
