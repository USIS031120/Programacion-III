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
            database="sistema_votaciones"
        )
        if self.db.is_connected():
            print("Conexion establecida")
        else:
            print("Conexion fallida")

    def consultar(self):
        cursor = self.db.cursor(dictionary=True)
        sql = "SELECT * FROM votaciones LIMIT 0, 5"
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def administrar_votacion(self, votacion):
        if votacion["accion"]=="nuevo":
            sql = "INSERT INTO votaciones (nombre) VALUES (%s)"
            val = (votacion["nombre"])
        return self.ejecutar_consultas(sql, val)
    
    def ejecutar_consultas(self, sql, val):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, val)
            self.db.commit()
            return "Registro procesado con exito"
        except Exception as e:
            return "Error: " + str(e)

    def iniciar_sesion(self, contenido):
        sql = "SELECT * FROM usuarios WHERE dui = %s AND clave = %s"
        val = (contenido["dui"], contenido["clave"])
        # return self.ejecutar_consultas(sql, val)
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        if len(result) != 0:
            crud.sesion["dui"] = contenido["dui"]
        return result

    def consultar_votacion(self, contenido):
        sql = "SELECT * FROM candidatos WHERE idVotacion = %s"
        val = (contenido["id"],)
        cursor = self.db.cursor(dictionary=True)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        return result
    sesion = {"dui": ""}
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
        elif self.path == "/elecciones":
            self.path = "/elecciones.html"
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

        if self.path == "/crear":
            resp = crud.administrar_votacion(contenido)
            resp = json.dumps(dict(resp=resp))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode("utf-8"))

        if self.path == "/iniciar-sesion":
            resp = crud.iniciar_sesion(contenido)
            resp = json.dumps(dict(resp=resp))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode("utf-8"))
        if self.path == "/votacion":
            resp = crud.consultar_votacion(contenido)
            resp = json.dumps(dict(data=resp))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode("utf-8"))
        if self.path == "/access":
            if crud.sesion["dui"] != "" and contenido["dui"] == crud.sesion["dui"]:
                resp = crud.sesion["dui"]
            else:
                resp = {"ok": False}
            resp = json.dumps(dict(data=resp))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode("utf-8"))
        if self.path == "/logout":
            crud.sesion["dui"] == ""
            resp = json.dumps(dict(data=resp))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(resp.encode("utf-8"))
print("Servidor iniciado")
server = HTTPServer(("localhost", 3000), servidorBasico)
server.serve_forever()