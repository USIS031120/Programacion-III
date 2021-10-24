import tensorflow as tf
import pandas as pd
from urllib import parse
from http.server import HTTPServer, BaseHTTPRequestHandler

temperaturas = pd.read_csv("C:/Users/USUARIO/Desktop/Parcial 2/datos.csv", sep=",")

celsius = temperaturas["celsius"]
fahrenheit = temperaturas["fahrenheit"]

modelo = tf.keras.Sequential()
modelo.add(tf.keras.layers.Dense(units=1, input_shape=[1]))

modelo.compile(optimizer=tf.keras.optimizers.Adam(1), loss="mean_squared_error")

modelo.fit(celsius, fahrenheit, epochs=100)

class servidorBasico(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Peticion GET recibida")
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        #Enviar respuesta
        self.wfile.write("Hola Chicos de Programacion III".encode())

    def do_POST(self):
        print("Peticion recibida")

        #Obtener datos de la peticion y limpiar los datos
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)

        data = data.decode().replace("celsius=", "")
        data = parse.unquote(data)
        data = float(data)
        
        prediccion = modelo.predict([data])
        print("Prediccion final: ", prediccion)

        #Regresar respuesta a la peticion HTTP
        self.send_response(200)
        #Evitar problemas con CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        prediccion = str(prediccion[0][0])
        self.wfile.write(prediccion.encode())

print("Iniciando el servidor... en el puerto 3004")
server = HTTPServer(('localhost', 3004), servidorBasico)
server.serve_forever()