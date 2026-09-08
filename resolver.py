import socket
from dnslib.dns import QTYPE
import os
from dns_reader import *
from dns_cache import *


def resolver(mensaje_consulta: bytes, ip_addr: str) -> bytes:
    """Función que recibe un mensaje de consulta DNS y lo reenvía a un servidor DNS recursivo.

    Args:
        mensaje_consulta (bytes): Mensaje de consulta DNS en formato binario.
        ip_addr (str): Dirección IP del servidor DNS recursivo.

    Returns:
        bytes: Respuesta del servidor DNS recursivo en formato binario.
    """
    while True:
        # Creamos el socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Definimos el puerto estándar para consultas DNS
        port: int = 53
        try:
            # A. Enviamos la consulta al servidor DNS recursivo
            sock.sendto(mensaje_consulta, (ip_addr, port))
            # Esperamos la respuesta del servidor
            data, _ = sock.recvfrom(4096)
        finally:
            sock.close()

        # Parseamos la respuesta para obtener el qname y los contadores
        parsed: DNSStruct = parse_dns_message(data)

        if not parsed:
            print("Error al parsear la respuesta DNS.")
            return data  # Retornamos la respuesta original si hubo un error al parsear
        
        # B. Revisar si hay respuesta tipo A en la seccion Answer
        # Buscamos iterando los registros de la lista Answer
        tiene_respuesta_A: bool = any(rr.rtype == QTYPE.A for rr in parsed.Answer)

        # Si encontramos un registro tipo A, retornamos la respuesta al cliente
        if tiene_respuesta_A:
            # debug
            print(f"(debug) Respuesta tipo A encontrada para {parsed.qname}. Retornando al cliente la IP {parsed.Answer[0].rdata}.")
            return data

        # C. Si no hay respuesta tipo A, revisamos la seccion Authority (Name Servers)
        ns_records: list = [rr for rr in parsed.Authority if rr.rtype == QTYPE.NS]

        if ns_records:
            # C.1. Revisamos si hay registros de tipo A en la seccion Additional para los NS encontrados
            ip_adicional: str | None = None
            for i in parsed.Additional:
                if i.rtype == QTYPE.A:
                    ip_adicional = str(i.rdata) # Obtenemos la IP
                    break

            if ip_adicional:
                # Se encontró una IP, actualizamos la variable y el bucle vuelve a empezar -> (A)
                ip_addr = ip_adicional

                # debug
                print(f"(debug) IP del Name Server {ns_records[0].rdata} encontrada en Additional: {ip_adicional}. Reintentando consulta.")
                continue

            # C.2. No hay IP en Additional. Debemos resolver el Name Server recursivamente.
            else:
                ns_name: str = str(ns_records[0].rdata)  # Tomamos el primer NS

                # Construimos la consulta DNS mediante DNSStruct y create_dns_message
                struct_ns = DNSStruct(
                    qname=ns_name,
                    ANCOUNT=0,
                    NSCOUNT=0,
                    ARCOUNT=0,
                    Answer=[],
                    Authority=[],
                    Additional=[]
                )
                query_ns: bytes = create_dns_message(struct_ns, False)

                # Llamada recursiva: Empezamos desde la raiz para buscar la IP del NS

                # debug
                print(f"(debug) No se encontró IP en Additional para el Name Server {ns_name}. Resolviendo recursivamente su IP.")
                respuesta_ns_bytes: bytes = resolver(query_ns, root_ip)
                parsed_ns: DNSStruct = parse_dns_message(respuesta_ns_bytes)

                # Buscamos la IP que nos devolvio nuestra recursion
                ip_resuelta: str | None = None
                if parsed_ns:
                    for rr in parsed_ns.Answer:
                        if rr.rtype == QTYPE.A:
                            ip_resuelta = str(rr.rdata)
                            break
                            
                if ip_resuelta:
                    # Si logramos resolver el NS, actualizamos la IP y seguimos el bucle
                    ip_addr = ip_resuelta
                    continue
                else:
                    # Si no pudimos resolver el NS por alguna razon, retornamos los datos
                    # debug
                    print(f"(debug) No se pudo resolver la IP para el Name Server {ns_name}.")
                    return data
                
        # D. Si recibe otro tipo de respuesta, se ignora
        # Si llega a este punto (no hay A en Answer, no hay NS en Authority), rompemos el ciclo
        return data




if __name__ == "__main__":

    # Defino el tamaño del buffer
    buff_size: int = 1024

    # Defino la IP del servidor raíz (root server) para iniciar la resolución recursiva
    root_ip = '198.41.0.4'

    # Creamos el DNSCache para manejar la cache de IPs
    dns_cache = DNSCache()

    # Creamos el socket no orientado a conexión (UDP)

    try:
        from dotenv import load_dotenv
        load_dotenv()  # Cargar variables de entorno desde el archivo .env
    except ImportError:
        print("(info) Librería 'python-dotenv' no instalada. Se usarán valores por defecto de server_host y server_port.")

    server_host: str = os.getenv('SERVER_HOST', 'localhost')
    server_port: int = int(os.getenv('SERVER_PORT', 8000))

    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dns_socket.bind((server_host, server_port))

    print(f"Resolver DNS escuchando en {server_host}:{server_port} ...")

    # Dejamos abierto el server
    while True:
        # Esperamos una pregunta del cliente:
        data, client_address = dns_socket.recvfrom(buff_size)
        query_name = parse_dns_message(data).qname
        
        print(f"Consulta de la pagina {query_name} recibida de: {client_address}")

        # Reenviamos la consulta al servidor DNS recursivo
        response_data: bytes = dns_cache.resolver_con_cache(data, resolver, root_ip)

        # Enviamos la respuesta de vuelta al cliente
        dns_socket.sendto(response_data, client_address)

        # debug
        parsed_response: DNSStruct = parse_dns_message(response_data)
        tiene_respuesta_A: bool = any(rr.rtype == QTYPE.A for rr in parsed_response.Answer)
        if tiene_respuesta_A:
            ip_final = None
            for rr in parsed_response.Answer:
                if rr.rtype == QTYPE.A:
                    ip_final = str(rr.rdata)
                    break
            print(f"IP de la pagina consultada {query_name}: {ip_final} enviada a: {client_address}")
        else:
            print(f"No se encontró IP para la pagina consultada {query_name}. Respuesta enviada a: {client_address}")




