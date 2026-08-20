import socket
from http_reader import *
# Creamos el cliente

print("Creando cliente...")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Definimos las variables de entorno
adress = ('localhost', 5000)

# Establecemos la conexión con el server
client_socket.connect(adress)

# Creamos la solicitud HTTP

method: str = 'GET'
route: str = '/'
request_HTTP_cient: RequestHttp = RequestHttp(method, route)
version: float = 1.1
header: dict = {'Host': 'localhost', 'Content-Type': 'text/html; charset=UTF-8'}

# Creamos la estructura
http_request_strcut: HttpContent = HttpContent(request_HTTP_cient, version, header, body=b'')

# La parseamos a HTTP
http_request_encoded: bytes = create_HTTP_message(http_request_strcut)

# Se envia el request
client_socket.send(http_request_encoded)

# Le llega un response
message_response = client_socket.recv(1024)
print(message_response)
