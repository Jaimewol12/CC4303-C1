import socket
from http_reader import *
import os
from dotenv import load_dotenv
# Creamos el cliente

print("Creando cliente...")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Definimos las variables de entorno
load_dotenv()

server_host: str = os.getenv('SERVER_HOST', 'localhost')
server_port: int = int(os.getenv('SERVER_PORT', 8000))

adress: tuple = (server_host, server_port)

# Establecemos la conexión con el server
client_socket.connect(adress)

# Creamos la solicitud HTTP

method: str = 'GET'
route: str = '/'
request_HTTP_client: RequestHttp = RequestHttp(method, route)
version: float = 1.1
header: dict = {'Host': 'localhost', 'Content-Type': 'text/html; charset=UTF-8', 'X-ElQuePregunta': 'Memo'}

# Creamos la estructura
http_request_struct: HttpContent = HttpContent(request_HTTP_client, version, header, body=b'')

# La parseamos a HTTP
http_request_encoded: bytes = create_HTTP_message(http_request_struct)

# Se envia el request
client_socket.send(http_request_encoded)

# Le llega un response
message_response = client_socket.recv(1024)
print(message_response)
