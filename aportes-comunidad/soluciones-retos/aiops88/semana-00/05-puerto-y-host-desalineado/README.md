# 🎯 Reto 5: El puerto fantasma y la trampa del localhost (`127.0.0.1` vs `0.0.0.0`)

* **Dificultad:** 🟢 Principiante / 🟡 Intermedio
* **Archivos:** [`Dockerfile`](./Dockerfile) y [`app.py`](./app.py)

---

## 🔍 El Escenario

Un compañero creó un microservicio en Python y lo empaquetó con Docker. Al ejecutarlo con `docker run -d -p 8080:8080`, el comando tiene éxito y `docker ps` muestra que el contenedor está en estado `Up` (corriendo).

Sin embargo, cuando intenta abrir **`http://localhost:8080`** en el navegador o ejecutar `curl http://localhost:8080`:
```text
curl: (52) Empty reply from server
# o bien:
curl: (7) Failed to connect to localhost port 8080: Connection refused
```

### 💥 ¿Por qué ocurre esto? (Las 2 causas más comunes)

1. **La trampa de `127.0.0.1` vs `0.0.0.0`:**  
   Dentro de un contenedor, `127.0.0.1` representa la interfaz de *loopback* interna de ese contenedor aislado. Si la aplicación se enlaza solo a `127.0.0.1`, **rechazará cualquier conexión que venga desde fuera del contenedor**. Para aceptar conexiones externas reenviadas por Docker, la aplicación debe escuchar en `0.0.0.0` (todas las interfaces de red del contenedor).
2. **Desalineación de puertos:**  
   Si la aplicación escucha en un puerto (ej. `5000`) pero Docker mapea otro (ej. `8080:8080`), el tráfico nunca llegará al proceso.

---

## 🎯 Tu Misión

Notas Airy 

Se encuentra un 3er bug 
Python, cuando detecta que no está escribiendo en una terminal (y un contenedor con -d no tiene terminal), acumula los print en un buffer para ahorrar escrituras. Los manda recién cuando se llena el buffer, que puede ser nunca. Lo que lo hace grave es que si la app crashea, lo que está en el buffer se pierde para siempre. Justo los logs que necesitaba para depurar, no están.
La solución es la variable PYTHONUNBUFFERED=1. Se relaciona con el reto 02, para ENV en valores por defecto que no son secretos. Este es el ejemplo.
ENV PYTHONUNBUFFERED=1

Bug 1:
                 ┌──────────── contenedor ────────────┐
 localhost:8080 ─┼─► eth0 (172.17.0.x) ──► nadie   │
   (docker -p)   │                                     │
                 │   lo   (127.0.0.1)  ──►  app:5000 │
                 │         ▲                           │
                 │         └── wget desde ADENTRO      │
                 └─────────────────────────────────────┘
127.0.0.1 (loopback): una puerta que solo se abre desde adentro del mismo contenedor. Por eso wget funcionó.
eth0: la puerta hacia afuera. Por ahí entra el tráfico del -p. Y la app no está escuchando ahí.
0.0.0.0: significa "escuchá en todas las puertas".

Bug 2: el puerto desalineado
-p  8080  :  8080       app escucha en: 5000
     │         │                          │
   host   contenedor ─────── ❌ ──────────┘

# Reto 05 · El puerto fantasma y la trampa del localhost — Solución de aiops88

## 🔍 Síntoma
`docker ps` mostraba el contenedor `Up`, pero el `curl` desde afuera fallaba.
Investigando: entré al contenedor con `docker exec` y el `wget` desde adentro sí respondía. O sea, la app estaba sana, el problema era por dónde escuchaba.
Además, `docker logs` no me traía nada, aunque la app tenía un `print` al arrancar.

## 💡 Causa: tres bugs
1. **`127.0.0.1` (loopback):** dentro de un contenedor, `127.0.0.1` es "solo este contenedor", una puerta que solo se abre desde adentro. El tráfico del `-p` entra por `eth0`, y ahí no escuchaba nadie. Mi localhost no es el localhost del contenedor.
2. **Puerto desalineado:** la app escuchaba en el `5000`, pero `-p 8080:8080` manda el tráfico al `8080` del contenedor.
3. **Bonus, logs vacíos:** Python acumula los `print` en un buffer cuando no escribe en una terminal (como en un contenedor con `-d`). Si la app crashea, esos logs se pierden.

## ✅ Solución
- `app.py`: `HOST = "0.0.0.0"` para escuchar en todas las interfaces, y el puerto por defecto en `8080`.
- `Dockerfile`: `ENV PYTHONUNBUFFERED=1` para que los logs salgan al instante, y `EXPOSE 8080` alineado con la app.

```bash
docker run -d -p 8080:8080 --name reto-puerto-app reto-puerto:v1.0
curl http://localhost:8080   # → "estado": "conectado"
```

## 🧠 Lo que aprendí
- **`Up` no es lo mismo que "funciona":** significa que el proceso vive, no que se pueda llegar al servicio.
- **`-p HOST:CONTENEDOR`:** la izquierda es mi máquina y la derecha es adentro del contenedor.
- **Arreglar el puerto sin tocar el código:** se puede con `-p 8080:5000`, o con `-e PORT=8080`, porque la app lee el puerto de una variable de entorno (el mismo principio del reto 02). Igual corregí el código, porque el valor por defecto, el `EXPOSE` y la documentación tienen que decir lo mismo. La IP no tenía arreglo desde afuera porque estaba fija en el código.
- **`ENV PYTHONUNBUFFERED=1`** es el ejemplo perfecto de cuándo sí usar `ENV`: no es secreto y es un requisito del contenedor.
- **En Kubernetes**, el `targetPort` de un Service apuntando a un puerto donde la app no escucha es el mismo error (semana 03).



