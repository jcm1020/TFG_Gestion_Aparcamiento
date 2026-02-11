Arquitectura de alto nivel

- Capas o grandes bloques del sistema
    - Preparación, inicialización del sistema:
        
        - Gestión de Usuarios.
            
        - Creación por parte del administrador del sistema de gestión de un aparcamiento, zonas de aparcamientos, plazas y disposiciones.
            
        - Creación de cámara en el sistema. Gestión para cámaras.
            
        - &nbsp;Creación por parte del administrador o del operador, del sistema de gestión de mapeo de plazas con respecto a las imágenes de las cámaras.
            
    - Inicio del sistema:
        
        - Adquisición de imágenes: captura de frames de video o imágenes de cámaras IP.
            
        - Preprocesamiento de imágenes: preprocesamiento de imagen digital, normalización de iluminación y otros, filtrados de privacidad.
            
        - Procesamiento de imágenes: reconocimiento de vehículos y plazas sin vehículos, asignación de cada vehículo a una plaza específica mediante el sistema de mapeo de plazas.
            
        - Correlacionar cámaras y gestión de errores: fusionar datos cuando se superponen zonas y manejo de errores para evitar duplicados o perdidas.
            
        - Estadísticas y telemetría de rendimiento. Actualización del sistema de control de la aplicación, panel web y/o app móvil del administrador.
            
    - Salida:
        
        - Presentación: panel web y/o app móvil para visualización en tiempo real y alertas, navegación. API REST para frontend.
