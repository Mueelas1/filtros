from crear_filtros import crear_filtro
from usar_filtros import usar_filtros

def mostrar_menu():
    while True:
        print("Menú:")
        print("1. Crear filtros")
        print("2. Usar filtros")
        print("3. Salir")
        opcion = input("Selecciona una opción (1/2/3): ")

        if opcion == '1':
            crear_filtro()

        elif opcion == '2':
            usar_filtros()
            
        elif opcion == '3':
            print("Saliendo del programa.")
            break

        else:
            print("Opción no válida. Por favor, selecciona una opción válida.")

mostrar_menu()
