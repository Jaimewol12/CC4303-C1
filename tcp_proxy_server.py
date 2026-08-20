import socket 
from http_reader import *

def receive_http_request(connection_socket, buff_size):

    # Recibimos el request http del cliente
    http_request, adress = connection_socket.recvfrm(buff_size)

    # Pasamos el request a la estructura creada usando la funcion parse
    request_parsed = parse_HTTP_message(http_request)

    body = "hola"
    response_http = create_HTTP_message()

    return (response_http, adress)

if __name__ == "__main__":

    # Defino el tamaño de buffer 
    buff_size = 1024

    # Creamos el socket no orientado a conexion
    new_socket_adress = ('localhost', 5000) # Dirección

    print('Creando socket del servidor')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Socket

    server_socket.bind(new_socket_adress)

    print("... Esperando clientes")
    # Dejamos el server prendido
    
    while True:
        http_response, adress_request = receive_http_request(server_socket, buff_size)

        server_socket.sendto(http_response, adress_request)





