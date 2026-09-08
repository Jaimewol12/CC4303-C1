
from dnslib import DNSRecord, RR, QTYPE, A
from dns_reader import DNSStruct, create_dns_message, parse_dns_message

class DNSCache:

    def __init__(self):
        self.historial: list[str] = []
        self.ips_guardadas: dict[str, str] = {}

    def obtener_top_3(self) -> list[str]:
        # Contamos la frecuencia de cada IP en el historial
        frecuencias: dict[str, int] = {} 
        for ip in self.historial:
            if ip in frecuencias:
                frecuencias[ip] += 1
            else:
                frecuencias[ip] = 1

        # Ordenamos las IPs por frecuencia y obtenemos las 3 más frecuentes
        top_3: list[str] = sorted(frecuencias, key=frecuencias.get, reverse=True)[:3]
        return top_3

    def resolver_con_cache(self, mensaje_consulta: bytes, resolver_func: function, ip_address: str) -> bytes:
        # Creamos la estructura DNS a partir del mensaje de consulta
        consulta_parsed: DNSStruct = parse_dns_message(mensaje_consulta)

        qname: str = consulta_parsed.qname

        # Agregamos la IP a la lista de historial
        self.historial.append(qname)
        if len(self.historial) > 20:
            self.historial.pop(0)  # Eliminamos la IP más antigua si excede el límite

        # Obtenemos las 3 IPs más frecuentes
        top_3: list[str] = self.obtener_top_3()

        # Limpiamos la cache de IPs que no están en el top 3
        self.ips_guardadas: dict[str, str] = {dom: ip for dom, ip in self.ips_guardadas.items() if dom in top_3}

        # Si la consulta está en la cache, devolvemos la respuesta con la IP guardada
        if qname in top_3 and qname in self.ips_guardadas:

            print(f"(debug) La consulta {qname} está en la cache. Retornando la IP guardada: {self.ips_guardadas[qname]}.")

            # Creamos una respuesta DNS con la IP guardada
            registro_respuesta = [RR(rname=consulta_parsed.qname, rtype=QTYPE.A, rdata=A(self.ips_guardadas[qname]), ttl=60)]

            # Instanciamos un nuevo DNSStruct para la respuesta
            respuesta_dns = DNSStruct(
                qname=consulta_parsed.qname,
                ANCOUNT=len(registro_respuesta),
                NSCOUNT=0,
                ARCOUNT=0,
                Answer=registro_respuesta,
                Authority=[],
                Additional=[],
                transaction_id=consulta_parsed.transaction_id
            )

            # Convertimos la estructura DNS a bytes
            
            return create_dns_message(respuesta_dns, True)

        # Si no está en la cache, llamamos a la función resolver_func para obtener la respuesta
        
        print(f"(debug) La consulta {qname} no está en la cache. Reenviando al servidor DNS recursivo.")

        respuesta_resolver: bytes = resolver_func(mensaje_consulta, ip_address)

        # Ahora guardamos la IP obtenida en la cache si es que hay una respuesta tipo A
        respuesta_parsed: DNSStruct = parse_dns_message(respuesta_resolver)
        if respuesta_parsed and respuesta_parsed.Answer:
            for rr in respuesta_parsed.Answer:
                if rr.rtype == QTYPE.A:

                    print(f"(debug) Guardando la IP {rr.rdata} para la consulta {qname} en la cache.")

                    self.ips_guardadas[qname] = str(rr.rdata)
                    break

        return respuesta_resolver