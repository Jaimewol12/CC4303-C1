class HttpContent:
    def __init__(self, type, version, header, body):
        self.type = type # El tipo puede ser o RequestHttp o ResponseHttp
        self.version = version
        self.header = header
        self.body = body
        


class RequestHttp:
    def __init__(self, method, route):
        self.method = method
        self.route = route


class ResponseHttp:
    def __init__(self, code, state):
        self.code = code
        self.state = state


def parse_HTTP_message(http_message):
        http_message_decoded = http_message.decode()
        content = http_message_decoded.splitlines()
        values_first_line = content[0].split()
        header = content[1:-1]
        body = content[-1]
        http_structured = None

        if values_first_line[0][:4] == "HTTP":
            version = float(values_first_line[0][5:8])
            Http_response = ResponseHttp(values_first_line[1], values_first_line[2])
            http_structured = HttpContent(Http_response, version, header, body)
        
        else:
             version = float(values_first_line[-1][-3:])
             Http_request = RequestHttp(values_first_line[0], values_first_line[1])
             http_structured = HttpContent(Http_request, version, header, body)

        return http_structured
    


# Esto es solo para probar, lo puedes borrar si quieres
texto = 'POST /login HTTP/1.1\r\n Host: www.ejemplo.com\r\n User-Agent: Mozilla/5.0\r\n Content-Type: application/json\r\n Content-Length: 36\r\n\r\n {"usuario":"admin","clave":"123456"}'
texto = texto.encode()

http_de_texto = parse_HTTP_message(texto)
print(http_de_texto.type.route)
