import cv2
import numpy as np
import os

# Variables globales y configuración inicial para el color y grosor de dibujo, y dimensiones de la ventana
color = (0, 0, 255)
grosor_seleccionado = 2
dibujando = False  # Variable que indica si se está en modo de dibujo
paleta_altura = 50  # Altura para la paleta de colores
ancho_ventana = 800
altura_ventana = 800  
mask = None  # Máscara usada para almacenar las partes del dibujo
ancho_controles = 800  # Ancho de la ventana de controles (color y grosor)
colores_paleta = [  # Lista de colores en la paleta
    (0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255),
    (128, 0, 128), (0, 128, 128), (128, 128, 0), (0, 0, 128), (128, 0, 0), (0, 128, 0),
    (255, 255, 255), (0, 0, 0), (128, 128, 128), (192, 192, 192), (64, 64, 64)
]
niveles_grosor = [1, 2, 3, 5, 8, 12]  # Niveles disponibles para grosor del pincel
img = None  # Imagen principal para dibujar

# Función para el manejo de eventos de dibujo
def pintar(event, x, y, flags, param):
    global x_prev, y_prev, color, grosor_seleccionado, dibujando, mask

    if event == cv2.EVENT_LBUTTONDOWN:
        dibujando = True  # Habilita el modo de dibujo al presionar el botón izquierdo
        x_prev, y_prev = x, y  # Guarda la posición inicial del clic
    elif event == cv2.EVENT_MOUSEMOVE and dibujando:
        overlay = img.copy()  # Crea una copia de la imagen para superponer temporalmente la línea
        cv2.line(overlay, (x_prev, y_prev), (x, y), color, grosor_seleccionado)
        cv2.addWeighted(overlay, 1, img, 0, 0, img)  # Dibuja la línea con un efecto de superposición
        cv2.line(mask, (x_prev, y_prev), (x, y), (255, 255, 255), grosor_seleccionado)  # Actualiza la máscara
        x_prev, y_prev = x, y  # Actualiza la posición actual para continuar dibujando
        cv2.imshow('Dibujo', img)
    elif event == cv2.EVENT_LBUTTONUP:
        dibujando = False  # Desactiva el modo de dibujo al soltar el botón

# Función para cambiar el color en función de la posición del clic en la paleta
def seleccionar_color(x):
    global color
    ancho_recuadro = ancho_controles // len(colores_paleta)  # Calcula el ancho de cada recuadro de color
    indice_color = x // ancho_recuadro  # Determina el índice de color seleccionado
    if 0 <= indice_color < len(colores_paleta):
        color = colores_paleta[indice_color]  # Actualiza el color global

# Función para cambiar el grosor en función de la posición del clic en el área de grosor
def seleccionar_grosor(x):
    global grosor_seleccionado
    ancho_recuadro = ancho_controles // len(niveles_grosor)  # Calcula el ancho de cada recuadro de grosor
    indice_grosor = x // ancho_recuadro  # Determina el índice de grosor seleccionado
    if 0 <= indice_grosor < len(niveles_grosor):
        grosor_seleccionado = niveles_grosor[indice_grosor]  # Actualiza el grosor global

# Función para seleccionar el color en la ventana de controles
def seleccionar_color_controles(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if y >= paleta_altura:  # Verifica si se hizo clic en la zona de selección de grosor
            seleccionar_grosor(x)
        else:  # Si el clic está en la parte superior, selecciona un color
            seleccionar_color(x)

# Función para borrar el dibujo y resetear la máscara
def borrar_dibujo(contorno):
    global img, mask
    img[:] = contorno.copy()  # Reinicia la imagen con el contorno original
    mask = np.zeros_like(img)  # Limpia la máscara de dibujo
    cv2.imshow('Dibujo', img)

# Función para guardar la imagen de dibujo como archivo PNG con transparencia
def guardar_dibujo():
    if not os.path.exists('filtros'):
        os.makedirs('filtros')  # Crea el directorio de guardado si no existe

    nombre_archivo = input("Ingresa el nombre del archivo para guardar (sin extensión): ")
    ruta_guardado = os.path.join('filtros', f"{nombre_archivo}.png")  # Define la ruta de guardado
    imagen_guardada = np.zeros((img.shape[0], img.shape[1], 4), dtype=np.uint8)  # Añade canal alfa para transparencia
    imagen_guardada[:, :, :3] = img  # Copia la imagen sin transparencia
    imagen_guardada[:, :, 3] = np.where(mask[:, :, 0] == 255, 255, 0)  # Define transparencia basada en la máscara
    cv2.imwrite(ruta_guardado, imagen_guardada)
    print(f"Imagen guardada en {ruta_guardado}")

# Función para dibujar la interfaz de controles (colores y grosor)
def dibujar_area_controles():
    img_controles = np.ones((paleta_altura * 2, ancho_controles, 3), dtype=np.uint8) * 255  # Área de controles

    # Paleta de colores
    ancho_recuadro = ancho_controles // len(colores_paleta)
    for i, c in enumerate(colores_paleta):
        x_inicio = i * ancho_recuadro
        x_fin = (i + 1) * ancho_recuadro
        cv2.rectangle(img_controles, (x_inicio, 0), (x_fin, paleta_altura), c, -1)  # Dibuja cada recuadro de color

    # Controles de grosor
    ancho_recuadro = ancho_controles // len(niveles_grosor)
    for i, grosor in enumerate(niveles_grosor):
        x_inicio = i * ancho_recuadro
        x_fin = (i + 1) * ancho_recuadro
        cv2.rectangle(img_controles, (x_inicio, paleta_altura), (x_fin, paleta_altura * 2), (200, 200, 200), -1)  # Fondo de grosor
        cv2.circle(img_controles, ((x_inicio + x_fin) // 2, paleta_altura 
                    + paleta_altura // 2), grosor, (0, 0, 0), -1)  # Representa el grosor con un círculo

    cv2.imshow('Controles', img_controles)

# Función principal para crear el filtro interactivo
def crear_filtro():
    global img, mask

    # Carga y redimensiona la plantilla de contorno
    contorno = cv2.imread('contornoCara.jpg')
    if contorno is None:
        print("Error: La imagen contornoCara.jpg no se pudo cargar.")
        return

    print("Crea tu propio filtro interactivo. Presiona 'g' para guardar, 'b' para borrar y 'q' para salir.")

    contorno = cv2.resize(contorno, (ancho_ventana, altura_ventana))  # Redimensiona la imagen para la ventana
    img = contorno.copy()
    mask = np.zeros_like(img)  # Inicializa la máscara

    # Configura la ventana de dibujo
    cv2.imshow('Dibujo', img)
    cv2.setMouseCallback('Dibujo', pintar)  # Configura el callback para pintar

    # Configura la ventana de controles
    cv2.namedWindow('Controles')
    dibujar_area_controles()
    cv2.setMouseCallback('Controles', seleccionar_color_controles)  # Callback para seleccionar color y grosor

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('g'):
            guardar_dibujo()
        elif key == ord('b'):
            borrar_dibujo(contorno)
        elif key == ord('q'):
            break

    cv2.destroyAllWindows()
