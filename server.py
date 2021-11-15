from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from typing import NamedTuple
from urllib import parse
import json
import mysql.connector
from mysql.connector import Error
from collections import namedtuple
class crud:
    def __init__(self):
        print("Iniciando conexion con la base de datos...")
        self.db = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            passwd="",
            database="db_academica_a2"
        )
        if self.db.is_connected():
            print("Conexion establecida")
        else:
            print("Conexion fallida")

    def consultar(self):
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT * FROM alumnos LIMIT 0, 5"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def administrar_alumno(self, alumno):
        if alumno["accion"]=="nuevo":
            sql = "INSERT INTO alumnos (codigo, nombre, telefono) VALUES (%s, %s, %s)"
            val = (alumno["codigo"], alumno["nombre"], alumno["telefono"])
        elif alumno["accion"]=="modificar":
            sql = "UPDATE alumnos SET codigo=%s, nombre=%s, telefono=%s WHERE idAlumno=%s"
            val = (alumno["codigo"], alumno["nombre"], alumno["telefono"], alumno["idAlumno"])
        elif alumno["accion"]=="eliminar":
            sql = "DELETE FROM alumnos WHERE idAlumno=%s"
            val = (alumno["idAlumno"],)
        return self.ejecutar_consultas(sql, val)
    
    def ejecutar_consultas(self, sql, val):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, val)
            self.db.commit()
            return "Registro procesado con exito"
        except Exception as e:
            return "Error: " + str(e)
crud = crud()
class servidorBasico(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        elif self.path == "/iniciar-sesion":
            self.path = "/iniciar-sesion.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        elif self.path == "/registrar":
            self.path = "/registrar.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        elif self.path == "/crear-votacion":
            self.path = "/crear-votacion.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path=="/consulta":
            resp = crud.consultar()
            resp = json.dumps(dict(data=resp))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode("utf-8"))

    def do_POST(self):
        longitud_contenido = int(self.headers['Content-Length'])
        contenido = self.rfile.read(longitud_contenido)
        contenido = contenido.decode("utf-8")
        contenido = parse.unquote(contenido)
        contenido = json.loads(contenido)
        resp = crud.administrar_alumno(contenido)
        resp = json.dumps(dict(resp=resp))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(resp.encode("utf-8"))

print("Servidor iniciado")
server = HTTPServer(("localhost", 3000), servidorBasico)
server.serve_forever()