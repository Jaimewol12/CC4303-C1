# CC4303-C1

## Los cambios

Hola Jaime, estos son los cambios que hice

1. Creé la función receive_client_request que toma el HTTP request del cliente crudo y lo parsea a la estructura que creamos, Retorna un HttpContent con toda la info del request.

2. Creé la función proxy_http_request que toma la request del cliente parseada y obtiene el Host final (el destiny) al cual quiere acceder, por ejemplo 'Host: www.dcc.uchile.cl', entonces el proxy crea un nuevo socket y hace una solicitud http para solicitar la info de la página web. Retorna el HTTP Response del servidor en bytes

3. Creé la función is_forbidden_adress que toma el Request parseado del cliente y el string del nombre del json file, en este caso "filtro.json", lo que hace es que obtiene el string del host de los Headers content, y lo va comparando con la lista de dominios prohibidos del JSON de la profe, si coincide, retorna True, si no Retorna False.

La idea es que el diagrama sea el siguiente (como ejemplo):

1. Cliente: Manda Request HTTP a algun Host: example.com.

2. Proxy: Interviene la solicitud del cliente.

3. El proxy revisa si dicha solicitud es prohibida segun el JSON: Si example.com pertenece a los dominios prohibidos.

4. En caso positivo, retornar un HTTP Response con código 403 y una fotito (como explica la actividad el EOL). 

5. En caso negativo, entonces el proxy hace un request HTTP al Host (a example.com), y le llega una respuesta.

6. Antes de mandar la respuesta al cliente, el Porxy se encarga de filtrar y intercambiar todas las palabras prohibidas encontradas en 'filtro.json'.

7. Una vez filtrado y transformado a un formato HTTP en bytes, el proxy está listo para mandar el HTTP Response filtrado al usuario y listo.

## Lo que debes hacer

Tienes que crear las funciones de los flitros y terminar el diagrama del server del proy

1. Completar proxy_adress_filter, la cual debería crear un Response HTTP que diga error 403 y en el body que incluya una imagen cute jeje (nada de pomnis) y que retorne ese mensaje al cliente (ahí te puedes guiar con el EOL).

2. Completar proxy_content_filter, que toma como parámetros el HTTP Response del Host del destino (puede ser crudo (en bytes) o ya parseado como quieras, ahí ves) y el string del archivo json "filtro.json". La idea es que tome el body del Response, y que vaya filtarando cada palabra prohibida y reemplazandola por la que está en el JSON, así creas el body "limpio" que es el que le va a retornar al cliente, finalmente retornas el Response HTTP que se le enviará al cliente.

