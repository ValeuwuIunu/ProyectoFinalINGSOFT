# imports
from flask import Flask, render_template, request
from config import DevelopmentConfig
import mysql.connector
from mysql.connector import Error
import os
from connectorMySQL import gen_cnx
from transactions import Transactions


cnx = gen_cnx()
cursor = cnx.cursor()
transactions = Transactions(cursor)
app = Flask(__name__)

## Endpoint para probar la conexion con la BD
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

## app.route = endpoint o sitio a donde me redirige un Form o un ancla <a></a>
@app.route('/')
def init():
    return index()

## Endpoint inicio
@app.route('/index')
def index():
    return render_template('index.html')

## Endpoint para vista ingresar
@app.route('/ingresar')
def login():
    message= ""
    return render_template('ingresar.html', message = message)

##Endpoint al que se redirige despues de darle al boton para ingresar con CVV
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

@app.route('/validatePassword', methods=['POST'])
def contrasena_validar():
    # Por POST se trae la contraseña ingresada y el tipo: consulta, retiro o transferencia 
    _tipo = request.form['tipo']
    _pass = request.form['pass']
    if(validar_contraseña(_pass)):
        verificacion = transactions.login(tarjeta['id_tarjeta'],int(_pass))
        if (verificacion):
            print("contraseña correcta")
            message = "" 
            saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])
            messageSaldo = "Estimado "+tarjeta['username']+", su saldo actual es de: "+ str(saldo[0])
            if (_tipo == "consultas"):
                return render_template('/consultas.html',message = message,messageSaldo = messageSaldo)
            elif(_tipo == "retiros"):
                return render_template('/retiros.html',message = message)
            elif(_tipo == "transferencias"):  
                return render_template('/transferencias.html',message = message)
        message = "Contraseña incorrecta"      
        return render_template('/contraseña.html',message = message,tipo = _tipo)

@app.route('/retirar',methods=['POST'])
def retirar_por_valor():
    # Por post se trae el valor seleccionado de los botones
    _valor = request.form['valor']
    saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])[0]
    if(validar_saldo_retirar(int(_valor),saldo)):
        transactions.update_retiro(tarjeta['id_cuenta'],int(_valor))
        nuevo_saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])[0]
        tiempo = transactions.crear_transaccion(int(_valor),tarjeta['id_tarjeta'],"Retiro")
        datos_transaccion = transactions.get_id_transaccion(tiempo['hora'],tiempo['fecha'],tarjeta['id_tarjeta'],"Retiro",int(_valor))
        message = "Retiro realizado con exito"
        cnx.commit()
        return render_template('/recibo.html',nuevo_saldo = nuevo_saldo,valor = _valor,message = message,transaccion = datos_transaccion,tarjeta = tarjeta)
    else:
        message = "No puede retirar esa cantidad de dinero actualmente"
        return render_template('/retiros.html',message = message)

@app.route('/cantidadRetiro')
def vista_retirar_cantidad():
    message = ''
    return render_template('/retirarCantidad.html',message = message)

@app.route('/retirarCantidadDinero',methods=['POST'])
def retirar_valor_ingresado():
    # Por post se trae el valor digitado ingresado por el usuario
    _valor = request.form['valor']
    saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])[0]
    try:
        if(validar_valor(_valor) and validar_valor_ingresado(int(_valor)) and validar_saldo_retirar(int(_valor),saldo)):
            if(validacion_no_monedas(_valor)):
                transactions.update_retiro(tarjeta['id_cuenta'],int(_valor))
                nuevo_saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])[0]
                tiempo = transactions.crear_transaccion(int(_valor),tarjeta['id_tarjeta'],"Retiro")
                datos_transaccion = transactions.get_id_transaccion(tiempo['hora'],tiempo['fecha'],tarjeta['id_tarjeta'],"Retiro",int(_valor))
                message = "Retiro realizado con exito"
                cnx.commit()
                return render_template('/recibo.html',nuevo_saldo = nuevo_saldo,valor = _valor,message = message,transaccion = datos_transaccion,tarjeta = tarjeta)
            else:
                message = "No se pueden retirar monedas"
                return render_template('/retirarCantidad.html',message = message) 
        else:
            message = "Valor ingresado no valido"
            return render_template('/retirarCantidad.html',message = message)
    except Error as e:
        message = "Algo sucedio en retirar cantidad valor ingresado"
        return render_template('/retirarCantidad.html',message = message)

@app.route('/buscarCuenta',methods=['POST'])
def buscar_cuenta():
    # por post se trae el # de cuenta
    _cuenta = request.form['cuenta']
    if(validar_cuenta(_cuenta)):
        tarjeta_transferencia = transactions.get_tarjetas_by_id_cuenta(int(_cuenta))
        if(tarjeta['username'] == tarjeta_transferencia['username']):
            message="No se puede transferir dinero a usted mismo"  
            return render_template('/transferencias.html',message = message)    
        else:
            message=""  
            return render_template('/cantidadTransferencia.html',message = message,tarjeta_transferencia = tarjeta_transferencia)
    else:
        message = "Valor ingresado no valido"
        return render_template('/transferencias.html',message = message)

@app.route('/transferirDinero',methods=['POST'])
def enviar_dinero():
    _user = request.form['usuario']
    _card = request.form['tarjeta']
    _cuenta = request.form['cuenta']
    _valor = request.form['valor']
    _tarjeta_transferencia = {
        'id_tarjeta':_card,
        'id_cuenta':_cuenta,
        'username':_user
    }
    message = "Algo paso"
    try:
        print("Antes de saldo")
        saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])[0]
        # Se usa el metodo validar_cuenta para verificar que se envie un numero mayor a 0
        if(validar_saldo_retirar(int(_valor),saldo) and validar_mayor_cero(_valor)):
            transactions.update_retiro(tarjeta['id_cuenta'],int(_valor))
            nuevo_saldo = transactions.get_cantidad_dinero(tarjeta['id_cuenta'])[0]
            tiempo = transactions.crear_transaccion(int(_valor),tarjeta['id_tarjeta'],"Retiro")
            datos_transaccion = transactions.get_id_transaccion(tiempo['hora'],tiempo['fecha'],tarjeta['id_tarjeta'],"Retiro",int(_valor))
            transactions.update_transferencia(int(_cuenta),int(_valor))
            message = "Transferencia realizada con exito"
            cnx.commit()
            return render_template('/recibo.html',nuevo_saldo = nuevo_saldo,valor = _valor,message = message,transaccion = datos_transaccion,tarjeta = tarjeta)
    except Error as e:
        message = "Algo sucedio al realizar la transferencia de la cantidad valor ingresado"
        return render_template('/cantidadTransferencia.html',message = message,tarjeta_transferencia = _tarjeta_transferencia)
    
    return render_template('/cantidadTransferencia.html',message = message,tarjeta_transferencia = _tarjeta_transferencia)
        

## Validaciones
def validar_mayor_cero(texto):
    if(len(texto)<=0):
        return False
    return texto.isnumeric()

# Validacion para entero
def validar_cuenta(texto):
    if(len(texto)>1):
        return False
    return texto.isnumeric()

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

# Validar si saldo a retirar es mayor que saldo actual
def validar_saldo_retirar(valor1,valor2):
    if(valor1 > valor2):
        return False
    return True

#validar saldo ingresado
def validar_valor(valor):
    if len(valor) < 5 or len(valor) > 7:
        return False
    return valor.isnumeric()

# validar valor
def validar_valor_ingresado(valor):
    if valor < 20000 or valor > 2700000:
        return False
    return True

# validacion para no entregar monedas
def validacion_no_monedas(valor):
    if ((valor[len(valor)-1] == '0') and (valor[len(valor)-2] == '0') and (valor[len(valor)-3] == '0')):
        return True
    else:
        return False

# validacion para que el numero ingresado sea mayor a 0
def validar_numero(valor):
    if(valor > 0):
        return True
    else:
        return False

# main
if __name__ == "__main__":
    app.config.from_object(DevelopmentConfig)
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.run(debug=True)