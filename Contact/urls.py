from django.urls import path

from Contact import views

# ## para registrar las url de los archivos de services
# from django.conf import settings
# from django.conf.urls.static import static


##  http://127.0.0.1:8000/contact/
##  http://127.0.0.1:8000/contact/empresa/
##  http://127.0.0.1:8000/contact/empresa_trabaja_en_hoffsel/
##  http://127.0.0.1:8000/contact/empresa_alianzas_socios/

##  http://127.0.0.1:8000/contact/productos/
##  http://127.0.0.1:8000/contact/productos_gps_link/
##  http://127.0.0.1:8000/contact/productos_virtual_c/
##  http://127.0.0.1:8000/contact/servicios/
##  http://127.0.0.1:8000/contact/servicios_portal_operativo/
##  http://127.0.0.1:8000/contact/servicios_gestion_transporte/
##
urlpatterns = [    
    path('',views.SendComment,name="SendComment")
    ## Empresa
   ,path('empresa/',views.ViewsEmpresa,name="ViewsEmpresa")
   ,path('empresa_trabaja_en_hoffsel/',views.ViewsEmpresaTrabajaEnHoffsel,name="ViewsEmpresaTrabajaEnHoffsel")
   ,path('empresa_alianzas_socios/',views.ViewsEmpresaAlianzasSociosEmpresa,name="ViewsEmpresaAlianzasSociosEmpresa")

    ## productos
   ,path('productos/',views.ViewsProductos,name="ViewsProductos") 
   ,path('productos_gps_link/',views.ViewsProductosGPSlink,name="ViewsProductosGPSlink")
   ,path('productos_virtual_c/',views.ViewsProductosVirtualC,name="ViewsProductosVirtualC")
   
    ## servicios
   ,path('servicios/',views.ViewsServicios,name="ViewsServicios")
   ,path('servicios_portal_operativo/',views.ViewsServiciosPortalOperativo,name="ViewsServiciosPortalOperativo")
   ,path('servicios_gestion_transporte/',views.ViewsServiciosGestionTransporte,name="ViewsServiciosGestionTransporte")
  ,

]
