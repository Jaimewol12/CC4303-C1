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
    body: str = 'hola'
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

        http_response = receive_http_request(server_socket, buff_size)

        server_socket.send(http_response)





