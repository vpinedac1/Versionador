from menu import menu_principal
import mysql.connector
import sys
import server

if __name__ == '__main__':

    try:
        conn = mysql.connector.connect(user=server.db['user'], password=server.db['password'], host=server.db['host'],
                                       database=server.db['bd'])

    except mysql.connector.Error as err:
        print("No puedo conectar a la base de datos:", err)
        sys.exit(1)
    else:
        cursor = conn.cursor()
        menu_principal(conn, cursor)










