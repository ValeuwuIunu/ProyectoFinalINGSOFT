# imports
from http.client import NON_AUTHORITATIVE_INFORMATION
from flask import Flask, render_template, request, redirect
from config import DevelopmentConfig
from jinja2 import Environment, FileSystemLoader
import mysql.connector
from mysql.connector import Error
import os
from connectorMySQL import gen_cnx
from transactions import Transactions


cnx = gen_cnx()
cursor = cnx.cursor()
transactions = Transactions(cursor)
app = Flask(__name__)

@app.route('/con')
def connection():
    try:
        cdtls = mysql.connector.connect(
            host='b5m7tmxx2gyzch9gnzvf-mysql.services.clever-cloud.com',
            port=3306,
            user='uaogiqnpy4akozm8',
            password='q4PawBo56v8MkxQ3JFHX',
            db='b5m7tmxx2gyzch9gnzvf'
        )
        if cdtls.is_connected():
            print("conexion exitosa")
            infoServer = cdtls.get_server_info()
            print("Informacion del servidor:",infoServer)

        return cdtls
    except Error as ex:
        print("error durante la conexion:", ex)

## app.route = endpoint o sitio a donde me redirige un boton o un ancla <a></a>
@app.route('/')
def init():
    return index()

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/ingresar')
def login():
    message= ""
    return render_template('ingresar.html', message = message)

@app.route('/login', methods=['POST'])
def loginUser():
    if request.method == 'POST':
        # Por POST se trae el parametro CVV de la vista
        _cvv = request.form['cvv']
        if(validar_tarjeta(_cvv)):
            global tarjeta
            tarjeta = Transactions.use_card(transactions,_cvv)
            if tarjeta is not None:
                print(tarjeta)
                return render_template('/seleccionarProceso.html')
            else:
                message = "No se encontro al usuario en el sistema"
                return render_template('/ingresar.html',message = message)
        else:
            message = 'Entrada no valida'
        return render_template('/ingresar.html',message = message)

@app.route('/ingresarContra', methods=['POST'])
def ingresar_contraseña():
    # Por POST se trae el tipo: consulta retiro o transferencia
    _tipo = request.form['tipo']
    message = "Para "+_tipo
    return render_template('contraseña.html', message = message,tipo = _tipo)        
## Validaciones

# Validacion tarjeta CVV
def validar_tarjeta(texto):
    if len(texto)>3:
        return False
    return texto.isnumeric()

# validar contraseña
def validar_contraseña(texto):
    if len(texto)>4:
        return False
    return texto.isnumeric()

# main
if __name__ == "__main__":
    app.config.from_object(DevelopmentConfig)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.run(debug=True)