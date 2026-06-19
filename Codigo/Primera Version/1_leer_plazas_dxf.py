import ezdxf
from shapely.geometry import Polygon, Point
import json
import sys
import os

VERBOSE = 1 # Nivel de detalle en la salida por consola (1 = detallado, 0 = resumido)

"""
Script independiente para leer y procesar archivos DXF de planos de aparcamiento.

Lee un archivo DXF, extrae los polígonos cerrados (LWPOLYLINE con flag 1)
agrupados por capa (Plazas, Calzadas, Aceras, etc.), asocia los textos
(TEXT/MTEXT) a los polígonos según su posición geográfica, calcula centroides
y genera un archivo JSON con la información estructurada.

Uso: python 1_leer_plazas_dxf.py <ruta_archivo_dxf>
"""

def punto_en_poligono(punto, poligono, umbral=0.1):
    """Comprueba que punto esta dentro de poligono. Usa buffer para manejar la precision adecuada."""
    punto_shapely = Point(punto)
    poligono_shapely = Polygon(poligono)
    
    # Primero verificar si esta dentro
    if punto_shapely.within(poligono_shapely):
        return True
    
    # Si no esta dentro, verificar si esta muy cerca del borde (precision)
    poligono_buffer = poligono_shapely.buffer(umbral)
    if punto_shapely.within(poligono_buffer):
        return True
    
    return False

def obtener_vertices(poly):
    """
    Extrae los vértices de una entidad LWPOLYLINE del DXF.

    Args:
        poly: Entidad LWPOLYLINE de ezdxf.

    Returns:
        Lista de tuplas (x, y) con las coordenadas de cada vértice.
        Solo extrae las dos primeras componentes (x, y), ignora z y otros datos.
    """
    vertices = []
    if poly.dxftype() == 'LWPOLYLINE':
        for punto in poly.get_points():
            if len(punto) >= 2:
                vertices.append((punto[0], punto[1]))
    return vertices

def obtener_centro_poligono(vertices):
    """
    Calcula el centroide de un polígono como media aritmética de sus vértices.

    No es un centroide geométrico exacto, sino una aproximación rápida
    útil para localizar la posición media del polígono.

    Args:
        vertices: Lista de tuplas (x, y).

    Returns:
        Tupla (cx, cy) con las coordenadas del centro, o None si hay menos de 3 vértices.
    """
    if len(vertices) < 3:
        return None
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    return (cx, cy)

def procesar_dxf(archivo):
    """
    Procesa un archivo DXF y extrae sus polígonos cerrados con textos asociados.

    Lee el DXF, itera las entidades del modelspace y recoge todas las
    LWPOLYLINE cerradas (flags & 1), agrupándolas por capa. Luego asocia
    los elementos TEXT y MTEXT a cada polígono si su punto de inserción
    cae dentro del polígono.

    Args:
        archivo: Ruta al archivo DXF.

    Returns:
        Diccionario {nombre_capa: [{poligono, vertices, texto}, ...]}
    """
    if not os.path.exists(archivo):
        print(f"Error: No se encuentra el archivo {archivo}")
        return {}
    
    doc = ezdxf.readfile(archivo)
    msp = doc.modelspace()
    
    entidades = {}
    
    #Primer bucle pasada: recoger todos los polígonos cerrados 
    #(flag bit 1) agrupados por capa
    for entidad in msp:
        if entidad.dxftype() == 'LWPOLYLINE' and (entidad.dxf.flags & 1):
            capa = entidad.dxf.layer
            vertices = obtener_vertices(entidad)
            if len(vertices) >= 3:
                if capa not in entidades:
                    entidades[capa] = []
                entidades[capa].append({'poligono': entidad, 'vertices': vertices, 'texto': []})
    #Segund bucle: asociar textos a polígonos según su posición            
    for capa in entidades:
        for area in entidades[capa]:
            for entidad in msp:
                if entidad.dxftype() in ('TEXT', 'MTEXT'):
                    try:
                        punto = (entidad.dxf.insert[0], entidad.dxf.insert[1])
                        if punto_en_poligono(punto, area['vertices']):
                            area['texto'].append(str(entidad.dxf.text))
                    except:
                        pass
    
    return entidades

def guardar_plazas_json(entidades, archivo_salida):
    """
    Guarda las entidades procesadas en un archivo JSON estructurado.

    Para cada polígono extrae: número identificador, vértices, centroide
    y capa de origen. En la capa 'Plazas', el número se obtiene del valor
    entero mínimo encontrado entre los textos asociados. Para el resto de
    capas se usa el primer texto disponible.

    Args:
        entidades: Diccionario de entidades procesadas.
        archivo_salida: Ruta donde guardar el JSON.

    Returns:
        Lista de plazas/zonas generadas.
    """
    plazas = []
    
    for capa, poligonos in entidades.items():
        for i, pol in enumerate(poligonos):
            numero = "Sin numero"
            textos = pol['texto']
            
            if textos:
                if capa == 'Plazas':
                    #Extraer todos los enteros de los textos y 
                    #usar el mínimo como identificador de plaza
                    numeros_encontrados = []
                    for texto in textos:
                        try:
                            numeros_encontrados.append(int(texto))
                        except:
                            pass
                    if numeros_encontrados:
                        numero = str(min(numeros_encontrados))
                else:
                    # Para otras capas (Calzadas, Aceras, etc.), usar el primer texto directamente
                    numero = textos[0].strip()
            
            vertices = pol['vertices']
            centro = obtener_centro_poligono(vertices)
            plazas.append({
                'numero': numero,
                'vertices': vertices,
                'cx': centro[0] if centro else None,
                'cy': centro[1] if centro else None,
                'capa': capa
            })
    
    with open(archivo_salida, 'w') as f:
        json.dump({'plazas': plazas}, f, indent=2)
    
    print(f"Plazas guardadas en: {archivo_salida}")
    print(f"Total plazas: {len(plazas)}")
    return plazas

def mostrar_resultados(entidades):
    """
    Muestra por consola los resultados del procesamiento del DXF.

    El nivel de detalle depende de la variable global VERBOSE:
    - 1: muestra vértices incluidos
    - 0: solo muestra tipo y textos asociados

    Args:
        entidades: Diccionario de entidades procesadas.
    """
    for capa, poligonos in entidades.items():
        print(f"\n=== TIPO DE AREA: {capa} ===")
        for pol in poligonos:
            tipo = pol['poligono'].dxftype()
            textos = pol['texto']
            vertices = pol['vertices']
            if VERBOSE==1:
                print(f"  Poligono detectado - Tipo: {tipo} | Vertices: {vertices} | Encontrado Texto: {textos}")
            else:
                print(f"  Poligono detectado - Tipo: {tipo} | Encontrado Texto: {textos}")
        print(f"Total poligonos: {len(poligonos)}")

if __name__ == "__main__":
    # Usar el argumento passado (ruta completa del archivo DXF)
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    else:
        print("Usage: python 1_leer_plazas_dxf.py <ruta_archivo_dxf>")
        sys.exit(1)
    
    archivo_salida = "auxiliar/1_plazas_dxf.json"
    
    print(f"Procesando archivo: {archivo}")
    entidades = procesar_dxf(archivo)
    mostrar_resultados(entidades)
    guardar_plazas_json(entidades, archivo_salida)
