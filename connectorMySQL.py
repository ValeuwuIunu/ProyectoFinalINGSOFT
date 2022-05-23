import mysql.connector
from mysql.connector import Error



def gen_cnx():
    try:
        cnx = mysql.connector.connect(
            host='b5m7tmxx2gyzch9gnzvf-mysql.services.clever-cloud.com',
            port=3306,
            user='uaogiqnpy4akozm8',
            password='q4PawBo56v8MkxQ3JFHX',
            db='b5m7tmxx2gyzch9gnzvf'
        )
        if cnx.is_connected():
            print("conexion exitosa")
            infoServer = cnx.get_server_info()
            print("Informacion del servidor:",infoServer)

        return cnx
    except Error as ex:
        print("error durante la conexion:", ex)