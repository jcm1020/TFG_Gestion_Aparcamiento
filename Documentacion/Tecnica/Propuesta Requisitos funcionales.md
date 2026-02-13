# 1\. Introducción.

### 1.1 Propósito

Creación para un aparcamiento limitado de un sistema de detección y contabilidad de plazas de aparcamiento ocupadas y libres, a partir de imágenes de una o varias cámaras, mostrando el resultado en un panel web y/o app móvil, respetando restricciones de privacidad.

### 1.2 Alcance

El sistema cubrirá:

- Captura de imágenes/vídeo de una o varias cámaras en un aparcamiento.
    
- Detección en tiempo (casi) real de plazas ocupadas y libres.
    
- Visualización del estado y localización de las plazas en una interfaz web y/o móvil.
    
- Gestión de múltiples cámaras.
    
- Respeto de la privacidad (no identificación de personas ni matrículas).
    

# 2\. Actores

- **Administrador del sistema**  
    Crea la configuración del aparcamiento, zonas de aparcamiento, configura cámaras, define plazas, gestiona usuarios, consulta estadísticas globales. Inicia el sistema.
    
- **Operador del aparcamiento**  
    Consulta el estado en tiempo real, recibe alertas, revisa incidencias. Opcional configuración de cámaras o mapeo.
    
- **Usuario final del aparcamiento** (vía app/web público)  
    Consulta plazas libres, ubicación de zonas y ocupación general.
    

# 3\. Requisitos funcionales

### 3.1 Gestión del aparcamiento, zonas y cámaras

**RF-01 – Gestión del aparcamiento y zonas dentro del aparcamiento**  
El sistema permitirá definir un solo aparcamiento general y definir “zonas” (p. ej., Exterior-1, Minusválidos, VIP) y asociar cada cámara y cada plaza a una zona.

**RF-02 – Alta de cámaras**  
El sistema permitirá al Administrador registrar nuevas cámaras indicando al menos: identificador, URL de acceso o fuente de imágenes, zona del aparcamiento a la que pertenecen, resolución y parámetros básicos (formato).

**RF-03 – Edición y baja de cámaras**  
El sistema permitirá modificar la configuración de una cámara existente y desactivar o eliminar cámaras que dejen de utilizarse, manteniendo el histórico asociado.

**RF-04 – Estado de cámaras**  
El sistema mostrará el estado de cada cámara (operativa, sin señal, en mantenimiento) para que el Operador pueda detectar fallos de captura.

* * *

## 3.2 Modelado de plazas de aparcamiento

**RF-05 – Definición de plazas**  
El sistema permitirá al Administrador definir las plazas de aparcamiento sobre el plano o sobre una imagen de referencia (por cámara), indicando un identificador único por plaza y su geometría (p. ej., polígono o rectángulo).

**RF-06 – Asociación plaza–cámara**  
El sistema permitirá asociar cada plaza a una o varias cámaras que la “ven”, para habilitar la fusión de información en caso de múltiples ángulos.

**RF-07 – Metadatos de plazas**  
El sistema permitirá registrar información adicional por plaza (reservada, general; zona; comentarios).

* * *

## 3.3 Captura y procesamiento de imágenes

**RF-08 – Captura continua de vídeo/imágenes**  
El sistema capturará de forma continua imágenes o frames de vídeo desde cada cámara registrada, dentro de un intervalo de tiempo configurable (por ejemplo, cada n milisegundos).

**RF-09 – Preprocesamiento de imágenes**  
El sistema aplicará un preprocesamiento sobre cada frame o imagen (p. ej., normalización de iluminación, redimensionado) para mejorar la detección bajo condiciones reales (cambios de luz, reflejos, sombras, condicionantes atmosféricos).

**RF-10 – Procesamiento de imágenes para detección de ocupación por plaza**  
El sistema analizará cada frame y clasificará, para cada plaza definida y visible, su estado como “ocupada” o “libre”, con un nivel de confianza asociado.

**RF-11 – Fusión de información entre cámaras**  
Cuando una plaza sea visible por varias cámaras, el sistema combinará los resultados de detección para obtener un estado único por plaza, utilizando reglas de decisión (p. ej., consenso o confianza mayor).

**RF-12 – Recuperación ante errores**  
El sistema aplicará reglas para evitar duplicados o perdidas  de datos y plazas asignadas teniendo en cuenta oclusiones temporales o errores puntuales.

* * *

## 3.4 Gestión del estado de ocupación

**RF-13 – Cálculo del estado actual por plaza**  
El sistema mantendrá para cada plaza su estado actual (ocupada/libre/desconocida) y la hora del último cambio de estado.

**RF-14 – Contabilidad global y por zona**  
El sistema calculará, en tiempo real, el número total de plazas ocupadas y libres, así como la contabilidad por zona.

**RF-15 – Duración de ocupación**  
El sistema registrará el tiempo de ocupación de cada plaza, desde el momento en que pasa a estado “ocupada” hasta que vuelve a “libre”.

**RF-16 – Manejo de estado desconocido**  
El sistema marcará una plaza como “desconocida” cuando el nivel de confianza de la detección sea insuficiente o cuando las cámaras que la cubren no estén operativas, diferenciando este caso de “libre” y “ocupada”.

* * *

## 3.5 Interfaz web y app móvil

**RF-17 – Visualización del mapa/plano del aparcamiento**  
El sistema mostrará en la interfaz un plano o mapa del aparcamiento donde cada plaza aparecerá representada con un icono/forma y un color según su estado (ocupada, libre, desconocida).

**RF-18 – Información detallada de plaza**  
Al seleccionar una plaza en el plano, el sistema mostrará sus detalles: identificador, zona, tipo de plaza, estado actual, tiempo de ocupación o tiempo desde que está libre.

**RF-19 – Vista de resumen**  
El sistema ofrecerá una vista resumen con: total de plazas, número de plazas libres/ocupadas/desconocidas, y desglose por zona.

**RF-20 – Navegación**  
El sistema permitirá abrir un sistema de navegación externo con los datos de la aplicación, para guiar a un usuario a una plaza.

**RF-21 – Actualización en tiempo casi real**  
La interfaz web y la app móvil actualizarán periódicamente (p. ej., cada pocos segundos) el estado de las plazas sin necesidad de recargar manualmente.

**RF-22 – Adaptación a distintos perfiles**  
Según el tipo de usuario (Administrador, Operador, Usuario final), la interfaz mostrará opciones y niveles de detalle distintos (por ejemplo, el usuario final verá solo plazas libres y su localización aproximada).

* * *

## 3.6 Gestión de usuarios y seguridad de acceso

**RF-23 – Autenticación de usuarios internos**  
El sistema permitirá que Administradores y Operadores accedan al panel mediante un mecanismo de autenticación (usuario/contraseña o similar).

**RF-24 – Roles y permisos**  
El sistema gestionará roles (Administrador, Operador, Usuario final), definiendo qué acciones puede realizar cada tipo de usuario (configurar cámaras, consultar algunos datos, acceder a estadísticas, etc.).

**RF-25 – Registro de actividad**  
El sistema registrará acciones relevantes (altas/bajas de cámaras, cambios de configuración, acceso a vistas de administración) para auditoría básica.

* * *

## 3.7 Alertas y notificaciones (opcional/escalable)

**RF-26 – Alertas de ocupación alta**  
El sistema podrá generar una alerta cuando el porcentaje de ocupación global o por zona supere un umbral configurable.

**RF-27 – Alertas de fallo de cámara**  
El sistema notificará al Administrador/Operador cuando una cámara deje de enviar señal o presente errores reiterados de procesamiento.

**RF-28 – Integración con notificaciones externas**  
El sistema podrá exponer eventos de alerta mediante API o integrarse con sistemas de mensajería (correo electrónico) para avisar a operadores.

* * *

## 3.8 Privacidad y protección de datos (a nivel funcional)

**RF-29 – No visualización de datos personales identificables**  
La interfaz de usuario no mostrará información que permita identificar personas ni matrículas de vehículos; cualquier imagen mostrada será, en la medida de lo posible, anonimizada (p. ej., difuminando áreas sensibles).

**RF-30 – Procesamiento centrado en plazas, no en personas**  
La lógica de detección estará orientada a determinar la ocupación de plazas (presencia/ausencia de vehículo en el área de la plaza), sin extraer ni almacenar características biométricas ni identificadores personales.

**RF-31 – Configuración de retención de datos**  
El sistema permitirá configurar el periodo de retención de imágenes (si se almacenan para diagnóstico o auditoría) y del histórico de estados de plazas, con posibilidad de eliminación automática tras ese periodo.

**RF-32 – Control de acceso a imágenes**  
El sistema limitará el acceso a cualquier imagen almacenada a usuarios con rol autorizado (p. ej., Administrador), y no ofrecerá acceso a imágenes brutas al usuario final.

* * *

## 3.9 APIs

**RF-33 – API para consulta de estado de plazas**  
El sistema ofrecerá un servicio (API) para consultar el estado de plazas, incluyendo filtros por zona y tipo de plaza, para su consumo por otros sistemas o aplicaciones.

**RF-34 – API para estadísticas**  
El sistema proporcionará archivos o datos para recuperar estadísticas acumuladas (ocupación histórica, medias por franja horaria, etc.), dentro de las políticas de retención definidas.

* * *

## 4\. Requisitos de datos

- **RD-01**:
    
- **RD-02**:
    
- **RD-03**:
