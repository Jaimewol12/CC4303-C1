import socket 
from http_reader import *
import os
from dotenv import load_dotenv
import json

def receive_client_request(connection_socket: socket, buff_size: int): 

    # Recibimos el request HTTP del cliente
    http_request: bytes = connection_socket.recv(buff_size)

    # Pasamos el request a la estrutura creada
    request_parse: HttpContent = parse_HTTP_message(http_request)

    return request_parse

def proxy_http_request(request_parsed: HttpContent, buff_size: int):

    # Obtenemos la dirección a la que se busca conectar
    request_adress: str = request_parsed.header.get('Host').lstrip()

    # Creamos un nuevo socket para la conexión al destino
    new_socket_destiny = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Establecemos conexión con el servidor
    destiny_server_adress: tuple = (request_adress, 80)
    new_socket_destiny.connect(destiny_server_adress)

    # Enviamos la solicitud
    proxy_to_destiny_request: bytes = create_HTTP_message(request_parsed)
    new_socket_destiny.send(proxy_to_destiny_request)

    # Esperamos la respuesta
    destiny_response: bytes = new_socket_destiny.recv(buff_size)

    return destiny_response

def is_forbidden_adress(http_request: HttpContent, json_file: str):
    # Abrimos el archivo del filtro
    with open(json_file) as file:
        data = json.load(file)

        # Obtenemos del JSON la lista de dominios prohibidos
        filtered_adresses: list = data.get('blocked')

        # Obtenemos del request del cliente al dominio el cual quiere acceder
        client_adress_requested: str = http_request.header.get('Host').lstrip()

        # Si ese Host request está dentro de la lista de los dominios prohibidos, entonces retorna True
        # Si no, retorna False
        for adress in filtered_adresses:
            if adress == client_adress_requested:
                return True
        return False


def proxy_adress_filter():
    return

def proxy_content_filter():
    return

if __name__ == "__main__":

    # Defino el tamaño de buffer 
    buff_size = 1024

    # Creamos el socket no orientado a conexion
    server_host: str = os.getenv('SERVER_HOST', 'localhost')
    server_port: int = int(os.getenv('SERVER_PORT', 5000))

    server_socket_adress: tuple = (server_host, server_port)

    print('Creando socket del servidor')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket orientado a conexión

    server_socket.bind(server_socket_adress)
    server_socket.listen(3)

    print("... Esperando clientes")
    # Dejamos el server prendido
    
    while True:
        new_socket, new_socket_adress = server_socket.accept()

        #http_response = receive_http_request(new_socket, buff_size)

        # Recibimos la request del cliente
        http_client_request = receive_client_request(new_socket, buff_size)
        print(f"Nueva {http_client_request.type.method} Request de: {http_client_request.header.get('X-ElQuePregunta')} a {http_client_request.header.get('Host')}")

        # Revisamos que no sea una página prohibida
        if is_forbidden_adress(http_client_request, 'filtro.json'):
            print("Proxy encontró dominio prohibido")
            # Acá se debe aplicar proxy_adress_filter() y retornar el mensaje de error 403 con la fotito

        else:
            print("Proxy no encontró, pero hay que filtrar las palabras")
            # Ahora pasamos su request al Host (dirección de destino)
            destiny_response = proxy_http_request(http_client_request, buff_size)

            # Acá se debe filtrar el contenido según el proxy usando proxy_content_filter()

            
            # Retornamos el response filrado al cliente
            





