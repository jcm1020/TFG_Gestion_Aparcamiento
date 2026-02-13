Requisitos no funcionales

- Rendimiento
    
    - Latencia de procesamiento objetivo: por debajo de 1–2 segundos por frame en flujos de video de resolución razonable; estable ante picos de carga.
        
    - Escalabilidad horizontal: permitir añadir cámaras/instancias de procesamiento sin mayor reconfiguración.
        
- Robustez
    
    - Tolerancia a iluminación variable y oclusiones parciales mediante técnicas de visión y/o fusión de datos.
        
    - Umbrales de confianza para evitar contabilidades erróneas y mecanismos de autocorrección.
        
- Privacidad
    
    - No almacenar imágenes completas de personas o con personas; procesar datos y/o en la nube con sistemas de detección anónimos.
        
    - No registrar matrículas; si se requieren, mantenerlas codificadas mediante 'hash' o solo para control de acceso, con consentimiento.
        
    - Acceso limitado a logs y métricas; auditorías y borrado periódico de datos sensibles.
        
- Seguridad
    
    - Autenticación y autorización en el sistema de presentación y gestión. Cifrados de contraseñas.
