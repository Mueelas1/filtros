import cv2
import os
import numpy as np

def usar_filtros():
    # Cargar el clasificador de caras preentrenado usando el archivo XML
    clasificador = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')

    # Definir la carpeta que contiene los filtros
    carpeta_filtros = 'filtros'
    
    # Obtener la lista de nombres de los filtros en la carpeta, eliminando la extensión ".png"
    filtros_disponibles = [f[:-4] for f in os.listdir(carpeta_filtros) if f.endswith('.png')]
    if not filtros_disponibles:
        print("No se encontraron filtros en la carpeta 'filtros'.")
        exit()

    # Configuración inicial de variables
    indice_filtro = 0  # Índice del filtro actualmente seleccionado
    filtro_actual = filtros_disponibles[indice_filtro]
    filtro_path = os.path.join(carpeta_filtros, filtro_actual + '.png')
    area_min = 10000  # Área mínima para considerar una región como un rostro detectado
    camara = cv2.VideoCapture(0)

    # Verificar si la cámara está disponible
    if not camara.isOpened():
        print("No es posible abrir la cámara")
        exit()

    # Obtener las dimensiones del cuadro de video para la colocación del filtro
    ancho_ventana = int(camara.get(cv2.CAP_PROP_FRAME_WIDTH))
    alto_ventana = int(camara.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Cargar el primer filtro con soporte para canal alfa (transparencia)
    filtro = cv2.imread(filtro_path, cv2.IMREAD_UNCHANGED)

    # Factor de escala para el tamaño del filtro sobre el rostro detectado
    factor_escala = 1.8  

    print("Presiona 'q' para salir, 'n' para el siguiente filtro, 'b' para el filtro anterior.")

    while True:
        # Capturar un fotograma de la cámara
        ret, frame = camara.read()
        if not ret:
            print("No es posible obtener la imagen")
            break

        # Convertir la imagen a escala de grises para la detección de rostros
        frame_byn = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        caras = clasificador.detectMultiScale(frame_byn)

        # Mostrar el nombre del filtro seleccionado en la ventana de la cámara
        cv2.putText(frame, f"Filtro: {filtro_actual}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Iterar sobre los rostros detectados en el fotograma
        for (x_cara, y_cara, ancho_cara, alto_cara) in caras:
            if ancho_cara * alto_cara > area_min:
                # Redimensionar el filtro basado en el tamaño del rostro
                ancho_filtro = int(ancho_cara * factor_escala)
                proporciones_filtro = filtro.shape[1] / filtro.shape[0]
                alto_filtro = int(ancho_filtro / proporciones_filtro)
                filtro_redimensionado = cv2.resize(filtro, (ancho_filtro, alto_filtro))

                # Ajustar la posición del filtro ligeramente por encima del rostro detectado
                y_filtro = y_cara - int(alto_filtro * 0.22)
                x_filtro = x_cara - int(ancho_filtro * 0.22)

                # Verificar que el filtro esté dentro de los límites de la ventana de la cámara
                if (x_filtro >= 0 and y_filtro >= 0 and 
                    x_filtro + ancho_filtro <= ancho_ventana and 
                    y_filtro + alto_filtro <= alto_ventana):
                    
                    roi = frame[y_filtro:y_filtro + alto_filtro, x_filtro:x_filtro + ancho_filtro]

                    # Aplicar el filtro con transparencia si tiene canal alfa
                    if filtro_redimensionado.shape[2] == 4:  # Verificar si existe un canal alfa
                        alpha_filtro = filtro_redimensionado[:, :, 3] / 255.0
                        for c in range(0, 3):  # Aplicar transparencia en cada canal (B, G, R)
                            roi[:, :, c] = roi[:, :, c] * (1 - alpha_filtro) + filtro_redimensionado[:, :, c] * alpha_filtro
                    else:
                        roi[:] = filtro_redimensionado[:]

                    # Reemplazar la región en el fotograma original con el ROI modificado
                    frame[y_filtro:y_filtro + alto_filtro, x_filtro:x_filtro + ancho_filtro] = roi

        # Mostrar el fotograma con el filtro aplicado
        cv2.imshow('Webcam', frame)

        # Crear una imagen para listar los filtros disponibles
        filtros_img = np.zeros((400, 300, 3), dtype=np.uint8)
        cv2.putText(filtros_img, "Filtros disponibles:", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

        # Listar cada filtro en la ventana "Filtros"
        for i, nombre_filtro in enumerate(filtros_disponibles):
            color = (0, 255, 0) if i == indice_filtro else (255, 255, 255)
            cv2.putText(filtros_img, nombre_filtro, (10, 60 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
        
        cv2.imshow("Filtros", filtros_img)

        # Control de teclas para cambiar el filtro o salir del programa
        key = cv2.waitKey(10)
        if key == ord('q'):  # Salir del programa con la tecla 'q'
            break
        elif key == ord('n'):  # Cambiar al siguiente filtro con la tecla 'n'
            indice_filtro = (indice_filtro + 1) % len(filtros_disponibles)
            filtro_actual = filtros_disponibles[indice_filtro]
            filtro_path = os.path.join(carpeta_filtros, filtro_actual + '.png')
            filtro = cv2.imread(filtro_path, cv2.IMREAD_UNCHANGED)
        elif key == ord('b'):  # Cambiar al filtro anterior con la tecla 'b'
            indice_filtro = (indice_filtro - 1) % len(filtros_disponibles)
            filtro_actual = filtros_disponibles[indice_filtro]
            filtro_path = os.path.join(carpeta_filtros, filtro_actual + '.png')
            filtro = cv2.imread(filtro_path, cv2.IMREAD_UNCHANGED)

    # Liberar la cámara y cerrar todas las ventanas
    camara.release()
    cv2.destroyAllWindows()
