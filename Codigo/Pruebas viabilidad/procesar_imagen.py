import cv2
import sqlite3
import os
from ultralytics import YOLO

# Configurar la base de datos
conn = sqlite3.connect("parking.db")
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS aparcamientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        x1 REAL,
        y1 REAL,
        x2 REAL,
        y2 REAL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

# Cargar el modelo de YOLOv8 o YOLOv8
#model = YOLO("yolov8n.pt")
model = YOLO("yolo11x.pt")

# Obtener la lista de todas las imágenes en el directorio actual
image_directory = "./Camara"  # Cambiar el nombre del directorio de imágenes
images = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.webp')]

if len(images) == 0:
    print("¡Advertencia! No se encontraron imágenes en el directorio: "+image_directory)
else:
    print(f"Procesando {len(images)} imágenes en el directorio.")

for index, image_name in enumerate(images):
    print(f"Procesando imagen: {image_name}")

    # Construir la ruta completa de la imagen
    image_path = os.path.join(image_directory, image_name)

    # Cargar la imagen
    try:
        original_image = cv2.imread(image_path)
    except Exception as e:
        print(f"Error al cargar la imagen {image_name}: {str(e)}")
        continue

    if original_image is None:
        print(f"La imagen {image_name} no pudo ser leída correctamente.")
        continue

    output_image = original_image.copy()

    # Detectar objetos o vehículos en la imagen
    results = model(original_image)

    for result in results:
        imagen_procesada = result.plot()

        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()  # Obtener coordenadas del bounding box

            # Imprimir coordenadas en consola
            print(f'x1: {x1} y1: {y1} x2: {x2} y2: {y2}')

            try:
                # Insertar en la base de datos
                cursor.execute('''
                    INSERT INTO aparcamientos (x1, y1, x2, y2)
                    VALUES (?, ?, ?, ?)
                ''', (x1, y1, x2, y2))

                # Dibujar el bounding box en la imagen con color rojo
                cv2.rectangle(output_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)

                # Obtener el label del vehículo detectado
                class_id = box.cls[0]
                label = model.names[int(class_id)]

                # Dibujar el label junto al bounding box
                cv2.putText(output_image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            except sqlite3.Error as e:
                print(f"Error al insertar en la base de datos: {str(e)}")

    # Guardar la imagen procesada
    path_imagenes_procesadas = os.path.join("imagenes_procesadas", f'processed_{image_name}')
    cv2.imwrite(path_imagenes_procesadas, imagen_procesada)

    print(f"Imagen guardada como {path_imagenes_procesadas}")

    # Mostrar las imágenes en ventanas separadas para cada imagen
    #cv2.imshow(f"Imagen Original - Imagen {index + 1}", original_image)
    cv2.imshow(f"Imagen Procesada - Imagen {index + 1}", output_image)

    # Esperar a que el usuario presione una tecla para cerrar las ventanas
    cv2.waitKey(0)
    cv2.destroyAllWindows()

conn.commit()

# Cerrar la conexión con la base de datos
conn.close()