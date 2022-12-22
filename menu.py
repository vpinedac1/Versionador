import scripts as s
from colorama import init, Fore, Back, Style
from libreria import borrar_pantalla


def mostrar_menu(nombre, opciones):  # incorporamos el parámetro para mostrar el nombre del menú
    print(Style.BRIGHT)
    print(f'#  {nombre}')
    print(Style.RESET_ALL)
    for clave in opciones:
        print(f'    {clave} - {opciones[clave][0]}')


def leer_opcion(opciones):
    while (a := input('Opción: ')) not in opciones:
        print('Opción incorrecta, vuelva a intentarlo.')
    return a


def ejecutar_opcion(conn, cursor, opcion, opciones, seleccion):
    opciones[opcion][1](conn, cursor, seleccion)


def generar_menu(conn, cursor, nombre, opciones, opcion_salida,
                 seleccion):  # incorporamos el parámetro para mostrar el nombre del menú
    opcion = None
    borrar_pantalla()
    while opcion != opcion_salida:
        mostrar_menu(nombre, opciones)
        opcion = leer_opcion(opciones)
        if opcion != opcion_salida:
            seleccion.append(opcion)
        elif len(seleccion) >= 1:
            seleccion.pop()
        ejecutar_opcion(conn, cursor, opcion, opciones, seleccion)
        print()

    if nombre == 'Menú Ambientes':
        conn.close()


def cargar_opciones(conn, cursor, seleccion):
    opciones = {}
    if len(seleccion) == 0:
        sql = 'SELECT NomAmbiente FROM ambiente'
        try:
            cursor.execute(sql)
            registros = cursor.fetchall()

            i = 1
            for registro in registros:
                opciones[f'{i}'] = (registro[0], menu_tipo_componente)
                i = i + 1
            opciones['S'] = ("Salir", salir)

        except:
            print("Error en la consulta Tabla Ambiente")

    elif len(seleccion) == 1:
        sql = 'SELECT NomComTipo FROM componente_tipo'
        try:
            cursor.execute(sql)
            registros = cursor.fetchall()

            i = 1
            for registro in registros:
                opciones[f'{i}'] = (registro[0], menu_componente)
                i = i + 1
            opciones['S'] = ("Salir", salir)

        except:
            print("Error en la consulta Tabla Componente Tipo")

    elif len(seleccion) == 2:
        sql = 'SELECT NomComponente FROM componente WHERE IdComTipo = ' + seleccion[1]
        try:
            cursor.execute(sql)
            registros = cursor.fetchall()

            i = 1
            for registro in registros:
                opciones[f'{i}'] = (registro[0], s.componente)
                i = i + 1
            opciones['S'] = ("Salir", salir)

        except:
            print("Error en la consulta Tabla Componente")

    return opciones


def menu_principal(conn, cursor):
    seleccion = []
    opciones = cargar_opciones(conn, cursor, seleccion)
    generar_menu(conn, cursor, 'MENÚ AMBIENTES', opciones, 'S', seleccion)  # indicamos el nombre del menú


def menu_tipo_componente(conn, cursor, seleccion):
    opciones = cargar_opciones(conn, cursor, seleccion)
    generar_menu(conn, cursor, 'MENÚ TIPO COMPONENTE', opciones, 'S',
                 seleccion)  # indicamos el nombre del submenú


def menu_componente(conn, cursor, seleccion):
    opciones = cargar_opciones(conn, cursor, seleccion)
    generar_menu(conn, cursor, 'MENÚ COMPONENTE', opciones, 'S',
                 seleccion)  # indicamos el nombre del submenú


def salir(conn, cursor, seleccion):
    borrar_pantalla()
