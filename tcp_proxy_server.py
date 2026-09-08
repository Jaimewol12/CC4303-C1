import socket 
from http_reader import *
import os
import json

def receive_and_parse_full_message(connection_socket: socket, buff_size: int) -> HttpContent:
    """Utiliza un socket para recibir un mensaje HTTP crudo y lo almacena en una estructura.

    El mensaje es recibido completamente incluso si 'buff_size' es menor que el largo del
    HEAD o BODY del mensaje.
    
    Args:
        connection_socket (socket.socket): Socket TCP activo conectado al cliente.
        buff_size (int): Tamaño del buffer de recepción en bytes.

    Returns:
        HttpContent: Objeto con la información de la petición HTTP (método, headers, body, etc.).
    """
    http_message: bytes = connection_socket.recv(buff_size)

    # Aseguramos que todos los bytes del HEAD fueron recibidos
    while b"\r\n\r\n" not in http_message:
        http_message += connection_socket.recv(buff_size)

    http_struct: HttpContent = parse_HTTP_message(http_message)

    if "Content-Length" in http_struct.head:
        # Aseguramos que todos los bytes del BODY fueron recibidos
        while len(http_struct.body) < int(http_struct.head["Content-Length"]):
            http_struct.body += connection_socket.recv(buff_size)

    return http_struct

        
def proxy_http_request(http_struct: HttpContent, buff_size: int) -> HttpContent:
    """Se conecta al servidor web de destino, reenvía la petición del cliente y parsea su respuesta.

    Args:
        http_struct (HttpContent): Petición del cliente parseada en objeto HttpContent.
        buff_size (int): Tamaño del búfer para recibir la respuesta remota.

    Returns:
        HttpContent: Objeto con la información de la respuesta enviada por el servidor de destino.
    """

    # Obtenemos la dirección a la que se busca conectar el cliente
    client_request_address: str = http_struct.head["Host"].lstrip()
    ip_to_connect: str = client_request_address.split(":")[0]
    destination_address: tuple = (ip_to_connect, 80)

    # Creamos un nuevo socket para la conexión al destino
    socket_for_destination = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Establecemos conexión con el servidor
    socket_for_destination.connect(destination_address)

    # Enviamos la solicitud al servidor de destino
    http_struct.head["X-ElQuePregunta"] = "Jaime Sepulveda"
    http_message_to_destination: bytes = create_HTTP_message(http_struct)
    socket_for_destination.send(http_message_to_destination)

    # Esperamos la respuesta completa del servidor y la almacenamos en nuestra estructura de datos
    http_struct_from_server: HttpContent = receive_and_parse_full_message(socket_for_destination, buff_size)

    # Cerramos la conexión proxy - servidor
    socket_for_destination.close()

    return http_struct_from_server

def is_forbidden_adress(http_client_request: HttpContent, json_file: str) -> bool:
    """Evalúa si la dirección solicitada por el cliente se encuentra en la lista negra del JSON.

    Args:
        http_client_request (HttpContent): Petición HTTP del cliente parseada.
        json_file (str): Ruta al archivo JSON de configuración ("filtro.json").

    Returns:
        bool: True si la dirección está bloqueada; False en caso contrario.
    """
    
    # Abrimos el archivo del filtro
    with open(json_file) as file:
        data = json.load(file)

        # Revisamos si la dirección del request está dentro de la lista de direcciones prohibidas
        for blocked_address in data["blocked"]:
            if blocked_address in http_client_request.type.route:
                return True
            
    return False


def create_forbidden_page_response(version: float = 1.1) -> bytes:
    """Construye una respuesta HTTP 403 Forbidden personalizada con un cuerpo HTML indicando el bloqueo.

    Args:
        version (float, optional): Versión del protocolo HTTP a responder. Por defecto 1.1.

    Returns:
        bytes: Respuesta HTTP 403 completa en bytes lista para ser enviada al cliente.
    """
    # Preparamos la respuesta con la información de la página bloqueada
    http_response_status: ResponseHttp = ResponseHttp(403, "Forbidden")
    version: float = version
    head: dict[str, str] = {'Content-Type': 'text/html; charset=UTF-8'}
    body: bytes = (b"""
    <html>
        <head>
            <title>An Example</title>
        </head>
        <body>
            <h1>Error 403</h1>
            <img src="MaomaoTheCat.png">
        </body>
    </html>
    """)
    head['Content-Length'] = len(body)

    # Creamos la estructura de datos con toda la información y la convertimos a bytes
    http_struct: HttpContent = HttpContent(http_response_status, version, head, body=body)
    http_message_to_client: bytes = create_HTTP_message(http_struct)

    return http_message_to_client

def create_forbidden_image_response(version: float = 1.1) -> bytes:
    """Construye una respuesta HTTP 403 Forbidden con la imagen del gato Maomao de The Apothecary Diaries.
    
    Args:
        version (float, optional): Versión del protocolo HTTP a responder. Por defecto 1.1.

    Returns:
        bytes: Respuesta HTTP 403 completa en bytes lista para ser enviada al cliente.
    """
    # Preparamos la respuesta con la información de la imagen
    http_response_status: ResponseHttp = ResponseHttp(403, "Forbidden")
    version: float = 1.1
    head: dict[str, str] = {'Content-Type': 'image/png'}
    with open("MaomaoTheCat.png", "rb") as file:
        body: bytes = file.read()
    head['Content-Length'] = len(body)

    # Creamos la estructura de datos con toda la información y la convertimos a bytes
    http_struct: HttpContent = HttpContent(http_response_status, version, head, body=body)
    http_message_to_client: bytes = create_HTTP_message(http_struct)
    return http_message_to_client
    

def replace_forbidden_words(http_struct: HttpContent, json_file: str) -> HttpContent:
    """Filtra el cuerpo de un mensaje http sustituyendo palabras prohibidas según los contenidos del JSON.

    Args:
        http_struct (HttpContent): Objeto con la información de un mensaje http.
        json_file (str): Ruta al archivo JSON con el diccionario de censura ("filtro.json").

    Returns:
        (HttpContent): Objeto con la información del mensaje HTTP pero con las palabras prohíbidas sustituídas.
    """

    # Abrimos el archivo del filtro
    with open(json_file) as file:
        data = json.load(file)

    # Reemplazamos las palabras del body
    forbidden_words: list[dict[str, str]] = data["forbidden_words"]
    for pair in forbidden_words:
        for forbidden_word, new_word in pair.items():
            http_struct.body = http_struct.body.replace(bytes(forbidden_word, "UTF-8"), bytes(new_word, "UTF-8"))

    # Actualizamos el largo del body
    http_struct.head["Content-Length"] = len(http_struct.body)

    return http_struct

if __name__ == "__main__":

    # Tamaño de los buffers del Proxy
    buff_size = 64

    try:
        from dotenv import load_dotenv
        load_dotenv()  # Cargar variables de entorno desde el archivo .env
    except ImportError:
        print("(info) Librería 'python-dotenv' no instalada. Se usarán valores por defecto de server_host y server_port.")

    # Anotamos la dirección del Proxy, utilizando las variables de entorno, o los valores por defecto.

    proxy_ip: str = os.getenv('SERVER_HOST', "localhost") # Reemplace el valor por defecto "localhost" por la IP de su maquina virtual.
    proxy_port: int = int(os.getenv('SERVER_PORT', 8000))
    proxy_address: tuple = (proxy_ip, proxy_port)
    print(f"La ip del servidor es {proxy_ip}")
    print(f"El puerto del servidor es {proxy_port}")

    # Creamos el socket orientado a conexion
    print("Creando socket del servidor")
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    proxy_socket.bind(proxy_address)
    proxy_socket.listen(3)

    print("... Esperando clientes")
    # Dejamos el server prendido
    
    while True:
        new_socket, new_socket_address = proxy_socket.accept()

        # Recibimos la request del cliente. Se asume que es de tipo Request.
        http_struct_from_client: HttpContent = receive_and_parse_full_message(new_socket, buff_size)

        # Si es del tipo CONNECT, la ignoramos ya que es una petición externa que usa HTTPS
        if http_struct_from_client.type.method == "CONNECT":
            new_socket.close()
            continue

        print(f"Nueva {http_struct_from_client.type.method} request a {http_struct_from_client.type.method}")

        # Si el cliente está pidiendo la imagen para construir el HTML de la página bloqueada
        if "MaomaoTheCat.png" in http_struct_from_client.type.route:
            print("Usuario pide la imagen MaomaoTheCat.png al servidor")
            http_message: bytes = create_forbidden_image_response()
            new_socket.send(http_message)
            print("Proxy envía la imagen MaomaoTheCat.png al usuario")

        # Revisamos si es una página prohibida
        elif is_forbidden_adress(http_struct_from_client, 'filtro.json'):
            print(f"Proxy recibió una dirección prohibida: {http_struct_from_client.type.method}")
            http_message: bytes = create_forbidden_page_response()
            new_socket.send(http_message)
            print("Proxy envía el HTML de la página bloqueada")

        else:
            print("Proxy no recibió una dirección prohibida. Ahora se van a filtrar las palabras")
            # Ahora enviamos la request del cliente al servidor de destino y recibimos la respuesta
            http_struct_from_server: HttpContent = proxy_http_request(http_struct_from_client, buff_size)

            # Reemplazamos las palabras prohíbidas
            filtered_http_struct: HttpContent = replace_forbidden_words(http_struct_from_server, "filtro.json")

            # Retornamos la respuesta filtrada al cliente
            filtered_server_response: bytes = create_HTTP_message(filtered_http_struct)
            new_socket.send(filtered_server_response)

        new_socket.close()