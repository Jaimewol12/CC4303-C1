# Informe parte 2: Construcción de un Resolver

Integrantes: César Barrueto, Jaime Sepúlveda.
Fecha: 07/09/2026.
Curso: Redes (CC4303-1).
Profesora: Ivana Bachmann.
Auxiliar: Julián Ferreira

Enlace de github: https://github.com/Jaimewol12/CC4303-C1.

Disclaimer uso de IA (Gemini 3.1): Se utilizó IA en el informe para mejorar la redacción y ortografía del mismo. Además de investigar de las ineficiencias del resolver para cuando no se entrega una respuesta satisfactoria en _Answer_.

### Estructura del DNS (_dns_reader.py_)

#### Funciones y métodos

1. _DNSStruct_ (clase): Estructura de datos personalizada que actúa como un contenedor para los datos importantes de un mensaje DNS. Almacenando los datos más importantes sugeridos por la actividad (qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional, ID de la transacción).

2. _parse_dns_message_: Función que recibe los bytes crudos y utiliza la librería dnslib para desencapsular en mensaje, extrayendo los datos relevantes y retorna el objeto de la clase _DNSStruct_.

3. create_dns_message: Realiza el proceso inverso, toma un objeto _DNSStruct_ y lo empaqueta nuevamente en un formato de bytes, donde se puede definir si es de tipo respuesta o no (_is_response_).

#### Decisiones de diseño

Se optó por usar la librería recomendada en la actividad _dnslib_ para la serialización de bo¿ytes, evitando la complejidad de trabajar directamente con operaciones de bits. La creación de DNSStruct fue importante para poder trabajar con objetos nativos de Python y sus funciones (como getter y setter de atributos) ya que es la principal desventaja de _dnslib_, la complejidad de trabajar con sus atributos por separado.

### Caché del DNS (_dns_cache.py_)

1. _DNSCache_ (clase): Encargada de inicializarse para poder utilizar cache y sus métodos de búsqueda a través de éste.
    
    Atributos: 
        

    a. _historial_: Acá se guarda el historial de las últimas 20 consultas hechas al resolver.


    b. _ips_guardadas_: diccionario que guarda las ips de cada dominio consultado satisfactoriamente. 

    Métodos:

    a. _obtener_top_tres_: Analiza el historial de consultas, cuenta la frecuencia de cada dominio y retorna una lista con los tres dominios más solicitados.

    b.  _resolver_con_cache_: Es el orquestador principal. Revisa si el dominio consultado está en el "top 3" frecuente y si ya tenemos su IP. Si es así, crea la respuesta al instante y la devuelve, Si no traspasa el trabajo a la función _resolver_, guardando el nuevo dominio en el historial y actualiza su dirección IP.

#### Decisiones de diseño

Se implementó un algoritmo de caché basado en su frecuencia como lo pidió la actividad. La idea de la clase es guardar en memoria RAM como 'caché' y que maneje el historial y sea capaz de responderle al cliente, así en caso negativo traspasar la responsabilidad al resolver 'clásico', de esa forma separamos la lógica del diseño.

### Servidor DNS (_resolver.py_)

#### Funciones

1. _resolver_: Es el motor de resolución recursiva e iterativa. Envía la consulta al servidor dado, parsea la respuesta implementando la siguiente lógica:

    a. Si hay una IP (tipo A) en la sección _Answer_, la retorna.

    b. Si no hay respuesta A, busca un Name Server en la sección _Authority_.

    c. Si encuentra un NS, busca su IP en la sección _Additional_ para consultarle directamente.

    d. Si el NS no trae su IP adjunta, hace una llamada recursiva a sí misma empezando desde la raíz para averiguar la IP de ese Name Server antes de continuar.

2. Bloque principal (sección _main_): Instancia el socket UDP (puerto 53), inicializa la caché y mantiene un ciclo infinito escuchando peticiones de clientes locales para delegarlas al flujo de trabajo.

#### Decisiones de diseño.

Se utilizó resolución recursiva para la función _resolver_ como se solicitaba en la actividad, la idea es que la solicitud del cliente primero sea procesado por el caché, en caso de que no pueda, el mismo caché es capaz de delegar a _resolver_ para responderlo, cada caso de encontrar la IP o Name Server está detallado en los pasos de la función, de esta forma se alcanza exhaustivamente todas las ramas y se retorna satisfactoriamente una respuesta al cliente (ya sea positiva o negativa).

### Observaciones y resultados de la actividad.

Para comenzar, la actividad pedía familiarizarse con el comando dig en bash, para eso se pedía ejecutar el siguiente comando:

```bash
 dig -p53 @1.1.1.1 example.com
```

En la sección _Answer_, la última respuesta entregada al bash, corresponde a la IP 104.20.23.154, y la segunda corresponde a la IP 172.66.147.243. A diferencia de la actividad anterior, que al ejecutar el código de la solicitud, en la sección _Answer_ primero se encuentra la IP 172.66.147.243 mientras que la segunda corresponde a 104.20.23.154.

Para la creación del socket el cual conectará el cliente y resolver, se utilizará conexión UDP, ya que en la actividad anterior se utiliza el mismo socket, además investigando, descubrimos que el 99% de las consultas se utiliza UDP, ya que es un protocolo sin conexión. No necesita el proceso de establecer un saludo (handshake) como TCP, lo que hace que las consultas sean casi instantáneas.

Luego se crea inicialmente la estructura _DNSStruct_ y la función _resolver_ para poder parsear y guardar las respuestas o consultas DNS a una estructura mucho más fácil de manejar.

El problema de esta función _resolver_ es que si no se cumple ninguna condición anterior ('a', 'b' o 'c'), entonces sólo retorna el mensaje (ignorándolo) provocando ciertas limitaciones como:

1. No maneja CNAMES (Alias), ya que muchas veces el servidor responde con un registro CNAME que apunta a otro dominio, no a una IP.

2. Ignora el IPv6, al ignorar todo lo que no sea tipo A, estás descartando los registros AAAA.

3. Ignora SOA (Start of Authority): Cuando se consulta un dominio que no existe (NXDOMAIN), el servidor responde con un registro SOA en la sección Authority para indicar un fallo oficial.

Ahora se comparará las consultas a través de dig, la IP de www.uchile.cl al resolver de Cloudflare vs el nuestro.

1. La de Cloudfare entrega el último Answer como: 200.89.76.36
2. El resolver creado entrega el último Answer como: 200.89.76.36

O sea, entregan lo mismo satisfactoriamente, este es el debug de cómo fue el procedimiento de nuestro resolver:

```
Consulta de la pagina www.uchile.cl. recibida de: ('192.168.1.105', 54865)
(debug) IP del Name Server cl2-tld.d-zone.ca. encontrada en Additional: 185.159.198.56. Reintentando consulta.
(debug) IP del Name Server ns1.uchile.cl. encontrada en Additional: 200.89.70.3. Reintentando consulta.
(debug) Respuesta tipo A encontrada para www.uchile.cl.. Retornando al cliente la IP 200.89.76.36.
IP de la pagina consultada www.uchile.cl.: 200.89.76.36 enviada a: ('192.168.1.105', 54865)
```

Una vez agregado el sistema de caché a nuestro resolver, se procede a probar si estos guardan satisfactoriamente en caché las direcciones, reduciendo el tiempo de búsqueda.

1. Consulta a eol.uchile.cl.

```
Consulta de la pagina eol.uchile.cl. recibida de: ('192.168.1.105', 58908)
(debug) La consulta eol.uchile.cl. no está en la cache. Reenviando al servidor DNS recursivo.
(debug) IP del Name Server cl2-tld.d-zone.ca. encontrada en Additional: 185.159.198.56. Reintentando consulta.
(debug) IP del Name Server ns1.uchile.cl. encontrada en Additional: 200.89.70.3. Reintentando consulta.
(debug) Respuesta tipo A encontrada para eol.uchile.cl.. Retornando al cliente la IP oeol-c.uchile.cl..
(debug) Guardando la IP 146.83.63.77 para la consulta eol.uchile.cl. en la cache.
IP de la pagina consultada eol.uchile.cl.: 146.83.63.77 enviada a: ('192.168.1.105', 58908)
```

Esta consulta devolvió 11 elementos en su sección Answer, todas respuestas de tipo A, mostrando su dirección IP, cuya caraterística principal es que esas IPs son del tipo _146.83.63.X_, siendo la última _146.83.63.77_

Luego, si vuelvo a hacer una consulta a la misma página eol.uchile.cl, como ya se había buscado, ésta se guarda en caché por lo que ahora no debería llamar a _resolver_, si no se consulta directamente al mismo caché (dando 1 respuesta en vez de 11).

```
Consulta de la pagina eol.uchile.cl. recibida de: ('192.168.1.105', 59104)
(debug) La consulta eol.uchile.cl. está en la cache. Retornando la IP guardada: 146.83.63.77.
IP de la pagina consultada eol.uchile.cl.: 146.83.63.77 enviada a: ('192.168.1.105', 59104)
```

#### Experimentos:

Si realizamos una llamada para resolver el dominio www.webofscience.com, el programa queda en un bucle infinito intentando resolver el nombre de dominio, repitiendo las mismas llamadas una y otra vez, retornando error en el bash _no servers could be reached_.

```
Consulta de la pagina www.webofscience.com. recibida de: ('192.168.1.105', 57143)
(debug) La consulta www.webofscience.com. no está en la cache. Reenviando al servidor DNS recursivo.
(debug) IP del Name Server l.gtld-servers.net. encontrada en Additional: 192.41.162.30. Reintentando consulta.
(debug) IP del Name Server ns-342.awsdns-42.com. encontrada en Additional: 205.251.193.86. Reintentando consulta.
(debug) No se encontró IP en Additional para el Name Server ns-1010.awsdns-62.net.. Resolviendo recursivamente su IP.
...
```
Esto pasa porque estos servidores no responden con una IP, sino con un Alias (registro _CNAME_), pero como el código no detecta tipos _CNAME_, busca directamente en Authority y encuentra la IP del servidor de AWS.

Una forma de solucionarlo es enseñarle al resolver que un _CNAME_ también es una respuesta válida, por lo que si encuentra ese tipo de respuesta, proceder respondiendo eso.

Ahora, si hago una consulta a www.cc4303.bachmann.cl, el siguiente mensaje es enviado satisfactoriamente, sin sección de Answer pero con sección Authority: _ns1.digitalocean.com_.

```
Consulta de la pagina www.cc4303.bachmann.cl. recibida de: ('192.168.1.105', 51722)
(debug) La consulta www.cc4303.bachmann.cl. no está en la cache. Reenviando al servidor DNS recursivo.
(debug) IP del Name Server cl2-tld.d-zone.ca. encontrada en Additional: 185.159.198.56. Reintentando consulta.
(debug) No se encontró IP en Additional para el Name Server ns1.digitalocean.com.. Resolviendo recursivamente su IP.
(debug) IP del Name Server l.gtld-servers.net. encontrada en Additional: 192.41.162.30. Reintentando consulta.
(debug) IP del Name Server kim.ns.cloudflare.com. encontrada en Additional: 108.162.192.126. Reintentando consulta.
(debug) Respuesta tipo A encontrada para ns1.digitalocean.com.. Retornando al cliente la IP 172.64.52.210.
No se encontró IP para la pagina consultada www.cc4303.bachmann.cl.. Respuesta enviada a: ('192.168.1.105', 51722)
```

Cuando se hacen llamados a _www.cc4303.bachmann_ a través de este resolver, lo que ocurre es que no retorna una dirección IP tipo A en _Answer_ (de hecho, retorna 0 respuestas), sino que retorna un elemento en la sección _Auhtority_ que es la siguiente dirección _ns1.digitalocean.com._, esto ocurrió porque nuestro servidor pregunta recursivamente la IP de _www.cc4303.bachmann_ a la página anterior, pero el Name Server respondió sin errores de conexión, pero indicando que no existe un registro tipo A configurado para ese subdominio específico.

```
Consulta de la pagina www.cc4303.bachmann.cl. recibida de: ('192.168.1.105', 51722)
(debug) La consulta www.cc4303.bachmann.cl. no está en la cache. Reenviando al servidor DNS recursivo.
(debug) IP del Name Server cl2-tld.d-zone.ca. encontrada en Additional: 185.159.198.56. Reintentando consulta.
(debug) No se encontró IP en Additional para el Name Server ns1.digitalocean.com.. Resolviendo recursivamente su IP.
(debug) IP del Name Server l.gtld-servers.net. encontrada en Additional: 192.41.162.30. Reintentando consulta.
(debug) IP del Name Server kim.ns.cloudflare.com. encontrada en Additional: 108.162.192.126. Reintentando consulta.
(debug) Respuesta tipo A encontrada para ns1.digitalocean.com.. Retornando al cliente la IP 172.64.52.210.
No se encontró IP para la pagina consultada www.cc4303.bachmann.cl.. Respuesta enviada a: ('192.168.1.105', 51722)
```

Exactamente el mismo resultado ocurre cuando se hace el llamado desde el resolver de _Cloudfare_, el cual no retorna ninguna respuesta en _Answer_, pero si la dirección _ns1.digitalocean.com._ en _Authority_.

Esto probablemente no se deba a un error del resolver ni de CloudFare, si no que debe de ser la respuesta que está configurada en el dominio, probablemente el administrador no registró un registro para el subdominio _www.cc4303_. Pero por regla del protocolo DNS, cuando un dominio existe pero el tipo de registro conultado (A) no, el servidor autoritativo responde con _Answer: 0_ y adjunta el registro en la sección Authority para indicar quién es el responsable de esa información.

Finalmente, si hago respuestas reiteradas al mismo dominio (reiniciando en cada llamada el servidor para que no se guarde en el caché), podemos observar el fenómeno de que la ruta de resolución a través del _debug_ varía aunque siempre pasemos por el servidor raíz y Name Server, termina entregando diferentes IPs al cliente.

Por ejemplo, si hago el llamado a google.com, estas son las siguientes procedimientos mostrados en el debug:

Llamada 1: 

```
Consulta de la pagina google.com. recibida de: ('192.168.1.105', 38202)
(debug) La consulta google.com. no está en la cache. Reenviando al servidor DNS recursivo.
(debug) IP del Name Server l.gtld-servers.net. encontrada en Additional: 192.41.162.30. Reintentando consulta.
(debug) IP del Name Server ns2.google.com. encontrada en Additional: 216.239.34.10. Reintentando consulta.
(debug) Respuesta tipo A encontrada para google.com.. Retornando al cliente la IP 142.250.0.101.
(debug) Guardando la IP 142.250.0.101 para la consulta google.com. en la cache.
IP de la pagina consultada google.com.: 142.250.0.101 enviada a: ('192.168.1.105', 38202)
```

Llamada 2:
```
Resolver DNS escuchando en 192.168.1.87:8000 ...
Consulta de la pagina google.com. recibida de: ('192.168.1.105', 55388)
(debug) La consulta google.com. no está en la cache. Reenviando al servidor DNS recursivo.
(debug) IP del Name Server l.gtld-servers.net. encontrada en Additional: 192.41.162.30. Reintentando consulta.
(debug) IP del Name Server ns2.google.com. encontrada en Additional: 216.239.34.10. Reintentando consulta.
(debug) Respuesta tipo A encontrada para google.com.. Retornando al cliente la IP 142.250.0.113.
(debug) Guardando la IP 142.250.0.113 para la consulta google.com. en la cache.
IP de la pagina consultada google.com.: 142.250.0.113 enviada a: ('192.168.1.105', 55388)
```

Como se puede observar en la primera llamada se encontró en _Answer_ la IP final _142.250.0.101_ mientras que en la segunda llamada, se encontró en _Answer_ la IP final _142.250.0.113_. El procedimiento es casi similar hasta la IP que resuelve el Name server _ns2.google.com_.

Esto puede deberse a que páginas como _google.com_ tiene una alta demanda de usuarios (millones de peticiones por segundo) entonces es preferible ir balanceando la carga a diferentes IPs para evitar el colapso, entonces el Name Server se encarga de ir direccionando probablemente al servidor con menos peticiones (tipo Round Robin) para aliviar la carga y evitar cuellos de botellas enormes.

#### ¿Cómo ejecutar el servidor Resolver?

Para iniciar los servidores, es necesario definir las variables de entorno que dictan la IP y el puerto de escucha. Por defecto, el sistema utilizará la IP '_localhost_' y el puerto _8000_ si no se especifican.

En su archivo .env (o modifique .env.example), debe poner lo siguiente:
```
SERVER_HOST= Acá pueden poner la IP que necesitan
SERVER_PORT= Acá pueden poner el puerto que necesitan (por defecto 8000)
```

De todas formas, si no se tiene el módulo dotenv (se puede instalar usando _pip install python-dotenv_), o no puede crear un archivo .env, se puede modificar la siguiente línea de código para poner la IP que se necesite.

```python
server_host: str = os.getenv('SERVER_HOST', 'Acá pueden poner la IP que necesiten sin utilizar la librería dotenv')
server_port: int = int(os.getenv('SERVER_PORT', Acá puede poner el puerto que necesiten sin utilizar la libería dotenv))
```

Finalmente basta dejar en ejecución el servidor Resolver ejecutando el archivo _resolver.py_.
