# Reto 02 · Variable de entorno faltante — Solución de aiops88 - Airy Nieves

## Síntoma
¿Qué pasaba al correr el contenedor? ¿Qué código de salida daba?
¿Qué decían los logs?

Al correr el contenedor no aparecía en `docker ps`. Con `docker ps -a` salía `Exited (1)`, y en los logs salía el error:
`💥 ERROR FATAL: La variable de entorno obligatoria 'APP_SECRET_TOKEN' no fue proporcionada.`

## Causa
¿Por qué el contenedor no tenía la variable? (pista: aislamiento del host)
¿Por qué la app se muere a propósito? ¿Qué es fail-fast y por qué es buen diseño?
¿Qué diferencia hay entre este Exited (1) y el Exited (0) del reto 01?

El contenedor no hereda las variables de entorno de mi máquina, está aislado, así que si una variable no se mete explícitamente, adentro no existe.
La app se muere a propósito con `sys.exit(1)` cuando no encuentra el token. Eso es fail-fast y es buen diseño: es mejor que falle al arrancar con un error claro, que arrancar sin token y fallar después en producción.
A diferencia del reto 01, donde `Exited (0)` significaba que el proceso terminó "bien" sin error, aquí `Exited (1)` sí es un error, y los logs lo dicen.

## Solución
Inyecté la variable al correr el contenedor con `-e`:
El comando exacto que usé: docker run -d -p 8080:8080 -e APP_SECRET_TOKEN="token-local-dev" --name mi-api-02 reto-docker-02

## ¿Por qué -e y no ENV?
# ¿Qué pasa con un secreto puesto con ENV? (capas, docker inspect, rotación)
# ¿Por qué "imagen privada" no alcanza?
# ¿Cuándo SÍ tiene sentido ENV? ejemplo

Usé `-e` al correr porque así el secreto no queda en la imagen. Si lo pongo con `ENV` en el Dockerfile queda horneado en las capas, se puede ver con `docker inspect`, y para rotarlo hay que reconstruir la imagen.
Que la imagen sea privada no alcanza: privada no es lo mismo que secreta, cualquiera con permiso de pull puede ver las variables.
`ENV` sí tiene sentido para valores por defecto que no son secretos, por ejemplo `PORT=8080` o `LOG_LEVEL=info`.

## Bonus: filtraciones que encontré y corregí
# Fuga 1: ¿dónde aparecía el token en la respuesta HTTP y cómo lo arreglaste?
# Fuga 2: ¿dónde aparecía en los logs y cómo lo arreglaste?
# ¿Por qué un secreto en los logs es peor que en la respuesta?
# ¿Por qué sacaste el puerto de la respuesta?

- **Fuga 1, respuesta HTTP:** la app devolvía el token impreso en el JSON. Lo cambié a `"token_configurado": true`, para que diga si existe pero no cuál es.
- **Fuga 2, logs:** el log de inicio (línea 35 del `app.py`) imprimía el token. Lo cambié para que solo confirme que cargó, sin mostrarlo.
- **¿Por qué los logs son peores?** Porque los logs no solo los ve quien hace la app: se guardan, se replican y se mandan a terceros (CloudWatch, Datadog, etc.). Si hackean al vendor que los guarda o filtra, también se filtra el secreto, y no se puede borrar de todos lados.
- **El puerto:** no me parece tan inseguro, pero tampoco es seguro mostrarlo sin más, porque no es necesario para cualquiera. Lo saqué de la respuesta (mínimo privilegio aplicado a la información). En el log sí lo dejé, porque le sirve al equipo que opera la app.


## 🚀 Próximo nivel
# -e tampoco es lo ideal en producción. ¿Qué se usa? (adelanto de la semana 04)
`-e` tampoco es lo ideal en producción, porque `docker inspect` del contenedor también muestra las variables. En producción los secretos vienen de un gestor como AWS Secrets Manager, Vault o Kubernetes Secrets (semana 04).