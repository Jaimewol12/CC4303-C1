import socket 
from http_reader import *
import os
from dotenv import load_dotenv
import json

def receive_client_request(connection_socket: socket, buff_size: int) -> HttpContent: 
    """Recibe la solicitud HTTP cruda enviada por el cliente y la convierte a un objeto estructurado.

    Args:
        connection_socket (socket.socket): Socket TCP activo conectado al cliente.
        buff_size (int): Tamaño del buffer de recepción en bytes.

    Returns:
        HttpContent: Objeto con la información de la petición HTTP (método, headers, body, etc.).
    """

    # Recibimos el request HTTP del cliente
    http_request: bytes = connection_socket.recv(buff_size)

    # Pasamos el request a la estrutura creada
    request_parse: HttpContent = parse_HTTP_message(http_request)

    return request_parse

def proxy_http_request(request_parsed: HttpContent, buff_size: int) -> bytes:
    """Se conecta al servidor web de destino, reenvía la petición del cliente y obtiene su respuesta.

    Args:
        request_parsed (HttpContent): Petición del cliente parseada en objeto HttpContent.
        buff_size (int): Tamaño del búfer para recibir la respuesta remota.

    Returns:
        bytes: Respuesta HTTP cruda en bytes enviada por el servidor de destino.
    """


    # Obtenemos la dirección a la que se busca conectar
    request_adress: str = request_parsed.header.get('Host').lstrip()
    ip: str = request_adress.split(":")[0]

    # Creamos un nuevo socket para la conexión al destino
    new_socket_destiny = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Establecemos conexión con el servidor
    destiny_server_adress: tuple = (ip, 80)
    new_socket_destiny.connect(destiny_server_adress)

    # Enviamos la solicitud
    request_parsed.header["X-ElQuePregunta"] = "Jaime Sepulveda"
    proxy_to_destiny_request: bytes = create_HTTP_message(request_parsed)
    new_socket_destiny.send(proxy_to_destiny_request)

    # Esperamos la respuesta
    destiny_response: bytes = new_socket_destiny.recv(buff_size)

    new_socket_destiny.close()

    return destiny_response

def is_forbidden_adress(http_request: HttpContent, json_file: str) -> bool:
    """Evalúa si el dominio solicitado por el cliente se encuentra en la lista negra del JSON.

    Args:
        http_request (HttpContent): Petición HTTP del cliente parseada.
        json_file (str): Ruta al archivo JSON de configuración ("filtro.json").

    Returns:
        bool: True si el dominio está bloqueado; False en caso contrario.
    """
    
    # Abrimos el archivo del filtro
    with open(json_file) as file:
        data = json.load(file)

        # Obtenemos del JSON la lista de dominios prohibidos
        filtered_adresses: list = data.get('blocked')

        # Si ese Host request está dentro de la lista de los dominios prohibidos, entonces retorna True
        # Si no, retorna False
        for blocked_adress in filtered_adresses:
            if blocked_adress in http_request.type.route:
                return True
        return False


def proxy_adress_filter() -> bytes:
    """Construye una respuesta HTTP 403 Forbidden personalizada con un cuerpo HTML e imagen indicando el bloqueo.

    Args:
        version (float, optional): Versión del protocolo HTTP a responder. Por defecto 1.1.

    Returns:
        (bytes): Respuesta HTTP 403 completa en bytes lista para ser enviada al cliente.
    """

    # Creamos la respuesta HTTP

    response_HTTP_server: ResponseHttp = ResponseHttp(403, "Forbidden")
    version: float = 1.1
    header: dict[str, str] = {'Content-Type': 'text/html; charset=UTF-8'}
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
    header['Content-Length'] = len(body)

    http_response_struct: HttpContent = HttpContent(response_HTTP_server, version, header, body=body)

    http_response_encoded: bytes = create_HTTP_message(http_response_struct)

    return http_response_encoded

def create_forbidden_image_response() -> bytes:

    response_HTTP_server: ResponseHttp = ResponseHttp(403, "Forbidden")
    version: float = 1.1
    header: dict[str, str] = {'Content-Type': 'image/png'}

    with open("MaomaoTheCat.png", "rb") as file:
        body: bytes = file.read()

    header['Content-Length'] = len(body)

    http_response_struct: HttpContent = HttpContent(response_HTTP_server, version, header, body=body)
    http_response_encoded: bytes = create_HTTP_message(http_response_struct)
    return http_response_encoded
    

def proxy_content_filter(server_response: bytes, json_file: str) -> bytes:
    """Filtra el cuerpo de la respuesta HTTP sustituyendo palabras prohibidas según el mapa de reemplazos del JSON.

    Args:
        destiny_response (bytes): Respuesta cruda obtenida del servidor web remoto.
        json_file (str): Ruta al archivo JSON con el diccionario de censura ("filtro.json").

    Returns:
        (bytes): Respuesta HTTP modificada y recompilada en bytes para entregar al cliente.
    """

    http_server_response: HttpContent = parse_HTTP_message(server_response)

    # Abrimos el archivo del filtro
    with open(json_file) as file:
        data = json.load(file)

    forbidden_words: list[dict[str, str]] = data["forbidden_words"]

    for dic in forbidden_words:
        for forbidden_word, new_word in dic.items():
            http_server_response.body = http_server_response.body.replace(bytes(forbidden_word, "UTF-8"), bytes(new_word, "UTF-8"))

    http_server_response.header["Content-Length"] = len(http_server_response.body)

    filtered_server_response: bytes = create_HTTP_message(http_server_response)

    return filtered_server_response

if __name__ == "__main__":

    # Defino el tamaño de buffer 
    buff_size = 1024

    # Creamos el socket no orientado a conexion
    server_host: str = os.getenv('SERVER_HOST', 'localhost')
    server_port: int = int(os.getenv('SERVER_PORT', 8000))

    print(f"El host del servidor es {server_host}")
    print(f"El puerto del servidor es {server_port}")

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
        http_client_request: HttpContent = receive_client_request(new_socket, buff_size)

        if http_client_request.type.method == "CONNECT":
            new_socket.close()
            continue

        # Revisamos que no sea una página prohibida
        elif is_forbidden_adress(http_client_request, 'filtro.json'):
            print(f"Nueva {http_client_request.type.method} Request de: {http_client_request.header.get('X-ElQuePregunta')} a {http_client_request.header.get('Host')}")
            print("Proxy encontró dominio prohibido")

            http_response_encoded = proxy_adress_filter()
            new_socket.send(http_response_encoded)

            max_attempts_to_request_the_image: int = 10
            i = 0
            while i < max_attempts_to_request_the_image:
                http_client_request = receive_client_request(new_socket, buff_size)

                print(http_client_request.type.route)
        
                if "MaomaoTheCat.png" in http_client_request.type.route:

                    print("Usuario pide la imagen MaomaoTheCat.png al servidor")
                    http_response_encoded = create_forbidden_image_response()
                    new_socket.send(http_response_encoded)
                    print("Proxy envía la imagen MaomaoTheCat.png al usuario")
                    break

                i += 1

        else:
            print(f"Nueva {http_client_request.type.method} Request de: {http_client_request.header.get('X-ElQuePregunta')} a {http_client_request.header.get('Host')}")
            print("Proxy no encontró dominio prohibido, pero hay que filtrar las palabras")
            # Ahora pasamos su request al Host (dirección de destino)
            destiny_response: bytes = proxy_http_request(http_client_request, buff_size)

            # Acá se debe filtrar el contenido según el proxy usando proxy_content_filter()
            
            # Retornamos el response filtrado al cliente
            filtered_server_response = proxy_content_filter(destiny_response, "filtro.json")
            new_socket.send(filtered_server_response)

        new_socket.close()
            





