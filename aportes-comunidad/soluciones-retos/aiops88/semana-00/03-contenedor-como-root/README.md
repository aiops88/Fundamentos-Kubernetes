# 🎯 Reto 3: El contenedor vulnerable que corre como root

* **Dificultad:** 🟡 Intermedio
* **Archivo:** [`Dockerfile`](./Dockerfile)

---

## 🔍 El Escenario

La empresa implementó una auditoría estricta de seguridad: **ningún contenedor en producción debe ejecutarse con privilegios de superusuario (`root`)**, ya que si la aplicación sufre una vulnerabilidad de ejecución remota de código, el atacante tendría control absoluto sobre los procesos.

Un compañero empaquetó una API en Python dentro de un contenedor, pero olvidó configurar un usuario sin privilegios.

### 💥 Síntomas

El contenedor funcionaba perfecto, no se caía ni daba error. El problema era de seguridad: con `docker run --rm reto-root id` salía `uid=0(root)`.
Para probar qué podía hacer, escribí un archivo en `/etc` y funcionó: como root su alcance es a cualquier lugar dentro del contenedor.

1. Construye la imagen actual:
   ```bash
   docker build -t reto-root:v1.0 semana-00-fundamentos-docker/2.reto-roto/03-contenedor-como-root
   ```
2. Inspecciona qué usuario ejecuta el proceso:
   ```bash
   docker run --rm reto-root:v1.0 whoami
   ```
   *Salida:* `root` ❌ (El proceso corre como UID 0).

3. Al probar con `curl`:
   ```bash
   docker run -d -p 8080:8080 --name test-root reto-root:v1.0
   curl http://localhost:8080
   ```
   *Salida:* `"alerta": "⚠️ ALERTA: Este contenedor está corriendo como superusuario (root)!"`

---

## 🎯 Tu Misión

Notas de Airy: 

Atacante explota tu app
        │
        ├─ app corre como ROOT  ──► escapa ──► root del HOST 💀
        │
        └─ app corre como 10001 ──► escapa ──► usuario sin permisos

## Causa

El Dockerfile no definía ningún usuario, entonces Docker corre todo como root por defecto.
El root del contenedor es el mismo UID 0 que el root del host. Lo que lo frena son las paredes de Docker (namespaces, capabilities), pero si alguna tiene un agujero (vulnerabilidad del kernel, `docker.sock` montado, `--privileged`), el atacante sale siendo root del servidor.
En Kubernetes con políticas seguras (`runAsNonRoot: true`) este contenedor ni siquiera arrancaría: `CreateContainerConfigError`.

## Solución
Me traje el patrón del reto 2, porque ese Dockerfile ya corría como usuario no privilegiado:

```dockerfile
RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup
COPY --chown=appuser:appgroup app.py .
USER appuser
```

## Lo que aprendí
- **¿Por qué UID 10001?** El kernel no conoce nombres, solo números. Del 0 al 999 son cuentas del sistema y el 1000 suele ser el primer usuario humano del host. Si el contenedor corre como 1000 y escapa o monta una carpeta del host, actúa como ese usuario real. Con 10001 lo más probable es que no coincida con nadie.
- **El orden importa:** si pongo `USER appuser` antes del `RUN adduser`, el build falla con `unable to find user appuser`, porque intenta correr como un usuario que todavía no existe. Además, crear usuarios requiere root. Primero va todo lo que necesita root y al final se baja de privilegio con `USER`.
- **Defensa en profundidad:** no confiar en una sola pared. Si la app corre como usuario normal y alguien escapa, sale sin poder.

-----------------------
## 🧪 Verificación
- `docker run --rm reto-root id` → `uid=10001`
- Intentar escribir en `/etc` → `Permission denied`
      
      1. Modifica [`Dockerfile`](./Dockerfile) para aplicar el principio de menor privilegio:
   * Crea un grupo y un usuario no privilegiado en Alpine (por ejemplo `appuser` con UID y GID `10001`):
     ```dockerfile
     RUN addgroup -g 10001 -S appgroup && \
         adduser -u 10001 -S appuser -G appgroup
     ```
   * Asigna la propiedad del archivo copiado al nuevo usuario usando:
     ```dockerfile
     COPY --chown=appuser:appgroup app.py .
     ```
   * Declara la instrucción `USER` antes de `CMD`:
     ```dockerfile
     USER appuser
     ```
2. Vuelve a compilar la imagen:
   ```bash
   docker build -t reto-root:v1.0 semana-00-fundamentos-docker/2.reto-roto/03-contenedor-como-root
   ```
3. Valida que el usuario sea el correcto:
   ```bash
   docker run --rm reto-root:v1.0 whoami
   ```
   *Salida esperada:* `appuser` (o UID 10001) ✅.

4. Corre el contenedor y valida la respuesta HTTP:
   ```bash
   docker run -d -p 8080:8080 --name test-root-ok reto-root:v1.0
   curl http://localhost:8080
   ```
   *Salida esperada:* `"es_root": false` y `"mensaje": "✅ EXCELENTE: El contenedor corre con un usuario sin privilegios."`

5. Limpia los contenedores de prueba:
   ```bash
   docker rm -f test-root test-root-ok
   ```

