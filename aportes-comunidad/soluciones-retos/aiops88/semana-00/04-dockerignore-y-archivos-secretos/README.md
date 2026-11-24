# 🎯 Reto 4: La fuga de secretos y contexto pesado por falta de `.dockerignore`

* **Dificultad:** 🟢 Principiante / 🟡 Intermedio
* **Archivos:** [`Dockerfile`](./Dockerfile) y [`.env`](./.env)

---

## 🔍 El Escenario

Un desarrollador del equipo usó `COPY . .` en el `Dockerfile` pero olvidó crear el archivo `.dockerignore`. En su máquina local tenía un archivo `.env` con credenciales de base de datos y llaves de acceso de prueba.

Al publicar la imagen a un registro público de contenedores, ¡cualquiera con acceso a la imagen puede inspeccionar sus capas y robar las contraseñas!

### 💥 Síntoma

1. Construye la imagen actual:
   ```bash
   docker build -t reto-leak:v1.0 semana-00-fundamentos-docker/2.reto-roto/04-dockerignore-y-archivos-secretos
   ```
2. Inspecciona el interior del contenedor:
   ```bash
   docker run --rm reto-leak:v1.0 cat .env
   ```
   *Salida:* ¡Podrás ver todas las contraseñas en texto plano! 😱


---
## Notas de Airy:
COPY  .              .
      │              │
      origen:        destino:
      el BUILD       el WORKDIR
      CONTEXT        (/app)

El segundo . : el directorio actual adentro de la imagen. Como antes hay un WORKDIR /app, es /app.
El primer . : el build context.

Local ──► [.dockerignore] ──► build context ──► [COPY explícito] ──► imagen (Defensa en Profundidad)
               pared 1:                              pared 2:
               "esto NI SALE                         "de lo que llegó,
               de mi máquina"                        solo entra ESTO"

Pared	         Estrategia	            Cómo piensa
.dockerignore	Lista negra (denylist)	"Todo entra, menos esto"
COPY app.py .	Lista blanca (allowlist)	"Solo entra esto"

Lista blanca para que sea seguro, y la negra como red de contención (y para que el contexto sea más liviano y el build más rápido).

Sintoma!
Al construir la imagen y correr `docker run --rm reto-leak:v1.0 ls -la`, salía el `.env` con las claves, y también el Dockerfile y el README.
Con `cat .env` se podía leer todo: la URL de la base de datos de producción con usuario y contraseña, la llave JWT y las credenciales de AWS. Eran de ejemplo, pero en la vida real con eso se tienen las llaves de todo.

## Solución: dos paredes (defensa en profundidad)
1. **`.dockerignore` (lista negra):** excluye `.env` y sus variantes, logs, temporales, `.git/` y archivos que la app no necesita. Esto ni sale de mi máquina.
2. **`COPY` explícito (lista blanca):** `COPY --chown=appuser:appgroup app.py .`. Solo entra lo que la app necesita.

La lista blanca es más segura, porque si mañana alguien agrega un archivo nuevo con secretos, la lista negra no lo conoce, pero la blanca ni se entera de que existe.
El `.dockerignore` igual suma: hace el contexto más liviano y el build más rápido, y es red de contención si alguien vuelve a poner un `COPY . .`.

## Lo que aprendí
- `.gitignore` y `.dockerignore` son independientes: uno protege el repo y el otro la imagen. Este repo ya tenía `.env` en el `.gitignore`, por eso no se subió a GitHub, pero Docker no lee el `.gitignore` y lo metía igual en la imagen.
- `.git/` también va al `.dockerignore`, porque un secreto borrado en un commit sigue en el historial.
- `**/.env` atrapa el `.env` en cualquier subcarpeta, no solo en la raíz.

## Verificación
- `docker run --rm reto-leak:v1.0 ls -la` → solo `app.py`
- `docker run --rm reto-leak:v1.0 cat .env` → `No such file or directory`

---

## 🎯 Tu Misión

1. Crea el archivo `.dockerignore` en `semana-00-fundamentos-docker/2.reto-roto/04-dockerignore-y-archivos-secretos/` para excluir:
   * `.env`
   * `*.log`
   * `*.tmp`
   * `.git/`
   * `README.md`
2. Modifica el [`Dockerfile`](./Dockerfile) para copiar de manera explícita solo el archivo `app.py` asignando la propiedad con `--chown=appuser:appgroup`.
3. Vuelve a construir la imagen:
   ```bash
   docker build -t reto-leak:v1.0 semana-00-fundamentos-docker/2.reto-roto/04-dockerignore-y-archivos-secretos
   ```
4. Comprueba que el archivo ya no exista dentro de la imagen:
   ```bash
   docker run --rm reto-leak:v1.0 ls -la
   ```
   Y al probar `docker run --rm reto-leak:v1.0 cat .env`, Docker debe responder:
   `cat: can't open '.env': No such file or directory` ✅
