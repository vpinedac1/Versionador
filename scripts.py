import time
import paramiko
from colorama import init, Fore, Back, Style
import mysql.connector
from progress.bar import ChargingBar
from libreria import borrar_pantalla


def consultar_version():
    version = input('Version: ')
    return version


def consultar_servidores(registros_servidor, version):
    print(f'Los siguientes servidores se actualizaran en la versión v{version}:')
    for IdServidor, DireccionIP, User, Password in registros_servidor:
        print(f'IP: {DireccionIP}')
    while (a := input('Desea Continuar[S/N]: ')) not in {'S', 'N'}:
        print('Opción incorrecta, vuelva a intentarlo.')
    if a == 'S':
        return True
    else:
        return False


def actualizar_version(conn, cursor, ambiente, comp, servidor, version):
    sql_buscar_version = f'SELECT * FROM version WHERE IdAmbiente = {ambiente} AND IdComponente = {comp} AND ' \
                         f'IdServidor = {servidor}'

    try:
        cursor.execute(sql_buscar_version)
        registros_version = cursor.fetchall()
    except:
        print("Error en la consulta Tabla Version")
    else:
        if len(registros_version) > 0:
            try:
                sql_update_version = f'UPDATE version SET  Version = "{version}"'
                cursor.execute(sql_update_version)
                conn.commit()
            except mysql.connector.Error as err:
                print("Error no se pudo actualizar Tabla Version", err)
                conn.rollback()
        else:
            try:
                sql_insert_version = f"""INSERT INTO  version(IdAmbiente, IdComponente, IdServidor, Version) VALUES""" \
                                     f"""({ambiente}, {comp}, {servidor}, '{version}')"""
                cursor.execute(sql_insert_version)
                conn.commit()
            except mysql.connector.Error as err:
                print("Error no se pudo Insertar Tabla Version", err)
                # Rolling back in case of error
                conn.rollback()


def componente(conn, cursor, seleccion):
    ambiente = seleccion[0]
    tipo_comp = seleccion[1]
    comp = seleccion[2]

    sql_servidor = f'SELECT  IdServidor, DireccionIP, User, Password FROM servidor WHERE Idservidor IN ( SELECT ' \
                   f'IdServidor FROM comando WHERE IdAmbiente = {ambiente} AND IdCompTipo = {tipo_comp} ' \
                   f'AND IdComponente = {comp} ORDER BY IdServidor )'

    try:
        cursor.execute(sql_servidor)
        registros_servidor = cursor.fetchall()
    except:
        print("Error en la consulta Tabla Servidor")
    else:
        if len(registros_servidor) > 0:
            borrar_pantalla()
            version = consultar_version()
            if consultar_servidores(registros_servidor, version):
                i = 1
                for IdServidor, DireccionIP, User, Password in registros_servidor:
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    try:
                        client.connect(DireccionIP, username=User, password=Password)
                        # Validamos que se pueda ejecutar el shell
                        shell = client.invoke_shell()
                    except IOError as error:
                        print(error)
                    except paramiko.ssh_exception.AuthenticationException as e:
                        print('Autenticacion fallida.')
                    else:
                        sql_comando = f'SELECT Comando, TiempoComando FROM comando WHERE IdAmbiente = {ambiente} ' \
                                      f'AND IdComponente = {comp} AND IdServidor = {IdServidor} ORDER BY IdServidor'
                        try:
                            cursor.execute(sql_comando)
                            registros_comandos = cursor.fetchall()

                        except:
                            print("Error en la consulta Tabla Comando")

                        else:
                            borrar_pantalla()
                            bar = ChargingBar(f'Actualizando servidor {DireccionIP}:', max=len(registros_comandos))
                            print(f'Conectado al Servidor IP: {DireccionIP}')
                            log_error = []

                            for comando, TiempoComando in registros_comandos:
                                nuevo_comando = comando.replace('+version', version)
                                #                                #print(nuevo_comando)
                                stdin, stdout, stderr = client.exec_command(nuevo_comando)
                                time.sleep(TiempoComando)
                                error = stderr.read()
                                if error.decode("utf-8") != '':
                                    log_error.append(error.decode("utf-8"))
                                bar.next()
                            bar.finish()
                            print('Errores: ', len(log_error))
                            if len(log_error) > 0:
                                while (a := input('Desea visualizar los Errores [S/N]: ')) not in {'S', 'N'}:
                                    print('Opción incorrecta, vuelva a intentarlo.')
                                if a == 'S':
                                    for e in log_error:
                                        print(e)
                            actualizar_version(conn, cursor, ambiente, comp, IdServidor, version)
                        if i == len(registros_servidor):
                            print(Fore.GREEN + 'PROCESO FINALIZADO')
                            print(Style.RESET_ALL)
                        i += 1
                        input("\n Presione Enter para continuar")
                        borrar_pantalla()

                    client.close()
                    shell.close()
                seleccion.pop()
            else:
                seleccion.pop()
        else:
            print(Fore.YELLOW + 'NO SE ENCUENTRAN SERVIDORES PARA LA SELECCIÓN')
            print(Style.RESET_ALL)
            seleccion.pop()
