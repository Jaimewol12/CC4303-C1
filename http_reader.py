class RequestHttp:
    def __init__(self, method: str, route: str):
        self.method: str = method
        self.route: str = route


class ResponseHttp:
    def __init__(self, code: int, status: str):
        self.code: int = code
        self.status: str = status

class HttpContent:
    def __init__(self, type: RequestHttp|ResponseHttp, version: float, header: dict[str, str], body: bytes):
        self.type: RequestHttp|ResponseHttp = type
        self.version: float = version
        self.header: dict[str, str] = header
        self.body: bytes = body       

def parse_HTTP_message(http_message: bytes) -> HttpContent:

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