import socket 
from http_reader import *

def receive_http_request(connection_socket, buff_size):

    # Recibimos el request http del cliente
    http_request = connection_socket.recv(buff_size)

    # Pasamos el request a la estructura creada usando la funcion parse
    request_parsed = parse_HTTP_message(http_request)

    # Crearemos un response para enviar al cliente
    response_struct: ResponseHttp = ResponseHttp(200, 'OK')
    version: float = request_parsed.version
    header: dict = {'Content-Type': 'text/html; charset=UTF-8', 'Content-Lenght': '4'}
    body_str = """<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Servidor Python</title>
                    <style>
                        body { font-family: sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                        .card { background: #1e293b; padding: 2rem; border-radius: 10px; text-align: center; }
                        h1 { color: #38bdf8; }
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h1>¡Conexión Exitosa!</h1>
                        <p>Página servida desde tu socket TCP en Python.</p>
                    </div>
                </body>
                </html>"""

    body: bytes = body_str.encode()
    Http_response_struct: HttpContent = HttpContent(response_struct, version, header, body)

    # Parseamos el response de la estructura a formato HTTP
    response_http = create_HTTP_message(Http_response_struct)

    return response_http

if __name__ == "__main__":

    # Defino el tamaño de buffer 
    buff_size = 1024

    # Creamos el socket no orientado a conexion
    server_socket_adress = ('localhost', 5000) # Dirección

    print('Creando socket del servidor')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket orientado a conexión

    server_socket.bind(server_socket_adress)
    server_socket.listen(3)

    print("... Esperando clientes")
    # Dejamos el server prendido
    
    while True:
        new_socket, new_socket_adress = server_socket.accept()

        http_response = receive_http_request(new_socket, buff_size)

        new_socket.send(http_response)





