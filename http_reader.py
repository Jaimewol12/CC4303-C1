class RequestHttp:
    """Representa la línea de solicitud (Start-Line) de una petición HTTP.

    Attributes:
        method (str): Método HTTP utilizado en la petición (e.g., 'GET', 'POST').
        route (str): Ruta o URI del recurso solicitado en el servidor (e.g., '/index.html').
    """

    def __init__(self, method: str, route: str):
        """Inicializa los atributos de la solicitud HTTP.

        Args:
            method (str): Método de la petición HTTP.
            route (str): Ruta del recurso solicitado.
        """
        self.method: str = method
        self.route: str = route


class ResponseHttp:
    """Representa la línea de estado (Status-Line) de una respuesta HTTP.

    Attributes:
        code (int): Código de estado numérico de la respuesta (e.g., 200, 404, 403).
        status (str): Texto o razón descriptiva del estado (e.g., 'OK', 'Forbidden').
    """

    def __init__(self, code: int, status: str):
        """Inicializa los atributos de la respuesta HTTP.

        Args:
            code (int): Código de estado HTTP.
            status (str): Mensaje descriptivo del estado.
        """
        self.code: int = code
        self.status: str = status

class HttpContent:
    """Estructura contenedora que abstrae un mensaje HTTP completo (Request o Response).

    Attributes:
        type (Union[RequestHttp, ResponseHttp]): Instancia que define si es una petición o respuesta.
        version (float): Versión del protocolo HTTP utilizada (e.g., 1.1).
        header (dict[str, str]): Diccionario clave-valor con los encabezados HTTP.
        body (Union[bytes, str]): Carga útil o cuerpo del mensaje HTTP.
    """

    def __init__(self, type: RequestHttp|ResponseHttp, version: float, header: dict[str, str], body: bytes):
        """Inicializa la estructura global del mensaje HTTP.

        Args:
            type (Union[RequestHttp, ResponseHttp]): Objeto RequestHttp o ResponseHttp.
            version (float): Versión del protocolo HTTP.
            header (dict[str, str]): Diccionario con las cabeceras HTTP.
            body (Union[bytes, str]): Contenido o cuerpo del mensaje.
        """
        self.type: RequestHttp|ResponseHttp = type
        self.version: float = version
        self.header: dict[str, str] = header
        self.body: bytes = body       

def parse_HTTP_message(http_message: bytes) -> HttpContent:
    """Analiza un flujo de bytes de un mensaje HTTP crudo y lo transforma en un objeto HttpContent.

    Args:
        http_message (bytes): Cadena binaria cruda del mensaje HTTP recibida desde un socket.

    Returns:
        HttpContent: Instancia estructurada con la información procesada del mensaje.
    """

    head_body_separator_idx: int = http_message.find(b"\r\n\r\n")

    header_section: str = http_message[:head_body_separator_idx].decode()
    body: bytes = http_message[head_body_separator_idx + 4:]

    content: list[str] = header_section.splitlines()
    values_first_line: list[str] = content[0].split()
    header: dict[str, str] = {}

    for line in content[1:]:
        idx: int = line.find(":")
        key: str = line[:idx]
        value: str = line[idx + 1:].removesuffix("\r\n")
        header[key] = value

    # Caso Response
    if values_first_line[0][:4] == "HTTP":
        version: float = float(values_first_line[0][5:])
        code: int = values_first_line[1]
        status: str = values_first_line[2]
        http_response = ResponseHttp(code, status)
        http_structured = HttpContent(http_response, version, header, body)

    # Caso Request
    else:
        version: float = float(values_first_line[-1][5:])
        method: str = values_first_line[0]
        route: str = values_first_line[1]
        http_request = RequestHttp(method, route)
        http_structured = HttpContent(http_request, version, header, body)

    return http_structured
    
def create_HTTP_message(http_structure: HttpContent) -> bytes:
    """Serializa un objeto HttpContent a su representación binaria lista para ser transmitida por un socket TCP.

    Args:
        http_structure (HttpContent): Objeto estructurado que representa la solicitud o respuesta.

    Returns:
        bytes: Secuencia binaria formateada según el estándar del protocolo HTTP.
    """
    if isinstance(http_structure.type, RequestHttp):
        mensaje = f"{http_structure.type.method} {http_structure.type.route} HTTP/{http_structure.version}\r\n"

    elif isinstance(http_structure.type, ResponseHttp):
        mensaje = f"HTTP/{http_structure.version} {http_structure.type.code} {http_structure.type.status}\r\n"

    for key, value in http_structure.header.items():
        mensaje += f"{key}:{value}\r\n"
    mensaje += f"\r\n"
    mensaje_codificado = mensaje.encode() + http_structure.body

    return mensaje_codificado

# Esto es solo para probar, lo puedes borrar si quieres
texto = 'GET /login HTTP/1.1\r\nHost: www.ejemplo.com\r\nUser-Agent: Mozilla/5.0\r\nContent-Type:application/json\r\nContent-Length: 36\r\n\r\n{"usuario":"admin","clave":"123456"}'
texto = texto.encode()

texto_response = "HTTP/1.1 200 OK\r\nContent-Type:test/html;charset=UTF-8\r\nContent-Length:155\r\n\r\n{'Hola que tal'}"
texto_response = texto_response.encode()

http_de_texto = parse_HTTP_message(texto)
#print(http_de_texto.type.method)
#print(create_HTTP_message(http_de_texto))

http_de_texto_response = parse_HTTP_message(texto_response)
#print(create_HTTP_message(http_de_texto_response))

#print(texto_response.decode())
#print(texto_response == create_HTTP_message(http_de_texto_response))