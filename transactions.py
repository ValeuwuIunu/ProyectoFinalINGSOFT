from datetime import datetime
from mysql.connector import Error
import mysqlx

class Transactions:

    def __init__(self, cursor):
        self.cursor = cursor


    def use_card(self, cvv):
        query = "SELECT id_tarjeta, id_cuenta, cvv, usuario FROM Tarjeta WHERE cvv = '{}'".format(cvv)
        try:
            self.cursor.execute(query)
            for (id_tarjeta, id_cuenta, cvv, u) in self.cursor:
                return {
                    'id_tarjeta': id_tarjeta,
                    'id_cuenta': id_cuenta,
                    'cvv': cvv,
                    'username': u,
                }
            return None
        except Error as ex:
            print("error while creating a xa:", ex)
            print("this is the query:", query)


    def login(self, id_tarjeta, password):
        query = "SELECT contraseña FROM Tarjeta WHERE id_tarjeta={0}".format(id_tarjeta)
        print(query)
        try:
            self.cursor.execute(query)
            contra= self.cursor.fetchall()[0]
            if  password == contra[0]: return True
            return False
        except Error as ex:
            print("error while creating a xa:", ex)
            print("this is the query:", query)


    def get_tarjetas_by_id_cuenta(self, id_cuenta):
        query = "SELECT id_tarjeta, id_cuenta, usuario FROM Tarjeta WHERE id_cuenta={}".format(id_cuenta)
        try:
            self.cursor.execute(query)
            for (id_tarjeta, id_cuenta, username) in self.cursor:
                return {
                    'id_tarjeta': id_tarjeta,
                    'id_cuenta': id_cuenta,
                    'username': username,
                }
            return None
        except Error as e:
            print("Error al hacer el SELECT de la cuenta transferencia:", e)
            print("this is the query:", query)

    def get_cuenta_by_tarjeta(self, id_tarjeta):
        query = "SELECT c.id_cuenta, c.id_cliente, c.cantidad_dinero FROM `Tarjeta` t INNER JOIN `Cuenta` c ON t.id_cuenta = c.id_cuenta WHERE t.id_tarjeta = '{}'".format(id_tarjeta)
        try:
            self.cursor.execute(query)
            for cuenta in self.cursor:
                return cuenta
        except Error as ex:
            print("error while creating a xa:", ex)
            print("this is the query:", query)

    def get_cantidad_dinero(self, id_cuenta):
        query = "SELECT cu.cantidad_dinero FROM Cuenta cu, Tarjeta t WHERE t.id_cuenta = cu.id_cuenta AND t.id_cuenta = {}".format(id_cuenta)
        try:
            self.cursor.execute(query)
            for(cantidad_dinero) in self.cursor:
                return cantidad_dinero
        except Error as e:
            print("Error: "+e)
            print("Query: "+query)

    def update_retiro(self, id_cuenta,valor):
        query = f"UPDATE Cuenta cu SET cu.cantidad_dinero = (cu.cantidad_dinero - {valor}) WHERE cu.id_cuenta = {id_cuenta}"
        try:
            self.cursor.execute(query)
            print("Retiro realizado")
        except Error as e:
            print("Error",e)
            print("Query"+query)

    def update_transferencia(self,id_cuenta,valor):
        query = f"UPDATE Cuenta cu SET cu.cantidad_dinero = (cu.cantidad_dinero + {valor}) WHERE cu.id_cuenta = {id_cuenta}"
        try:
            self.cursor.execute(query)
            print("Transferencia realizada")
        except Error as e:
            print("Error",e)
            print("Query"+query)

    def crear_transaccion(self, valor, id_tarjeta, tipo):
        now = datetime.now()
        hora, fecha = (now.time(), now.date())
        query = "INSERT INTO `Transacciones`(id_tarjeta, hora, fecha, tipo_transaccion, cant_dinero) VALUES (%s, %s, %s, %s, %s)"
        data = (id_tarjeta, hora, fecha, tipo, valor)
        try:
            self.cursor.execute(query, data)
            tiempo = {
                'fecha': fecha,
                'hora': hora
            }
            print("Transaccion guardada")
            return tiempo
        except Error as e:
            print("Error al hacer el insert:", e)
            print("this is the query:", query)

    def get_id_transaccion(self,hora,fecha,id_tarjeta,tipo,valor):
        query = "SELECT id_transaccion, fecha, hora FROM Transacciones WHERE id_tarjeta = %s AND fecha = %s AND hora = %s AND cant_dinero = %s AND tipo_transaccion = %s"
        data = (id_tarjeta, fecha, hora, valor, tipo)
        try:
            self.cursor.execute(query,data)
            for(transacciones) in self.cursor:
                return transacciones
            print("ID transaccion obtenido")
        except Error as e:
            print("Error al hacer el select de get transaccion:", e)
            print("this is the query:", query)

    