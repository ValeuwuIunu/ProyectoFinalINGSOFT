from datetime import datetime
from mysql.connector import Error

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


    def create_xa(self, amount, id_tarjeta, xa_type):
        now = datetime.now()
        hora, fecha = (now.time(), now.date())
        query = "INSERT INTO `Transacciones`(id_tarjeta, hora, fecha, tipo_transaccion, cant_dinero) VALUES (%s, %s, %s, %s, %s)"
        data = (id_tarjeta, hora, fecha, xa_type, amount)

        try:
            self.cursor.execute(query, data)
        except Error as ex:
            print("error while creating a xa:", ex)
            print("this is the query:", query)

    def get_tarjetas_by_id_cuenta(self, id_cuenta):
        query = "SELECT id_tarjeta, id_cuenta, usuario, constraseña FROM `Tarjet` WHERE id_cuenta='{}'".format(id_cuenta)
        try:
            self.cursor.execute(query)
            res = []
            for (id_tarjeta, id_cuenta, username, password) in self.cursor:
                res.add({'id_tarjeta': id_tarjeta, 'id_cuenta': id_cuenta, 'username': username, 'password': password})

            return res
        except Error as ex:
            print("error while creating a xa:", ex)
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