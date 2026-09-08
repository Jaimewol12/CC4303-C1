from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

class DNSStruct:

    def __init__(self, qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional, transaction_id=0):
        self.qname: str= qname
        self.ANCOUNT: int = ANCOUNT
        self.NSCOUNT: int = NSCOUNT
        self.ARCOUNT: int = ARCOUNT
        self.Answer: list = Answer
        self.Authority: list = Authority
        self.Additional: list = Additional
        self.transaction_id: int = transaction_id  # Se puede agregar si es necesario


def parse_dns_message(data) -> DNSStruct:
    try:
        dns_record: DNSRecord = DNSRecord.parse(data)
        
        # Qname de la primera pregunta
        qname: str = str(dns_record.q.qname) if dns_record.questions else ""
        
        # Los contadores están en el 'header'
        ANCOUNT: int = dns_record.header.a
        NSCOUNT: int = dns_record.header.auth
        ARCOUNT: int = dns_record.header.ar
        
        # Las secciones están en estas propiedades específicas
        Answer: list = dns_record.rr        # 'rr' = Resource Records (Answer)
        Authority: list = dns_record.auth   # 'auth' = Authority
        Additional: list = dns_record.ar    # 'ar' = Additional

        # Extraemos el ID
        transaction_id: int = dns_record.header.id

        return DNSStruct(qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional, transaction_id)
    except Exception as e:
        print(f"Error parsing DNS response: {e}")
        return None

def create_dns_message(dns_structure: DNSStruct, is_response: bool) -> bytes:
    try:
        # Creamos el registro base con la pregunta del cliente
        dns_record = DNSRecord.question(dns_structure.qname)

        dns_record.header.id = dns_structure.transaction_id
        dns_record.header.qr = 1 if is_response else 0  # 1 para respuesta, 0 para consulta

        # Asignamos los registros a las secciones correspondientes en dnslib
        dns_record.rr = dns_structure.Answer
        dns_record.auth = dns_structure.Authority
        dns_record.ar = dns_structure.Additional

        # Convertimos todo a bytes binarios
        return dns_record.pack()
    except Exception as e:
        print(f"Error creating DNS message: {e}")
        return b""