import os
import ezdxf
from django.db import models
from django.db.models import Model
from zonas.models import Zona


def obtener_capas(archivo_dxf):
    """Obtiene las capas únicas de un archivo DXF."""
    if not archivo_dxf or not os.path.exists(archivo_dxf):
        return []
    
    try:
        doc = ezdxf.readfile(archivo_dxf)
        msp = doc.modelspace()
        
        capas = set()
        for entidad in msp:
            if entidad.dxftype() == 'LWPOLYLINE' and (entidad.dxf.flags & 1):
                capa = entidad.dxf.layer
                capas.add(capa)
        
        return list(capas)
    except:
        return []


def aplicar_reglas_zonas(operador, valor, accion):
    """Aplica regla de activación a zonas según tipo."""
    
    zonas = Zona.objects.all()
    
    for zona in zonas:
        if operador == '==':
            if zona.tipo == valor:
                if accion == 'activar':
                    zona.activo = True
                else:
                    zona.activo = False
        elif operador == '!=':
            if zona.tipo != valor:
                if accion == 'activar':
                    zona.activo = True
                else:
                    zona.activo = False
        
        zona.save()
